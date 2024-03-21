import os
import sys
import subprocess
import multiprocessing


# root directory for music
IN_DIR = sys.argv[1]
OUT_DIR = "/mnt/f/HiRes"
EXCLUDE_DIRS = ["__MACOSX"]
INPUT_FORMATS = "8svx aif aifc aiff aiffc al amb au avr cdda cdr cvs cvsd cvu dat dvms f32 f4 f64 f8 flac fssd gsrt hcom htk ima ircam la lpc lpc10 lu maud mp2 mp3 nist prc raw s1 s16 s2 s24 s3 s32 s4 s8 sb sf sl sln smp snd sndr sndt sou sox sph sw txw u1 u16 u2 u24 u3 u32 u4 u8 ub ul uw vms voc vox wav wavpcm wve xa".split()


file_lock = multiprocessing.Lock()

if not IN_DIR.startswith("/"):
    print("Use absolute path for argument.")


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
    relative_path = path[len(IN_DIR):]
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
    

def upsample_sinc(input):
    transplanted_input, input_extension, output_flac  = digest_input(input)
    # do not perform upsampling
    if input_extension not in INPUT_FORMATS:
        if os.path.exists(transplanted_input):
            print(transplanted_input, "already exists")
            return
        cmd = f"cp input output".split()
        cmd[cmd.index("input")] = input
        cmd[cmd.index("output")] = transplanted_input
        result = subprocess.run(cmd, capture_output=True)
        print(result.stderr.decode())
        return
    
    if os.path.exists(output_flac):
        print(output_flac, "already exists")
        return
    
    sample_rate = find_sample_rate(input)
    sample_target = 192000
    if sample_rate % 44100 == 0:
        sample_target = 176400


    cmd = "sox -S -V6 input -b 24 -r sample_target output upsample 4 sinc -22050 -n 8000000 -L -b 0 vol 4".split()
    cmd[cmd.index("input")] = input
    cmd[cmd.index("output")] = output_flac
    cmd[cmd.index("sample_target")] = str(sample_target)
    print("Making...", output_flac)
    result = subprocess.run(cmd, capture_output=True)
    print(result.stdout.decode())


all_files, all_dir = get_all_files(IN_DIR)
create_directories(all_dir)

for f in all_files:
    upsample_sinc(f)



# logging and tests
new_files, new_dir = get_all_files(OUT_DIR)

for dir in all_dir:
    print(dir)
print(len(all_dir))

for dir in new_dir:
    print(dir)
print(len(new_dir))
