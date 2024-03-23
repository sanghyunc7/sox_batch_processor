from datetime import datetime

# Get the current time
current_time = datetime.now()

# Convert the current time to a string
current_time_str = datetime.now().strftime("%Y_%m_%d_%Hh_%Mm_%Ss")

print("Current time as string:", current_time_str)