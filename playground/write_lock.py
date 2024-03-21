import multiprocessing

# Create a lock object
file_lock = multiprocessing.Lock()

def write_to_file(filename, data):
    # Acquire the lock before writing to the file
    with file_lock:
        with open(filename, 'a') as f:
            f.write(data)
            f.write('\n')  # Ensure data is written on a new line

# Example usage in multiple processes
def process_function(process_id):
    for i in range(50):
        write_to_file('shared_file.txt', f'Process {process_id} - Line {i}')

# Create and start multiple processes
processes = []
for i in range(5):
    process = multiprocessing.Process(target=process_function, args=(i,))
    processes.append(process)
    process.start()

# Wait for all processes to complete
for process in processes:
    process.join()

print("All processes have finished writing to the file.")
