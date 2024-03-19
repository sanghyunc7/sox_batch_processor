import os
import sys

OUT_DIR = "/mnt/f/HiRes"

if not sys.argv[1].startswith('/'):
    print("Use absolute path for argument.")

def get_all_files(parent_dir):
    # List to hold all file paths
    all_dir = []
    all_files = []
    # Walk through all directories and files recursively
    for root, dirs, files in os.walk(parent_dir):
        all_dir.append(root)
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)

    return all_files, all_dir


# let a single thread create the directories first
# otherwise, two processes doing new_dir/file1 and new_dir/file2 respectively
# can run into concurrency issues when they're both creating new_dir
def create_directories(all_dir):
    input = len(sys.argv[1])

    for d in all_dir:
        relative_path = d[input:]
        absolute_out = os.path.join(OUT_DIR, relative_path)
        # does mkdir -p
        os.makedirs(absolute_out, exist_ok=True)
    
    
parent_directory = sys.argv[1]
all_files, all_dir = get_all_files(parent_directory)

create_directories(all_dir)





# logging and tests
new_files, new_dir = get_all_files(OUT_DIR)

for dir in all_dir:
    print(dir)
print(len(all_dir))

for dir in new_dir:
    print(dir)
print(len(new_dir))
