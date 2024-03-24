import os
import sys
import subprocess
import multiprocessing
import logging
import time
import traceback
from datetime import datetime
from collections import Counter

TEST = False
OUT_DIR = "/mnt/f/HiRes"
if TEST:
    OUT_DIR = "/home/dan/test_music2"

# where is your music
IN_DIR = "/mnt/f/Music"
if len(sys.argv) > 1:
    IN_DIR = sys.argv[1]
if not IN_DIR.startswith("/"):
    print("Use absolute path for argument.")
    sys.exit(1)


EXCLUDE_DIRS = ["__MACOSX"]
INPUT_FORMATS = "8svx aif aifc aiff aiffc al amb au avr cdda cdr cvs cvsd cvu dat dvms f32 f4 f64 f8 flac fssd gsrt hcom htk ima ircam la lpc lpc10 lu maud mp2 mp3 nist prc raw s1 s16 s2 s24 s3 s32 s4 s8 sb sf sl sln smp snd sndr sndt sou sox sph sw txw u1 u16 u2 u24 u3 u32 u4 u8 ub ul uw vms voc vox wav wavpcm wve xa".split()


start_time = time.time()
history_file = os.path.join(OUT_DIR, "history.txt")

# shared memory between processes
# they should be initialized by main, then passed as arguments during child process creation
# those arguments should then be used to initialize the respective variables in the child process memory stack
# history_readonly doesn't have to follow this flow, as it technically does not have to be the same between processes (although it should)
logger = logger_lock = queue = history_readonly = history_file_lock = (
    timestamp_offset
) = None


# should only be called by main
def logger_init():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s :: %(levelname)-8s :: %(message)s")
    formatter.datefmt = "%Y-%m-%d %H:%M:%S"
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
    # create files but leave empty
    with open(f"logs/info_{current_time_str}.log", "w") as file:
        pass
    with open(f"logs/error_{current_time_str}.log", "w") as file:
        pass

    sym_info_link = "info.log"
    if os.path.exists(sym_info_link) and os.path.islink(sym_info_link):
        os.unlink(sym_info_link)
    sym_error_link = "error.log"
    if os.path.exists(sym_error_link) and os.path.islink(sym_error_link):
        os.unlink(sym_error_link)

    os.symlink(f"logs/info_{current_time_str}.log", sym_info_link)
    os.symlink(f"logs/error_{current_time_str}.log", sym_error_link)

    return logger


def log_info(msg, stdout=False):
    with logger_lock:
        logger.info(msg)
        if stdout:
            print(msg)


def log_error(msg, stderr=False):
    with logger_lock:
        logger.error(msg)
        if stderr:
            print(msg, file=sys.stderr)


def get_all_files(parent_dir):
    log_info(f"Finding all files of {parent_dir}..")
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

    log_info(f"Found all {len(all_files)} files and {len(all_dir)} directories.")
    return all_files, all_dir


def digest_input(path):
    """
    takes in an input file, and returns useful information.
    Returns
    transplanted_input: the input file's path if it were copied over to OUT_DIR. Essentially readlink -f $OUT_DIR/input_file
    input_extension: get the file extension of the input file
    output_flac: Essentially readlink -f $OUT_DIR/output_file

    Note: It can also be used for finding output_dir.
    """
    relative_path = path[len(IN_DIR) :].lstrip("/")
    transplanted_input = os.path.join(OUT_DIR, relative_path)
    file_parts = transplanted_input.split(".")
    input_extension = file_parts[-1]
    file_parts[-1] = "flac"
    output_flac = ".".join(file_parts)
    return transplanted_input, input_extension, output_flac


def create_directories(all_dir):
    """
    let a single thread create the directories first
    otherwise, two processes doing new_dir/file1 and new_dir/file2 respectively
    can run into concurrency issues when they're both creating new_dir
    """
    for d in all_dir:
        output_dir, garbage1, garbage2 = digest_input(d)
        # does mkdir -p
        os.makedirs(output_dir, exist_ok=True)


def find_sample_rate(file):
    sample_rate = 176400
    try:
        cmd = f"sox --info input".split()
        # do this instead of f-strings because we don't want to split the "file" with spaces
        cmd[cmd.index("input")] = file

        result = subprocess.run(cmd, capture_output=True)
        res = [item.decode("utf-8") for item in result.stdout.split()]
        sample_rate = int(res[res.index("Rate") + 2])  # "Rate", ":", "44100"
    except Exception as e:
        log_error(
            f"\ninput: {file}\nmessage: {e}\n{traceback.format_exc()}"
        )  # Traceback (most recent call last):
    return sample_rate


def get_time_passed():
    time_passed = time.time() - start_time + timestamp_offset
    hours, remainder = divmod(time_passed, 3600)
    minutes, seconds = divmod(remainder, 60)
    return int(time_passed), int(hours), int(minutes), int(seconds)


def write_history(msg):
    with history_file_lock:
        with open(history_file, "a") as f:
            time_passed, g1, g2, g3 = get_time_passed()
            f.write(f"{time_passed} {msg}\n")


def upsample_sinc(input):
    try:
        transplanted_input, input_extension, output_flac = digest_input(input)
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
            log_info(f"Copied to {transplanted_input}")
            write_history(transplanted_input)
            return True

        if output_flac in history_readonly:
            log_info(f"Skipping: {output_flac} already exists")
            return True

        # 4x upsampling for PI2AES interface limit
        sample_target = 192000
        if find_sample_rate(input) % 44100 == 0:
            sample_target = 176400

        cmd = "sox -S -V6 input -b 24 -r sample_target output upsample 4 sinc -22050 -n 8000000 -L -b 0 vol 4".split()
        cmd[cmd.index("input")] = input
        cmd[cmd.index("output")] = output_flac
        cmd[cmd.index("sample_target")] = str(sample_target)
        log_info(f"Making... {output_flac}")

        result = 0
        if TEST:
            time.sleep(0.001)
        elif not TEST:
            result = subprocess.run(cmd, capture_output=True).returncode
        if result > 0:
            raise RuntimeError(f"When doing sox sinc command: {result.stderr.decode()}")

        # write mark of completion in history_file
        write_history(output_flac)
        log_info(f"Completed {output_flac}")
    except Exception as e:
        log_error(
            f"\ninput: {input}\noutput_flac: {output_flac}\nmessage: {e}\n{traceback.format_exc()}"
        )
        return False
    return True


# this wrapper helps to assign the arguments to variables with global scope
def task(
    input,
    mlogger,
    mlogger_lock,
    mqueue,
    mhistory_readonly,
    mhistory_file_lock,
    mtimestamp_offset,
):
    global logger, logger_lock, queue, history_readonly, history_file_lock, timestamp_offset

    logger = mlogger
    logger_lock = mlogger_lock
    queue = mqueue
    history_readonly = mhistory_readonly
    history_file_lock = mhistory_file_lock
    timestamp_offset = mtimestamp_offset

    result = upsample_sinc(input)
    # print(result)
    queue.put(result)
    return result


# only for that single process assigned to be the monitor
success = 0
fail = 0


# a realtime monitor to view quick summaries on stdout
def monitor(mlogger, mlogger_lock, mqueue, mtimestamp_offset, total_tasks):
    global logger, logger_lock, queue, timestamp_offset
    global success, fail  # unique to monitor

    logger = mlogger
    logger_lock = mlogger_lock
    queue = mqueue
    timestamp_offset = mtimestamp_offset

    while True:
        item = queue.get()  # block until queue is not empty
        if item:
            success += 1
        else:
            fail += 1
        g1, hours, minutes, seconds = get_time_passed()
        print(
            f"{success} successful | {fail} failed | {total_tasks} total tasks | Time passed: {hours:02d}h:{minutes:02d}m:{seconds:02d}s"
        )
        if success + fail == total_tasks:
            print("Monitor done.")
            break
    return True


if __name__ == "__main__":
    # create shared variables
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    history_file_lock = manager.Lock()
    logger_lock = manager.Lock()
    logger = logger_init()
    log_info(f"See info.log and error.log for progress.", stdout=True)
    history_readonly = set()

    all_files, all_dir = get_all_files(IN_DIR)
    create_directories(all_dir)

    # read in history.txt
    # this history file keeps track of jobs that were completed, or were in-progress
    # state in-progress means that script crashed or was killed before output file was finalized
    # Ultimately, this lets us know which output files should be overwritten since they are corrupted
    timestamp_offset = 0
    if os.path.exists(history_file):
        with open(history_file, "r") as file:
            lines = file.readlines()
            for line in lines:
                song_offset = line.index(OUT_DIR)
                line = line.rstrip()  # of the \n in particular
                timestamp_offset = max(timestamp_offset, int(line[:song_offset]))
                history_readonly.add(line[song_offset:])

        log_info(
            f"\nAccording to the history file, we already processed {len(history_readonly)} / {len(all_files)} files.\n",
            stdout=True,
        )

    num_processes = multiprocessing.cpu_count() + 1  # 1 extra for monitor
    pool = multiprocessing.Pool(processes=num_processes)

    time.sleep(3)
    pool.apply_async(
        monitor, (logger, logger_lock, queue, timestamp_offset, len(all_files))
    )
    results = pool.starmap_async(
        task,
        [
            (
                all_files[i],
                logger,
                logger_lock,
                queue,
                history_readonly,
                history_file_lock,
                timestamp_offset,
            )
            for i in range(len(all_files))
        ],
    )
    pool.close()
    pool.join()

    results_list = results.get()
    successes = Counter(results_list)
    log_info(f"Success rate: {successes[True]} / {len(results_list)}", stdout=True)

    # # logging and tests
    new_files, new_dir = get_all_files(OUT_DIR)
    log_info(
        f"{len(new_dir)} new directories, {len(all_dir)} old directories, {len(new_files)} new files, {len(all_files)} old files",
        stdout=True,
    )
