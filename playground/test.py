import os
import sys
import subprocess


sample_rates = []

file = "Pablo Casals-06-Bach _ Partita No.1 In B Flat Major BWV.825 - IV. Sarabande.mp3"
# cmd = f"sox --info f1 \n".split()
# cmd[2] = file
output_flac = "bach_sarabande.flac"
cmd = "sox -S -V6 input -b 24 -r sample_target output upsample 4 sinc -22050 -n 100000 -L -b 0 vol 4".split()
cmd[cmd.index("input")] = file
cmd[cmd.index("output")] = output_flac
cmd[cmd.index("sample_target")] = "176400"

result = subprocess.run(cmd, capture_output=True)
print(0, result.returncode)
print(1, result.stdout.decode())
print(2, result.stderr.decode())
# res = [item.decode("utf-8") for item in result.stdout.split()]
# print(res)
# sample_rates.append(res[res.index("Rate") + 2])


# print(sample_rates)
