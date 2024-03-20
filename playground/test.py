
import os
import sys
import subprocess


sample_rates = []
for r, dirs, files in os.walk("/home/dan/Music/classic/john/Tchaikovsky"):
    print(r)
    
    dirs[:] = [d for d in dirs if d not in "__MACOSX"]

    for f in files:
        if not (f.endswith(".mp3") or f.endswith(".flac")):
            continue
        # f = "Pablo Casals-06-Bach _ Partita No.1 In B Flat Major BWV.825 - IV. Sarabande.mp3"
        file = os.path.join(r, f)
        print(file)
        cmd = f"sox --info f1 \n".split()
        cmd[2] = file

        result = subprocess.run(cmd, capture_output=True)
        print(result.stdout.decode())
        res = [item.decode("utf-8") for item in result.stdout.split()]
        print(res)
        sample_rates.append(res[res.index("Rate") + 2])
        

print(sample_rates)