"""
Course: CSE 251, week 14
File: functions.py
Author: Sulove Dahal

Instructions:

Depth First Search
https://www.youtube.com/watch?v=9RHO6jU--GU

Breadth First Search
https://www.youtube.com/watch?v=86g8jAQug04


Requesting a family from the server:
request = Request_thread(f'{TOP_API_URL}/family/{id}')
request.start()
request.join()

Example JSON returned from the server
{
    'id': 6128784944, 
    'husband_id': 2367673859,        # use with the Person API
    'wife_id': 2373686152,           # use with the Person API
    'children': [2380738417, 2185423094, 2192483455]    # use with the Person API
}

Requesting an individual from the server:
request = Request_thread(f'{TOP_API_URL}/person/{id}')
request.start()
request.join()

Example JSON returned from the server
{
    'id': 2373686152, 
    'name': 'Stella', 
    'birth': '9-3-1846', 
    'parent_id': 5428641880,   # use with the Family API
    'family_id': 6128784944    # use with the Family API
}

You will lose 10% if you don't detail your part 1 and part 2 code below

Describe how to speed up part 1

- To speed up Part 1, I'll fetch the details for all family members – husband, wife, and children – at the same time, rather than one by one. This parallel processing will save time. Also, I'll start the threads for both the husband and wife together and then wait for them to complete, allowing these tasks to run concurrently. This approach will make the whole process more efficient and faster.




Describe how to speed up part 2

- To speed up Part 2, I'll make a few key changes to handle threads and requests more efficiently. First, in the breadth_fs_pedigree function, I'll manage the threads smarter. Instead of waiting for every single thread to finish before starting new ones, I'll keep an eye on them and join the completed ones while others are still running. This way, there's always something being processed, and we're not just waiting around.

Next, for the process_individuals function, I'll introduce concurrent processing of the husband, wife, and children. I'll start all their threads at once and then join them together. It's like setting up multiple tasks to run side by side, rather than waiting for each one to finish before starting the next.
        
"""
from common import *
from queue import Queue
import queue 
from threading import Semaphore

    
class FamilyMemberThread(threading.Thread):
    lock = threading.Lock()  

    def __init__(self, member_id, tree):
        threading.Thread.__init__(self)
        self.member_id = member_id
        self.tree = tree

    def run(self):
        request = Request_thread(f'{TOP_API_URL}/person/{self.member_id}')
        request.start()
        request.join()
        person_data = request.get_response()
        if person_data:
            with FamilyMemberThread.lock:  
                if not self.tree.does_person_exist(person_data['id']):
                    person = Person(person_data)
                    self.tree.add_person(person)


def depth_fs_pedigree(family_id, tree):
    if family_id is None:
        return

    req_family = Request_thread(f'{TOP_API_URL}/family/{family_id}')
    req_family.start()
    req_family.join()
    new_family = Family(req_family.get_response())
    tree.add_family(new_family)

    # Get husband details
    husband_id = new_family.get_husband()
    req_person1 = Request_thread(f'{TOP_API_URL}/person/{husband_id}')
    req_person1.start()

    # Get wife details
    wife_id = new_family.get_wife()
    req_person2 = Request_thread(f'{TOP_API_URL}/person/{wife_id}')
    req_person2.start()

    # Retrieve the children
    child_threads = []
    for child_id in new_family.get_children():
        if not tree.does_person_exist(child_id):
            child_thread = Request_thread(f'{TOP_API_URL}/person/{child_id}')
            child_thread.start()
            child_threads.append(child_thread)

    # Wait for the children threads to complete
    for child_thread in child_threads:
        child_thread.join()
        child_data = child_thread.get_response()
        if child_data:
            child = Person(child_data)
            tree.add_person(child)

    # Wait for the husband and wife threads to complete
    req_person1.join()
    req_person2.join()
    
    # Convert the parents data into Person objects and add to tree
    husband_data = req_person1.get_response()
    wife_data = req_person2.get_response()
    if husband_data:
        husband = Person(husband_data)
        tree.add_person(husband)
    if wife_data:
        wife = Person(wife_data)
        tree.add_person(wife)

    # Process the husband's and wife's parents
    husband_thread = wife_thread = None
    if husband and husband.get_parentid():
        husband_thread = threading.Thread(target=depth_fs_pedigree, args=(husband.get_parentid(), tree))
        husband_thread.start()

    if wife and wife.get_parentid():
        wife_thread = threading.Thread(target=depth_fs_pedigree, args=(wife.get_parentid(), tree))
        wife_thread.start()

    # Wait for the husband's and wife's parents threads
    if husband_thread:
        husband_thread.join()
    if wife_thread:
        wife_thread.join()

# -----------------------------------------------------------------------------
def breadth_fs_pedigree(start_family_id, tree):
    queue = Queue()
    queue.put(start_family_id)
    processed_families = set()
    active_threads = []

    while not queue.empty() or active_threads:
        # Start processing families in the queue
        while not queue.empty():
            family_id = queue.get()
            if family_id in processed_families:
                continue

            thread = threading.Thread(target=process_family, args=(family_id, queue, tree, processed_families))
            thread.start()
            active_threads.append(thread)

        # Clean up completed threads
        for thread in list(active_threads):
            if not thread.is_alive():
                thread.join()
                active_threads.remove(thread)

def process_family(family_id, queue, tree, processed_families):
    # Guard
    if family_id in processed_families:
        return

    # Get the requested family
    req_family = Request_thread(f'{TOP_API_URL}/family/{family_id}')
    req_family.start()
    req_family.join()
    family_data = req_family.get_response()
    if not family_data:
        return

    new_family = Family(family_data)
    tree.add_family(new_family)
    processed_families.add(family_id)

    # Process husband, wife, and children
    process_individuals(new_family, tree)

    # Enqueue parents' families for future processing
    husband = tree.get_person(new_family.get_husband())
    wife = tree.get_person(new_family.get_wife())

    if husband and husband.get_parentid() and husband.get_parentid() not in processed_families:
        queue.put(husband.get_parentid())

    if wife and wife.get_parentid() and wife.get_parentid() not in processed_families:
        queue.put(wife.get_parentid())

def process_individuals(family, tree):
    # Create threads for husband, wife, and children
    person_ids = [family.get_husband(), family.get_wife()] + family.get_children()
    threads = []

    for person_id in person_ids:
        if person_id and not tree.does_person_exist(person_id):
            thread = threading.Thread(target=process_person, args=(person_id, tree))
            thread.start()
            threads.append(thread)

    # Wait 
    for thread in threads:
        thread.join()

def process_person(person_id, tree):
    req_person = Request_thread(f'{TOP_API_URL}/person/{person_id}')
    req_person.start()
    req_person.join()
    person_data = req_person.get_response()
    if person_data:
        person = Person(person_data)
        tree.add_person(person)


# -----------------------------------------------------------------------------
def breadth_fs_pedigree_limit5(family_id, tree):
    if family_id is None:
        return

    family_queue = queue.Queue()
    family_queue.put(family_id)
    processed_families = set()
    thread_semaphore = Semaphore(5)

    def fetch_family_data(fid):
        request = Request_thread(f'{TOP_API_URL}/family/{fid}')
        request.start()
        request.join()
        return request.get_response()

    def fetch_person_data(pid):
        request = Request_thread(f'{TOP_API_URL}/person/{pid}')
        request.start()
        request.join()
        return request.get_response()

    def process_family(fid):
        if fid in processed_families:
            return

        family_data = fetch_family_data(fid)
        if family_data is None:
            return

        family = Family(family_data)
        tree.add_family(family)
        processed_families.add(fid)

        for pid in [family.get_husband(), family.get_wife()] + family.get_children():
            if pid and not tree.does_person_exist(pid):
                person_data = fetch_person_data(pid)
                if person_data:
                    person = Person(person_data)
                    tree.add_person(person)

                    if person.get_parentid() and person.get_parentid() not in processed_families:
                        family_queue.put(person.get_parentid())

    def _helper(fid):
        process_family(fid)
        thread_semaphore.release()

    while not family_queue.empty():
        threads = []
        count = 0

        while count < 5 and not family_queue.empty():
            thread_semaphore.acquire()
            process_family_id = family_queue.get()
            t = threading.Thread(target=_helper, args=(process_family_id,))
            t.start()
            threads.append(t)
            count += 1

        for t in threads:
            t.join()
