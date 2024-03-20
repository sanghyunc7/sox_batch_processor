import os
import sys
import subprocess


# root directory for music
IN_DIR = sys.argv[1]
OUT_DIR = "/mnt/f/HiRes"
EXCLUDE_DIRS = ["__MACOSX"]
INPUT_FORMATS = "8svx aif aifc aiff aiffc al amb au avr cdda cdr cvs cvsd cvu dat dvms f32 f4 f64 f8 flac fssd gsrt hcom htk ima ircam la lpc lpc10 lu maud mp2 mp3 nist prc raw s1 s16 s2 s24 s3 s32 s4 s8 sb sf sl sln smp snd sndr sndt sou sox sph sw txw u1 u16 u2 u24 u3 u32 u4 u8 ub ul uw vms voc vox wav wavpcm wve xa".split()

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


def convert_to_output_path(path):
    relative_path = path[len(IN_DIR):]
    absolute_out = os.path.join(OUT_DIR, relative_path)
    return absolute_out


# let a single thread create the directories first
# otherwise, two processes doing new_dir/file1 and new_dir/file2 respectively
# can run into concurrency issues when they're both creating new_dir
def create_directories(all_dir):
    for d in all_dir:
        output_dir = convert_to_output_path(d)
        # does mkdir -p
        os.makedirs(output_dir, exist_ok=True)


def upsample(file):
    out_file = convert_to_output_path(file)
    file_parts = out_file.split('.')
    
    # do not perform upsampling
    if file_parts[-1] not in INPUT_FORMATS:
        if os.path.exists(out_file):
            print(out_file, "already exists")
            return
        cmd = f"cp {file} {out_file}".split()
        subprocess.run(cmd, capture_output=True)
        print(result.stdout.decode())
        return
    
    # sample_rate = 
    
    
    file_parts[-1] = 'flac'
    out_file = ".".join(file_parts)
    if os.path.exists(out_file):
        print(out_file, "already exists")
        return
    

    cmd = "./sox -S -V6 placeholder1 -b 24 -r 176400 placeholder2 upsample 4 sinc -22050 -n 8000000 -L -b 0 vol 4".split()
    cmd[cmd.index("placeholder1")] = file # do this instead of f-strings because we don't want to split the file with spaces
    cmd[cmd.index("placeholder2")] = out_file
    result = subprocess.run(cmd, capture_output=True)
    print(result.stdout.decode())


all_files, all_dir = get_all_files(IN_DIR)
create_directories(all_dir)

for f in all_files:
    upsample(f)



# logging and tests
new_files, new_dir = get_all_files(OUT_DIR)

for dir in all_dir:
    print(dir)
print(len(all_dir))

for dir in new_dir:
    print(dir)
print(len(new_dir))
