import multiprocessing
import time


lock = None
queue = None
history_readonly = None

def write_to_file(filename, data, n):
    
    if data in history_readonly:
        print("yes")
    else:
        print(history_readonly, data)
    
    with lock:
        for i in range(n):
            time.sleep(0.1)
            with open(filename, "a") as file:
                # Acquire the lock before writing to the file
                file.write(data)
            if i % 3 == 0:
                queue.put(True)
            else:
                queue.put(False)



def wrapper(filename, lck, q, data, n, mhistory_readonly):
    global lock, queue, history_readonly
    lock = lck
    queue = q
    history_readonly = mhistory_readonly
    
    write_to_file(filename, data, n)




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


if __name__ == "__main__":
    filename = "data.txt"


    manager = multiprocessing.Manager()
    queue = manager.Queue()
    lock = manager.Lock()  # Create a lock object
    n = 30
    history_readonly = set(['1', '2', '3'])

    pool = multiprocessing.Pool(processes=3)
    pool.starmap_async(monitor, [(queue, 2 * n)])
    pool.starmap_async(
        wrapper,
        [(filename, lock, queue, "1", n, history_readonly), (filename, lock, queue, "0", n, history_readonly)],
    )

    pool.close()
    pool.join()

    print("main exiting")
