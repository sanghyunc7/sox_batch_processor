import multiprocessing
import time


def producer(queue, item):
    print("Producer send:", item)
    if item % 10 == 0:
        queue.put(False)
    else:
        queue.put(True)
    # if item == 19:
    #     queue.put(None)


# only for single instance of consumer
success = 0
fail = 0


def consumer(queue, n):
    global success, fail
    while True:
        item = queue.get()
        if item:
            success += 1
        else:
            fail += 1
        print(f"{success} successful | {fail} failed | {n} total tasks")
        if success + fail == n:
            print("breaking")
            break


if __name__ == "__main__":
    with multiprocessing.Pool(processes=2) as pool:
        with multiprocessing.Manager() as manager:
            queue = manager.Queue()  # Create a shared queue

            n = 2000
            # Use starmap_async to apply the consumer function to a single tuple of arguments
            pool.starmap_async(consumer, [(queue, n)])

            # Use starmap_async to apply the producer function to multiple tuples of arguments
            pool.starmap_async(producer, [(queue, i) for i in range(n)])

            # Give some time for the tasks to execute concurrently
            pool.close()
            pool.join()
            print("main exiting")
            # time.sleep(1)
