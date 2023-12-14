"""
Course: CSE 251 
Lesson: L02 Prove
File:   prove.py
Author: Sulove Dahal

Purpose: Retrieve Star Wars details from a server

Instructions:

- Each API call must only retrieve one piece of information
- You are not allowed to use any other modules/packages except for the ones used
  in this assignment.
- Run the server.py program from a terminal/console program.  Simply type
  "python server.py"
- The only "fixed" or hard coded URL that you can use is TOP_API_URL.  Use this
  URL to retrieve other URLs that you can use to retrieve information from the
  server.
- You need to match the output outlined in the description of the assignment.
  Note that the names are sorted.
- You are required to use a threaded class (inherited from threading.Thread) for
  this assignment.  This object will make the API calls to the server. You can
  define your class within this Python file (ie., no need to have a separate
  file for the class)
- Do not add any global variables except for the ones included in this program.

The call to TOP_API_URL will return the following Dictionary(JSON).  Do NOT have
this dictionary hard coded - use the API call to get this.  Then you can use
this dictionary to make other API calls for data.

{
   "people": "http://127.0.0.1:8790/people/", 
   "planets": "http://127.0.0.1:8790/planets/", 
   "films": "http://127.0.0.1:8790/films/",
   "species": "http://127.0.0.1:8790/species/", 
   "vehicles": "http://127.0.0.1:8790/vehicles/", 
   "starships": "http://127.0.0.1:8790/starships/"
}
"""

from datetime import datetime, timedelta
import requests
import json
import threading
from abc import ABC, abstractmethod

# Include cse 251 common Python files
from cse251 import *

# Const Values
TOP_API_URL = 'http://127.0.0.1:8790'

# Global Variables
call_count = 0


# Just wanted to practice DESIGN PATTERNS and SOLID Principles -- I know it's overkill
class SortingStrategy(ABC):
    @abstractmethod
    def sort(self, data):
        pass

class AlphabeticalSortStrategy(SortingStrategy):

    def sort(self, data):
        return sorted(data)


class SingleApiCallThread(threading.Thread):
    def __init__(self, url, api_fetcher, url_key):
        super().__init__()
        self.url = url
        self.api_fetcher = api_fetcher
        self.url_key = url_key 
        self.data = None

    def run(self):
        self.data = self.api_fetcher.fetch(self.url).get('name', '')


class APIFetcher:
    def __init__(self, log):
        self.log = log
        # self.semaphore = semaphore

    def fetch(self, url):
        response = requests.get(url)
        global call_count
        call_count +=1

        return response.json()

class Executor:
    def __init__(self, log,sorting_strategy=SortingStrategy):
        self.log = log
        # self.semaphore = semaphore
        self.sorting_strategy = sorting_strategy

    def execute(self):
        api_fetcher = APIFetcher(self.log)
        top_data = api_fetcher.fetch(TOP_API_URL)
        
        film_url = top_data.get('films') + '6'
        film_data = api_fetcher.fetch(film_url)
        
        self.log_film_detail(film_data)
        
        threads = self.create_and_start_threads(api_fetcher, film_data)
        self.wait_for_threads(threads)
        
        results = self.process_and_organize_results(threads)
        self.log_results(results)

    def log_film_detail(self, film_data):
        labels = [
            "Title",
            "Director",
            "Producer",
            "Released"
        ]
        
        max_label_length = max(len(label) for label in labels)
        
        self.log.write(f"{labels[0].ljust(max_label_length)} : {film_data['title']}")
        self.log.write(f"{labels[1].ljust(max_label_length)} : {film_data['director']}")
        self.log.write(f"{labels[2].ljust(max_label_length)} : {film_data['producer']}")
        self.log.write(f"{labels[3].ljust(max_label_length)} : {film_data['release_date']}")
        self.log.write(" ")


    def create_and_start_threads(self, api_fetcher, film_data):
        threads = []
        for retriever_class_data_key in ['characters', 'planets', 'species', 'vehicles', 'starships']:
            url_key = 'people' if retriever_class_data_key == 'characters' else retriever_class_data_key

            for url in film_data[retriever_class_data_key]:
                thread = SingleApiCallThread(url, api_fetcher, url_key) 
                thread.start()
                threads.append(thread)
        return threads


    def wait_for_threads(self, threads):
        for thread in threads:
            thread.join()

    def process_and_organize_results(self, threads):
        url_key_to_result_key = {
            'people': 'characters',
            'planets': 'planets',
            'species': 'species',
            'vehicles': 'vehicles',
            'starships': 'starships'
        }
        
        results = {'characters': [], 'planets': [], 'species': [], 'vehicles': [], 'starships': []}
        
        for thread in threads:
            result_key = url_key_to_result_key[thread.url_key]  
            results[result_key].append(thread.data)
            
        return results

    
    def log_results(self, results):
        for key, value in results.items():
            sorted_value = self.sorting_strategy.sort(value)
            self.log.write(f"{key.capitalize()}: {len(sorted_value)}")
            self.log.write(', '.join(sorted_value))
            self.log.write('')


def main():
    log = Log(show_terminal=True)
    log.start_timer('Starting to retrieve data from the server')
    log.write("----------------------------------------")

    # semaphore = threading.Semaphore(1)

    sorting_strategy = AlphabeticalSortStrategy()
    executor = Executor(log, sorting_strategy)
    executor.execute() 

    log.stop_timer('Total Time To complete')
    log.write(f'There were {call_count} calls to the server')
    

if __name__ == "__main__":
    main()