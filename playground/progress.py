import multiprocessing
import time

progress = multiprocessing.Value("i", 0)  # share stack memory between processes
monitor_state = multiprocessing.Value("b", True)


# it is okay if the data gets stale by the time the function result is used
def get_progress():
    global progress
    with progress.get_lock():
        return progress.value


def get_monitor_state():
    global monitor_state
    with monitor_state.get_lock():
        return monitor_state.value


def test(i):
    global progress
    print("i", i)
    if i == 0:
        for i in range(20):
            with progress.get_lock():
                if progress.value == 19:
                    break
            print(f"{get_progress()} / --")
            time.sleep(0.1)
        print("Done monitor.")
    else:
        if i == 19:
            print("hello", progress.value)
            with monitor_state.get_lock():
                monitor_state.value = False
        time.sleep(0.1)
        with progress.get_lock():
            progress.value += 1
            print(progress.value)


if __name__ == "__main__":
    all_files = [i for i in range(20)]
    pool = multiprocessing.Pool(processes=4)

    # Submit tasks asynchronously using apply_async
    results = pool.map(test, all_files)
    print(progress.value)
    pool.close()
    pool.join()
    print("done")
