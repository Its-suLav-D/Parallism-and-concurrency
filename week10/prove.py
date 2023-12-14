"""
Course: CSE 251
Lesson Week: 10
File: assignment.py
Author: Sulove Dahal

Purpose: assignment for week 10 - reader writer problem

Instructions:

- Review TODO comments

- writer: a process that will send numbers to the reader.  
  The values sent to the readers will be in consecutive order starting
  at value 1.  Each writer will use all of the sharedList buffer area
  (ie., BUFFER_SIZE memory positions)

- reader: a process that receive numbers sent by the writer.  The reader will
  accept values until indicated by the writer that there are no more values to
  process.  

- Do not use try...except statements

- Display the numbers received by the reader printing them to the console.

- Create WRITERS writer processes

- Create READERS reader processes

- You can use sleep() statements for any process.

- You are able (should) to use lock(s) and semaphores(s).  When using locks, you can't
  use the arguments "block=False" or "timeout".  Your goal is to make your
  program as parallel as you can.  Over use of lock(s), or lock(s) in the wrong
  place will slow down your code.

- You must use ShareableList between the two processes.  This shareable list
  will contain different "sections".  There can only be one shareable list used
  between your processes.
  1) BUFFER_SIZE number of positions for data transfer. This buffer area must
     act like a queue - First In First Out.
  2) current value used by writers for consecutive order of values to send
  3) Any indexes that the processes need to keep track of the data queue
  4) Any other values you need for the assignment

- Not allowed to use Queue(), Pipe(), List(), Barrier() or any other data structure.

- Not allowed to use Value() or Array() or any other shared data type from 
  the multiprocessing package.

- When each reader reads a value from the sharedList, use the following code to display
  the value:
  
                    print(<variable>, end=', ', flush=True)

Add any comments for me:

"""

import random
from multiprocessing.managers import SharedMemoryManager
import multiprocessing as mp


# BUFFER_SIZE = 10
READERS = 2
WRITERS = 2

class SharedBuffer:
    """ Manages indices and initialization for the shared buffer. """
    # Here are some constants for our buffer. We're setting aside extra space for control variables.
    BUFFER_SIZE = 10
    HEAD = BUFFER_SIZE
    TAIL = BUFFER_SIZE + 1
    CURRENT_VALUE = BUFFER_SIZE + 2
    READ_COUNT = BUFFER_SIZE + 3

    def __init__(self):
        # Initialize a shared memory manager and allocate a shared buffer
        self.manager = SharedMemoryManager()
        self.manager.start()
        self.buffer = self.manager.ShareableList([0] * (self.BUFFER_SIZE + 4))

    def shutdown(self):
        self.manager.shutdown()

    @property # Easy access to buffer like it's a simple attribute
    def shared_list(self):
        return self.buffer
    

# Writers put stuff into the buffer
def writer(buffer, lock, empty_sem, full_sem, items_to_send):
    for _ in range(items_to_send):
        empty_sem.acquire() # Wait until there's room in the buffer
        with lock: # Locking it up so no one messes with it while we're writing
            # Write the next value and move the tail pointer
            buffer[buffer[SharedBuffer.TAIL] % SharedBuffer.BUFFER_SIZE] = buffer[SharedBuffer.CURRENT_VALUE]
            buffer[SharedBuffer.TAIL] = (buffer[SharedBuffer.TAIL] + 1) % SharedBuffer.BUFFER_SIZE
            buffer[SharedBuffer.CURRENT_VALUE] += 1
        full_sem.release() # Let others know there's more to read

# Readers take stuff out of the buffer
def reader(buffer, lock, empty_sem, full_sem):
    while True:
        full_sem.acquire()  # Waiting for something to read
        with lock: # Lock it while we read
            # Grab the next value and move the head pointer

            value = buffer[buffer[SharedBuffer.HEAD] % SharedBuffer.BUFFER_SIZE]
            if value == -1: # SENTINEL VALUE FOR DONE 
                break
            print(value, end=', ', flush=True)
            buffer[SharedBuffer.HEAD] = (buffer[SharedBuffer.HEAD] + 1) % SharedBuffer.BUFFER_SIZE
            buffer[SharedBuffer.READ_COUNT] += 1
        empty_sem.release() # Signal we've read something, so there's space


# Setting up the writers and readers
def create_processes(buffer, lock, empty_sem, full_sem, num_writers, num_readers, items_per_writer):
    writers = [mp.Process(target=writer, args=(buffer, lock, empty_sem, full_sem, items_per_writer)) for _ in range(num_writers)]
    readers = [mp.Process(target=reader, args=(buffer, lock, empty_sem, full_sem)) for _ in range(num_readers)]
    return writers, readers


def main():
    items_to_send = random.randint(1000, 10000)
    items_per_writer = items_to_send // WRITERS # Give Each Writer numbers to process so they won't mess up 

    # Starting the shared buffer and all the sync stuff
    shared_buffer = SharedBuffer()
    lock = mp.Lock()
    empty_sem = mp.Semaphore(SharedBuffer.BUFFER_SIZE)
    full_sem = mp.Semaphore(0)

    # Get all our processes ready and start em 
    writers, readers = create_processes(shared_buffer.shared_list, lock, empty_sem, full_sem, WRITERS, READERS, items_per_writer)

    for process in writers + readers:
        process.start()

    for process in writers:
        process.join()


   # Telling the readers it's time to stop
    for _ in range(READERS):
        empty_sem.acquire()
        with lock:
            tail_index = shared_buffer.shared_list[SharedBuffer.TAIL] % SharedBuffer.BUFFER_SIZE
            shared_buffer.shared_list[tail_index] = -1 # This is our stop signal
            shared_buffer.shared_list[SharedBuffer.TAIL] += 1
        full_sem.release()

    for process in readers:
        process.join()

    print(f'\n{items_to_send} values sent')
    print(f'{shared_buffer.shared_list[SharedBuffer.READ_COUNT]} values received')

    shared_buffer.shutdown()

if __name__ == '__main__':
    main()