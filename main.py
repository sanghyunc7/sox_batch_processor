import os
import sys
import subprocess
import multiprocessing
import logging
from datetime import datetime
from collections import Counter


# root directory for music
IN_DIR = sys.argv[1]
OUT_DIR = "/mnt/f/HiRes"
EXCLUDE_DIRS = ["__MACOSX"]
INPUT_FORMATS = "8svx aif aifc aiff aiffc al amb au avr cdda cdr cvs cvsd cvu dat dvms f32 f4 f64 f8 flac fssd gsrt hcom htk ima ircam la lpc lpc10 lu maud mp2 mp3 nist prc raw s1 s16 s2 s24 s3 s32 s4 s8 sb sf sl sln smp snd sndr sndt sou sox sph sw txw u1 u16 u2 u24 u3 u32 u4 u8 ub ul uw vms voc vox wav wavpcm wve xa".split()


# manager = multiprocessing.Manager()
history_file_lock = multiprocessing.Lock()
history_file = os.path.join(OUT_DIR, "history.txt")
history_readonly = set() # should be used as read-only unless during init


logger_info_lock = multiprocessing.Lock()
logger_error_lock = multiprocessing.Lock()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)-8s :: %(message)s')
formatter.datefmt = '%Y-%m-%d %H:%M:%S'
current_time_str = datetime.now().strftime("%Y_%m_%d_%Hh_%Mm_%Ss")

# Create a file handler for info logs
info_handler = logging.FileHandler(f"logs/info_{current_time_str}.log")
info_handler.setFormatter(formatter)
info_handler.setLevel(logging.INFO)

# Create a file handler for error logs
error_handler = logging.FileHandler(f"logs/error_{current_time_str}.log")
error_handler.setFormatter(formatter)
error_handler.setLevel(logging.ERROR)

logger.addHandler(info_handler)
logger.addHandler(error_handler)


# Create soft links to latest logs
os.makedirs("logs", exist_ok=True)
with open(f"logs/info_{current_time_str}.log", 'w') as file:
    pass
with open(f"logs/error_{current_time_str}.log", 'w') as file:
    pass

sym_info_link = "info.log"
if os.path.exists(sym_info_link) and os.path.islink(sym_info_link):
    os.unlink(sym_info_link)
sym_error_link = "error.log"
if os.path.exists(sym_error_link) and os.path.islink(sym_error_link):
    os.unlink(sym_error_link)
    
os.symlink(f"logs/info_{current_time_str}.log", sym_info_link)
os.symlink(f"logs/error_{current_time_str}.log", sym_error_link)


def log_info(msg):
    with logger_info_lock:
        logger.info(msg)


def log_error(msg):
    with logger_error_lock:
        logger.error(msg)
            

if not IN_DIR.startswith("/"):
    log_error("Use absolute path for argument.")
    print("Use absolute path for argument.")
    sys.exit(1)


def get_all_files(parent_dir):
    # List to hold all file paths
    all_dir = []
    all_files = []
    # Walk through all directories and files recursively
    for root, dirs, files in os.walk(parent_dir):
        # avoid going into these subdirectories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        all_dir.append(root)
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)

    return all_files, all_dir


def digest_input(path):
    '''
    takes in an input file, and returns useful information.
    Returns
    transplanted_input: the input file's path if it were copied over to OUT_DIR. Essentially readlink -f $OUT_DIR/input_file
    input_extension: get the file extension of the input file
    output_flac: Essentially readlink -f $OUT_DIR/output_file
    
    Note: It can also be used for finding output_dir.
    '''
    relative_path = path[len(IN_DIR):].lstrip('/')
    transplanted_input = os.path.join(OUT_DIR, relative_path)
    file_parts = transplanted_input.split(".")
    input_extension = file_parts[-1]
    file_parts[-1] = "flac"
    output_flac = ".".join(file_parts)
    return transplanted_input, input_extension, output_flac


def create_directories(all_dir):
    '''
    let a single thread create the directories first
    otherwise, two processes doing new_dir/file1 and new_dir/file2 respectively
    can run into concurrency issues when they're both creating new_dir
    '''
    for d in all_dir:
        output_dir, garbage1, garbage2 = digest_input(d)
        # does mkdir -p
        os.makedirs(output_dir, exist_ok=True)


def find_sample_rate(file):
    cmd = f"sox --info input \n".split()
    # do this instead of f-strings because we don't want to split the "file" with spaces
    cmd[cmd.index("input")] = file 

    result = subprocess.run(cmd, capture_output=True)
    res = [item.decode("utf-8") for item in result.stdout.split()]
    sample_rate = res[res.index("Rate") + 2] # "Rate", ":", "44100"
    return int(sample_rate)
    

def write_history(msg):
    with history_file_lock:
        with open(history_file, 'a') as f:
            f.write(f"{msg}\n")


def upsample_sinc(input):
    try:
        transplanted_input, input_extension, output_flac  = digest_input(input)
        # do not perform upsampling
        if input_extension not in INPUT_FORMATS:
            if transplanted_input in history_readonly:
                log_info(f"Skipping: {transplanted_input} already exists")
                return True
            cmd = f"cp input output".split()
            cmd[cmd.index("input")] = input
            cmd[cmd.index("output")] = transplanted_input
            result = subprocess.run(cmd, capture_output=True)
            if result.returncode > 0:
                raise RuntimeError(f"When doing cp command: {result.stderr.decode()}")
            write_history(transplanted_input)
            return True
        
        if output_flac in history_readonly:
            log_info(f"{output_flac} already exists. Skipping..")
            return True
        
        # 4x upsampling for PI2AES interface limit
        sample_rate = find_sample_rate(input)
        sample_target = 192000
        if sample_rate % 44100 == 0:
            sample_target = 176400

        cmd = "sox -S -V6 input -b 24 -r sample_target output upsample 4 sinc -22050 -n 8000000 -L -b 0 vol 4".split()
        cmd[cmd.index("input")] = input
        cmd[cmd.index("output")] = output_flac
        cmd[cmd.index("sample_target")] = str(sample_target)
        log_info(f"Making... {output_flac}")
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode > 0:
                raise RuntimeError(f"When doing sox sinc command: {result.stderr.decode()}")
        
        # write mark of completion in history_file
        write_history(output_flac)
        log_info(f"Completed {output_flac}")
    except Exception as e:
        log_error(f"\ninput: {input}\noutput_flac: {output_flac}\nmessage: {e}")
        return False
    return True
    

if __name__ == "__main__":
    
    all_files, all_dir = get_all_files(IN_DIR)
    create_directories(all_dir)
    
    # read in history.txt
    # this history file keeps track of jobs that were completed, or were in-progress
    # state in-progress means that script crashed or was killed before output file was finalized
    # Ultimately, this lets us know which output files should be overwritten since they are corrupted
    if os.path.exists(history_file):
        with open(history_file, 'r') as file:
            lines = [line.lstrip().rstrip() for line in file.readlines()] # in particular, remove '\n' from line
            history_readonly.update(lines)
    
    num_processes = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=num_processes)
    
    log_info(f"\nAccording to the history file, we already processed {len(history_readonly)} / {len(all_files)} files.\n")
    
    results = pool.map(upsample_sinc, all_files)
    pool.close()
    pool.join()

    successes = Counter(results)
    log_info(f"Success rate: {successes[True]} / {len(results)}")

    # # logging and tests
    new_files, new_dir = get_all_files(OUT_DIR)
    print(len(new_dir), len(all_dir), len(new_files), len(all_files))
