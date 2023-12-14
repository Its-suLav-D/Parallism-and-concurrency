"""
Course: CSE 251
Lesson Week: 11
File: Assignment.py
Name: Sulove Dahal
"""

import time
import random
import multiprocessing as mp

# number of cleaning staff and hotel guests
CLEANING_STAFF = 2
HOTEL_GUESTS = 5

# Run program for this number of seconds
TIME = 60

STARTING_PARTY_MESSAGE =  'Turning on the lights for the party vvvvvvvvvvvvvv'
STOPPING_PARTY_MESSAGE  = 'Turning off the lights  ^^^^^^^^^^^^^^^^^^^^^^^^^^'

STARTING_CLEANING_MESSAGE =  'Starting to clean the room >>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
STOPPING_CLEANING_MESSAGE  = 'Finish cleaning the room <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'

# Locke & Keys haha
room_lock = mp.Lock()
guest_count_lock = mp.Lock()
guest_count = mp.Value('i', 0) 

# Helper functions
def cleaner_waiting():
    time.sleep(random.uniform(0, 2))

def cleaner_cleaning(id):
    print(f'Cleaner {id}: Cleaning')
    time.sleep(random.uniform(0, 2))

def guest_waiting():
    time.sleep(random.uniform(0, 2))

def guest_partying(id, count):
    print(f'Guest {id}: Party count = {count}')
    time.sleep(random.uniform(0, 1))

# Extra Helpers 
def start_cleaning(id, cleaned_count):
    print(STARTING_CLEANING_MESSAGE)
    cleaner_cleaning(id)
    with cleaned_count.get_lock():
        cleaned_count.value += 1

def finish_cleaning():
    print(STOPPING_CLEANING_MESSAGE)

def enter_room_as_guest(id, party_count):
    with guest_count_lock:
        if guest_count.value == 0:
            room_lock.acquire()
            print(STARTING_PARTY_MESSAGE)
            with party_count.get_lock():
                party_count.value += 1
        guest_count.value += 1
    guest_partying(id, party_count.value)


def leave_room_as_guest():
    with guest_count_lock:
        guest_count.value -= 1
        if guest_count.value == 0:
            print(STOPPING_PARTY_MESSAGE)
            room_lock.release()


# Processes
def cleaner(id, cleaned_count):
    """
    do the following for TIME seconds
        cleaner will wait to try to clean the room (cleaner_waiting())
        get access to the room
        display message STARTING_CLEANING_MESSAGE
        Take some time cleaning (cleaner_cleaning())
        display message STOPPING_CLEANING_MESSAGE
    """
    end_time = time.time() + TIME
    while time.time() < end_time:
        cleaner_waiting()
        with room_lock:
            start_cleaning(id, cleaned_count)
            finish_cleaning()

def guest(id, party_count):
    """
    do the following for TIME seconds
        guest will wait to try to get access to the room (guest_waiting())
        get access to the room
        display message STARTING_PARTY_MESSAGE if this guest is the first one in the room
        Take some time partying (call guest_partying())
        display message STOPPING_PARTY_MESSAGE if the guest is the last one leaving in the room
    """
    end_time = time.time() + TIME
    while time.time() < end_time:
        guest_waiting()
        enter_room_as_guest(id, party_count)
        leave_room_as_guest()

def main():
    cleaned_count = mp.Value('i', 0)
    party_count = mp.Value('i', 0)


    cleaners = [mp.Process(target=cleaner, args=(i, cleaned_count)) for i in range(CLEANING_STAFF)]
    guests = [mp.Process(target=guest, args=(i, party_count)) for i in range(HOTEL_GUESTS)]

    for p in cleaners + guests:
        p.start()

    for p in cleaners + guests:
        p.join()

    print(f'Room was cleaned {cleaned_count.value} times, there were {party_count.value} parties')




if __name__ == '__main__':
    main()
