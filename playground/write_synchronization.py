import multiprocessing
import time


lock = None
queue = None

def write_to_file(filename, lck, q, data, n):
    global lock, queue
    lock = lck
    queue = q
    with lock:
        for i in range(n):
            time.sleep(0.1)
            with open(filename, 'a') as file:
                # Acquire the lock before writing to the file
                file.write(data)
            if i % 3 == 0:
                queue.put(True)
            else:
                queue.put(False)
    

# only for single instance of monitor
success = 0
fail = 0
def monitor(q, n):
    global success, fail, lock, queue
    queue = q
    while True:
        item = queue.get()
        if item:
            success += 1
        else:
            fail += 1
        print(f"{success} successful | {fail} failed | {n} total tasks")
        if success + fail == n:
            print("Monitor done.")
            break

if __name__ == '__main__':
    filename = 'data.txt'

    manager = multiprocessing.Manager()

    lock = manager.Lock()  # Create a lock object    
    pool = multiprocessing.Pool(processes=3)
    
    queue = manager.Queue()
    history_file_lock = manager.Lock()
    logger_info_lock = manager.Lock()
    logger_error_lock = manager.Lock()
    
    n = 30
    pool.starmap_async(monitor, [(queue, 2 * n)])
    pool.starmap_async(write_to_file, [(filename, lock, queue, '1', n),
                                (filename, lock, queue, '0', n)])
    
    pool.close()
    pool.join()
    
    print("main exiting")