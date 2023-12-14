from datetime import datetime, timedelta
import threading

from cse251 import * 

prime_count = 0
numbers_processed = 0
lock = threading.Lock()

def is_prime(n):
    global numbers_processed
    numbers_processed += 1

    """Primality test using 6k+-1 optimization.
    From: https://en.wikipedia.org/wiki/Primality_test
    """
    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i ** 2 <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def threading_task(start, end):
    global prime_count
    for i in range(start, end):
        if is_prime(i):
            with lock:
                prime_count += 1
                print(i, end=', ', flush=True)
    print(flush=True)


if __name__ == "__main__":
    log = Log(show_terminal=True)
    log.start_timer()

    start = 10000000000
    range_count = 100000
    step = range_count // 10
    threads = []


    for i in range(10):
        thread_start = start + (i * step)
        thread_end = thread_start + step
        thread = threading.Thread(target=threading_task, args=(thread_start, thread_end))
        threads.append(thread)


    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print(flush=True)


    # Should find 4306 primes
    log.write(f'Numbers processed = {numbers_processed}')
    log.write(f'Primes found      = {prime_count}')
    log.stop_timer('Total time')