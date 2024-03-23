import os


history_file = "history.txt"
history_readonly = set()
output_flac = "sample.flac"
output_flac2 = "sample2.flac"

with open(history_file, "a") as f:
    f.write(f"{output_flac}\n")
    f.write(f"{output_flac2}\n")


if os.path.exists(history_file):
    with open(history_file, "r") as file:
        lines = [line.lstrip().rstrip() for line in file.readlines()]
        history_readonly.update(lines)


print(history_readonly)

if output_flac in history_readonly:
    print(f"{output_flac} already exists. Skipping..")

if output_flac2 in history_readonly:
    print(f"{output_flac2} already exists. Skipping..")

print("done")
