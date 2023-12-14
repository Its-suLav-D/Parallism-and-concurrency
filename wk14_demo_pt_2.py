# Level order search:
def breadth_fs_pedigree(family_id, tree):
    # Setup a queue system for level order (breadth first) search.
    family_queue = queue.Queue()
    family_queue.put(family_id)

    # Create a helper function that will process each family and continue in level order (breadth first).
    def _helper(fid):
        pass

    # Traverse the families in level order (breadth first).
    while not family_queue.empty():

        threads = []
        count = 0

        # Limit how many request you make to the server; be nice.
        while count < 20 and not family_queue.empty():
            process_family_id = family_queue.get()
            t = threading.Thread(target=_helper, args=(process_family_id, ))
            t.start()
            threads.append(t)
            count += 1

        # Wait for the current threads to be processed before allowing another batch through; if any.
        for t in threads:
            t.join()