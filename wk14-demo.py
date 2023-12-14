def depth_fs_pedigree(family_id, tree):
    """
    The `depth_fs_pedigree` function is meant to be recursive so we need to add
    a stop for when we reach the end of a branch.
    """
    if family_id == None:
        return

    # Get the requested family; we gave you this code already.
    req_family = Request_thread(f'{TOP_API_URL}/family/{family_id}')
    req_family.start()
    req_family.join()

    # Make sure to add this family to the tree you're building; modified from what we did last time.
    new_family = Family(req_family.get_response())
    tree.add_family(new_family)

    husband = None
    wife = None

    # Get husband details:
    husband_id = new_family.get_husband()
    req_person1 = Request_thread(f'{TOP_API_URL}/person/{husband_id}')
    req_person1.start()

    # Get wife details:
    wife_id = new_family.get_wife()
    req_person2 = Request_thread(f'{TOP_API_URL}/person/{wife_id}')
    req_person2.start()

    # Retrieve the children:
    children = []
    for child_id in new_family.get_children():
        # Don't request a person if that person is in the tree already.
        if not tree.does_person_exist(child_id):
            # Request the next childs data...
            pass

    # Wait on the children threads...
    pass

    # Convert the children data into a Person object.
    pass
    
    # Wait on the husband and wife details threads...
    pass

    # Convert the parents data into Person objects.
    husband = Person(req_person1.get_response())
    wife = Person(req_person2.get_response())

    # Go up the path of the husband's parents:
    husband_thread = None
    if husband != None:
        pass

    # Go up the path of the wife's parents:
    wife_thread = None
    if wife != None:
        pass

    # Wait on the husband and wife parents threads....
    pass



from queue import Queue
import threading

def breadth_fs_pedigree(family_id, tree):
    if family_id is None:
        return

    queue = Queue()
    queue.put(family_id)

    while not queue.empty():
        current_family_id = queue.get()

        # Fetching the current family
        req_family = Request_thread(f'{TOP_API_URL}/family/{current_family_id}')
        req_family.start()
        req_family.join()
        new_family = Family(req_family.get_response())
        tree.add_family(new_family)

        # Start threads for husband and wife but do not join immediately
        husband_thread = wife_thread = None
        if new_family.get_husband():
            husband_thread = threading.Thread(target=request_person_and_enqueue, args=(new_family.get_husband(), tree, queue))
            husband_thread.start()

        if new_family.get_wife():
            wife_thread = threading.Thread(target=request_person_and_enqueue, args=(new_family.get_wife(), tree, queue))
            wife_thread.start()

        # Process children
        process_children(new_family.get_children(), tree, queue)

        # Join husband and wife threads after children processing
        if husband_thread:
            husband_thread.join()
        if wife_thread:
            wife_thread.join()

def process_children(children_ids, tree, queue):
    child_threads = []
    for child_id in children_ids:
        if not tree.does_person_exist(child_id):
            child_thread = threading.Thread(target=request_person_and_enqueue, args=(child_id, tree, queue))
            child_thread.start()
            child_threads.append(child_thread)

    # Wait for all child threads to complete
    for thread in child_threads:
        thread.join()

def request_person_and_enqueue(person_id, tree, queue):
    req_person = Request_thread(f'{TOP_API_URL}/person/{person_id}')
    req_person.start()
    req_person.join()
    person_data = req_person.get_response()
    if person_data:
        person = Person(person_data)
        tree.add_person(person)
        if person.get_parentid():
            queue.put(person.get_parentid())


# def depth_fs_pedigree(family_id, tree):
#     if family_id is None:
#         return

#     req_family = Request_thread(f'{TOP_API_URL}/family/{family_id}')
#     req_family.start()
#     req_family.join()
#     new_family = Family(req_family.get_response())
#     tree.add_family(new_family)

#     # Get husband details
#     husband_id = new_family.get_husband()
#     req_person1 = Request_thread(f'{TOP_API_URL}/person/{husband_id}')
#     req_person1.start()

#     # Get wife details
#     wife_id = new_family.get_wife()
#     req_person2 = Request_thread(f'{TOP_API_URL}/person/{wife_id}')
#     req_person2.start()

#     # Retrieve the children
#     child_threads = []
#     for child_id in new_family.get_children():
#         if not tree.does_person_exist(child_id):
#             child_thread = Request_thread(f'{TOP_API_URL}/person/{child_id}')
#             child_thread.start()
#             child_threads.append(child_thread)

#     # Wait for the children threads to complete
#     for child_thread in child_threads:
#         child_thread.join()
#         child_data = child_thread.get_response()
#         if child_data:
#             child = Person(child_data)
#             tree.add_person(child)

#     # Wait for the husband and wife threads to complete
#     req_person1.join()
#     req_person2.join()
    
#     # Convert the parents data into Person objects and add to tree
#     husband_data = req_person1.get_response()
#     wife_data = req_person2.get_response()
#     if husband_data:
#         husband = Person(husband_data)
#         tree.add_person(husband)
#     if wife_data:
#         wife = Person(wife_data)
#         tree.add_person(wife)

#     # Process the husband's and wife's parents
#     husband_thread = wife_thread = None
#     if husband and husband.get_parentid():
#         husband_thread = threading.Thread(target=depth_fs_pedigree, args=(husband.get_parentid(), tree))
#         husband_thread.start()

#     if wife and wife.get_parentid():
#         wife_thread = threading.Thread(target=depth_fs_pedigree, args=(wife.get_parentid(), tree))
#         wife_thread.start()

#     # Wait for the husband's and wife's parents threads
#     if husband_thread:
#         husband_thread.join()
#     if wife_thread:
#         wife_thread.join()