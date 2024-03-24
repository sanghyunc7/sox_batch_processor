lines = []
with open('history.txt', "r") as file:
    lines = file.readlines()

timelines = []

with open('new_history.txt', 'w') as file:
    for line in lines:
        file.writelines(f"1427 {line}")