import multiprocessing
import time

def producer(queue, item):
    print("Producer send:", item)
    queue.put(item)
    if item == 19:
        queue.put(None)

def consumer(queue):
    # while not queue.empty():
    while True:
        item = queue.get()
        if item is None:
            break
        print("Consumer got:", item)

if __name__ == '__main__':
    with multiprocessing.Pool(processes=2) as pool:
        with multiprocessing.Manager() as manager:
            queue = manager.Queue()  # Create a shared queue
        
            # Use starmap_async to apply the consumer function to a single tuple of arguments
            pool.starmap_async(consumer, [(queue,)])
            
            # Use starmap_async to apply the producer function to multiple tuples of arguments
            pool.starmap_async(producer, [(queue, i) for i in range(20)])
            
            # Give some time for the tasks to execute concurrently
            time.sleep(1)
