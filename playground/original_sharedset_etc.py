import multiprocessing
import time


# Function to process an item of data
def process_data(item, log_file, processed_items, lock):
    # Simulate processing time
    time.sleep(item)  # Assuming each item takes 'item' seconds to process

    # Write log to file
    with lock:
        with open(log_file, "a") as f:
            f.write(f"Processed item {item}\n")

    # Add the processed item to the shared set
    with processed_items.get_lock():
        processed_items.add(item)

    # Example processing: doubling the item
    return item * 2


if __name__ == "__main__":
    # Define the list of data to be processed
    data_list = [1, 2, 3, 4, 5]  # Example list of data

    # Create a multiprocessing pool with the number of desired worker processes
    num_processes = multiprocessing.cpu_count()  # Use number of CPU cores
    pool = multiprocessing.Pool(processes=num_processes)

    # Create a multiprocessing manager
    manager = multiprocessing.Manager()
    # Create a shared set for processed items
    processed_items = manager.list()

    # Create a global lock for synchronization
    lock = manager.Lock()

    # Define the log file
    log_file = "processing_logs.txt"

    # Map the data processing function to the list of data
    results = pool.starmap(
        process_data, [(item, log_file, processed_items, lock) for item in data_list]
    )

    # Close the pool to prevent further tasks from being submitted
    pool.close()

    # Wait for all processes to complete
    pool.join()

    # Print the results
    print("Processed results:", results)
    # Print the processed items
    print("Processed items:", processed_items)
