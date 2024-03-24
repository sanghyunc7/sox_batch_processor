lines = []
with open('history.txt', "r") as f:
    lines = [line for line in f.readlines() if "/HiRes/others/" not in line]

with open('new_history.txt', 'w') as f:
    f.writelines(lines)

            