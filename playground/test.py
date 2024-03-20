
import os
import sys
import subprocess
for r, d, files in os.walk("/home/dan/Music/classic/Bach/"):
    for f in files:
        f = "Pablo Casals-06-Bach _ Partita No.1 In B Flat Major BWV.825 - IV. Sarabande.mp3"
        print(f)
        cmd = f"sox --info f1 \n".split()
        cmd[2] = f
        # cmd = "pwd".split()
        result = subprocess.run(cmd, capture_output=True)
        print(result.stderr.decode())
        print(result.stdout.decode())
sample_rate = ""