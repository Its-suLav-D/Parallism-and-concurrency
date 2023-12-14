"""
Course: CSE 251 
Lesson: L05 Prove
File:   prove.py
Author: Sulove Dahal

Purpose: Assignment 05 - Factories and Dealers

Instructions:

- Read the comments in the following code.  
- Implement your code where the TODO comments are found.
- No global variables, all data must be passed to the objects.
- Only the included/imported packages are allowed.  
- Thread/process pools are not allowed
- You MUST use a barrier!
- Do not use try...except statements.
- You are not allowed to use the normal Python Queue object. You must use Queue251.
- The shared queue between the threads that are used to hold the Car objects
  can not be greater than MAX_QUEUE_SIZE.
"""

from datetime import datetime, timedelta
import time
import threading
import random

# Include cse 251 common Python files
from cse251 import *

# Global Constants.
MAX_QUEUE_SIZE = 10
SLEEP_REDUCE_FACTOR = 50

# NO GLOBAL VARIABLES!

class Car():
    """ This is the Car class that will be created by the factories """

    # Class Variables
    car_makes = ('Ford', 'Chevrolet', 'Dodge', 'Fiat', 'Volvo', 'Infiniti', 'Jeep', 'Subaru', 
                'Buick', 'Volkswagen', 'Chrysler', 'Smart', 'Nissan', 'Toyota', 'Lexus', 
                'Mitsubishi', 'Mazda', 'Hyundai', 'Kia', 'Acura', 'Honda')

    car_models = ('A1', 'M1', 'XOX', 'XL', 'XLS', 'XLE' ,'Super' ,'Tall' ,'Flat', 'Middle', 'Round',
                'A2', 'M1X', 'SE', 'SXE', 'MM', 'Charger', 'Grand', 'Viper', 'F150', 'Town', 'Ranger',
                'G35', 'Titan', 'M5', 'GX', 'Sport', 'RX')

    car_years = [i for i in range(1990, datetime.now().year)]

    def __init__(self):
        # Make a random car
        self.model = random.choice(Car.car_models)
        self.make = random.choice(Car.car_makes)
        self.year = random.choice(Car.car_years)

        # Sleep a little.  Last statement in this for loop - don't change
        time.sleep(random.random() / (SLEEP_REDUCE_FACTOR))

        # Display the car that has was just created in the terminal
        print(f'Created: {self.info()}')
           
    def info(self):
        """ Helper function to quickly get the car information. """
        return f'{self.make} {self.model}, {self.year}'


class Queue251():
    """ This is the queue object to use for this assignment. Do not modify!! """

    def __init__(self):
        self.items = []
        self.max_size = 0

    def get_max_size(self):
        return self.max_size

    def put(self, item):
        self.items.append(item)
        if len(self.items) > self.max_size:
            self.max_size = len(self.items)

    def get(self):
        return self.items.pop(0)
    
    
class Factory(threading.Thread):
    """ This is a factory.  It will create cars and place them on the car queue """

    def __init__(self, car_queue, queue_slots, queue_items, barrier, production_stats, dealer_count):
        super().__init__()
        self.car_queue = car_queue
        self.queue_slots = queue_slots
        self.queue_items = queue_items
        self.barrier = barrier
        self.production_stats = production_stats
        self.dealer_count = dealer_count
        self.cars_produced = 0

    def run(self):
        self._produce_cars()
        self._update_production_stats()
        self._notify_dealers_if_production_complete()

    def _produce_cars(self):
        production_size = random.randint(200, 300)
        for _ in range(production_size):
            self._create_and_queue_car()

    def _create_and_queue_car(self):
        car = Car()
        self.queue_slots.acquire()
        self.car_queue.put(car)
        self.cars_produced += 1
        self.queue_items.release()

    def _update_production_stats(self):
        self.production_stats.append(self.cars_produced)

    def _notify_dealers_if_production_complete(self):
        self.barrier.wait() # Wait for other factories
        if self.barrier.n_waiting == 0: # All factories have reached the barrier.
            for _ in range(self.dealer_count): # For each dealer, signal that we're done. 
                self.queue_items.release()


class Dealer(threading.Thread):
    """ This is a dealer that receives cars """

    def __init__(self, car_queue, queue_slots, queue_items, dealer_stats, index):
        super().__init__()
        self.car_queue = car_queue
        self.queue_slots = queue_slots
        self.queue_items = queue_items
        self.dealer_stats = dealer_stats
        self.index = index

    def run(self):
        while self._car_available():
            self._sell_car()


    def _car_available(self):
        self.queue_items.acquire()
        if not self.car_queue.items:
            return False
        return True


    def _sell_car(self):
        # We are guaranteed that at this point, there is at least one car in the queue
        self.car_queue.get() 
        self.dealer_stats[self.index] += 1
        self.queue_slots.release()  # Free Slot 

        # Simulate the selling time
        time.sleep(random.random() / (SLEEP_REDUCE_FACTOR + 0))


def run_production(factory_count, dealer_count):
    """Handles the running of factories and dealerships."""

    car_queue, queue_slots, queue_items, production_stats, dealer_stats, factory_barrier = _setup_production_environment(factory_count, dealer_count)

    factories, dealers = _create_factories_and_dealers(factory_count, dealer_count, car_queue, queue_slots, queue_items, production_stats, dealer_stats, factory_barrier)

    _start_and_wait_for_completion(factories, dealers)

    total_cars_produced = sum(production_stats)
    max_queue_size = car_queue.get_max_size()

    return (total_cars_produced, max_queue_size, dealer_stats, production_stats)

def _setup_production_environment(factory_count, dealer_count):

    car_queue = Queue251()

    # Semaphores 
    queue_slots = threading.Semaphore(MAX_QUEUE_SIZE)
    queue_items = threading.Semaphore(0)

    production_stats = []
    dealer_stats = [0] * dealer_count

    factory_barrier = threading.Barrier(factory_count)

    return car_queue, queue_slots, queue_items, production_stats, dealer_stats, factory_barrier

def _create_factories_and_dealers(factory_count, dealer_count, car_queue, queue_slots, queue_items, production_stats, dealer_stats, factory_barrier):

    factories = [
        Factory(car_queue, queue_slots, queue_items, factory_barrier, production_stats, dealer_count)
        for _ in range(factory_count)
    ]

    dealers = [
        Dealer(car_queue, queue_slots, queue_items, dealer_stats, i)
        for i in range(dealer_count)
    ]

    return factories, dealers

def _start_and_wait_for_completion(factories, dealers):

    for dealer in dealers:
        dealer.start()

    for factory in factories:
        factory.start()

    for factory in factories:
        factory.join()

    for dealer in dealers:
        dealer.join()

def main(log):
    """ Main function - DO NOT CHANGE! """

    runs = [(1, 1), (1, 2), (2, 1), (2, 2), (2, 5), (5, 2), (10, 10)]
    for factories, dealerships in runs:
        run_time, max_queue_size, dealer_stats, factory_stats = run_production(factories, dealerships)

        log.write(f'Factories      : {factories}')
        log.write(f'Dealerships    : {dealerships}')
        log.write(f'Run Time       : {run_time:.4f}')
        log.write(f'Max queue size : {max_queue_size}')
        log.write(f'Factory Stats  : Made = {sum(dealer_stats)} @ {factory_stats}')
        log.write(f'Dealer Stats   : Sold = {sum(factory_stats)} @ {dealer_stats}')
        log.write('')

        # The number of cars produces needs to match the cars sold
        assert sum(dealer_stats) == sum(factory_stats)


if __name__ == '__main__':
    log = Log(show_terminal=True)
    main(log)
