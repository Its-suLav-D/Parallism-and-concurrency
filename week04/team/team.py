"""
Course: CSE 251 
Lesson: L04 Team Activity
File:   team.py
Author: <Add name here>

Purpose: Practice concepts of Queues, Locks, and Semaphores.

Instructions:

- Review instructions in Canvas.

Question:

- Is the Python Queue thread safe? (https://en.wikipedia.org/wiki/Thread_safety)
"""

import threading
import queue
import requests
import json

# Include cse 251 common Python files
from cse251 import *

RETRIEVE_THREADS = 4        # Number of retrieve_threads
NO_MORE_VALUES = 'No more'  # Special value to indicate no more items in the queue

def retrieve_thread(shared_queue, semaphore, log):  # TODO add arguments
    """ Process values from the data_queue """

    while True:
        url = shared_queue.get()
        if url == NO_MORE_VALUES:
            break
        try:
            semaphore.acquire()
            log.write(f'processing {url}')
            response = requests.get(url)
            data = response.json()
            print("Name: ", data['name'])
            semaphore.release() 
        except Exception as catch:
            print("Error:", catch)
            semaphore.release()


def file_reader(shared_queue, semaphore, log): # TODO add arguments
    """ This thread reading the data file and places the values in the data_queue """

    # TODO Open the data file "urls.txt" and place items into a queue
    with open('urls.txt') as file:
        for line in file:
            semaphore.acquire()
            shared_queue.put(line.strip())
            semaphore.release()
            
    log.write('finished reading file')

    # TODO signal the retrieve threads one more time that there are "no more values"
    for _ in range(RETRIEVE_THREADS):
        shared_queue.put(NO_MORE_VALUES)


def main():
    """ Main function """

    log = Log(show_terminal=True)

    # TODO create queue
    shared_data_queue = queue.Queue()
    # TODO create semaphore (if needed)
    semaphore = threading.Semaphore(1)

    # TODO create the threads. 1 filereader() and RETRIEVE_THREADS retrieve_thread()s
    # Pass any arguments to these thread need to do their job
    threads = []
    t1 = threading.Thread(target=file_reader, args=(shared_data_queue, semaphore, log))

    threads.append(t1)

    # Create 4 retreive threads
    for _ in range(RETRIEVE_THREADS):
        threads.append(threading.Thread(target=retrieve_thread, args=(shared_data_queue, semaphore, log)))

    log.start_timer()

    # TODO Get them going - start the retrieve_threads first, then file_reader

    for thread in threads:
        thread.start() 

    # TODO Wait for them to finish - The order doesn't matter

    for threads in threads:
        thread.join()

    log.stop_timer('Time to process all URLS')


if __name__ == '__main__':
    main()


