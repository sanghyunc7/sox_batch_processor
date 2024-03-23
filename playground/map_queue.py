import multiprocessing
import time

def producer(queue, item):
    print("Producer send:", item)
    queue.put(item)
    # if item == 19:
    #     queue.put(None)

total = 0 # to be used by single instance of consumer
def consumer(queue, n):
    global total
    while True:
        item = queue.get()
        total += 1
        # if item is None:
        #     break
        print("Consumer got:", item, total)
        if total == n:
            print("breaking")
            break

if __name__ == '__main__':
    with multiprocessing.Pool(processes=2) as pool:
        with multiprocessing.Manager() as manager:
            queue = manager.Queue()  # Create a shared queue
        
            n = 20
            # Use starmap_async to apply the consumer function to a single tuple of arguments
            pool.starmap_async(consumer, [(queue)])
            
            # Use starmap_async to apply the producer function to multiple tuples of arguments
            pool.starmap_async(producer, [(queue, i, n) for i in range(n)])
            
            # Give some time for the tasks to execute concurrently
            time.sleep(1)
