"""
Course: CSE 251 
Lesson: L04 Prove
File:   prove.py
Author: Sulove Dahal

Purpose: Assignment 04 - Factory and Dealership

Instructions:

- Complete the assignments TODO sections and DO NOT edit parts you were told to leave alone.
- Review the full instructions in Canvas; there are a lot of DO NOTS in this lesson.
"""

import time
import threading
import random

# Include cse 251 common Python files
from cse251 import *

# Global Constants - DO NOT CHANGE
CARS_TO_PRODUCE = 500
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
           
    def info(self):
        """ Helper function to quickly get the car information. """
        return f'{self.make} {self.model}, {self.year}'


class Queue251():
    """ This is the queue object to use for this assignment. Do not modify!! """

    def __init__(self):
        self.items = []

    def size(self):
        return len(self.items)

    def put(self, item):
        assert len(self.items) <= 10
        self.items.append(item)

    def get(self):
        return self.items.pop(0)


class Factory(threading.Thread):
    """ This is a factory.  It will create cars and place them on the car queue """
    def __init__(self, queue, can_produce, can_consume, log):
        super().__init__()
        self.queue = queue
        self.can_produce = can_produce
        self.can_consume = can_consume
        self.log = log

    def run(self):
        for _ in range(CARS_TO_PRODUCE):
            self.produce_car()

        self.notify_no_more_cars()

    def produce_car(self):
        self.can_produce.acquire()
        car = Car()
        self.queue.put(car)
        self.log_car_production(car)
        self.can_consume.release()

    def log_car_production(self, car):
        self.log.write(f"Created: {car.info()} - Queue Size: {self.queue.size()}")

    def notify_no_more_cars(self):
        self.can_consume.release()


class Dealer(threading.Thread):
    """ This is a dealer that receives cars """
    def __init__(self, queue, can_produce, can_consume, queue_stats, log):
        super().__init__()
        self.queue = queue
        self.can_produce = can_produce
        self.can_consume = can_consume
        self.queue_stats = queue_stats
        self.log = log
        self.cars_sold_per_queue_size = [[] for _ in range(MAX_QUEUE_SIZE)]

    def run(self):
        self.process_cars_until_none_left()
        self.log_all_sold_cars()

    def process_cars_until_none_left(self):
        while True:
            self.can_consume.acquire()
            if self.queue_is_empty():
                break
            self.sell_car()
            self.sleep_after_selling()

    def sell_car(self):
        current_queue_size = self.queue.size()
        car = self.queue.get()
        self.log_sold_car(current_queue_size, car)
        self.queue_stats[current_queue_size - 1] += 1
        self.can_produce.release()

    def log_sold_car(self, queue_size, car):
        self.cars_sold_per_queue_size[queue_size - 1].append(car)

    def queue_is_empty(self):
        return self.queue.size() == 0

    def sleep_after_selling(self):
        time.sleep(random.random() / (SLEEP_REDUCE_FACTOR))

    def log_all_sold_cars(self):
        for i, cars in enumerate(self.cars_sold_per_queue_size):
            if cars:
                self.log.write(f"Queue Size {i + 1}:")
                for car in cars:
                    self.log.write(f"Sold: {car.info()}")
                self.log.write(f"Total: {len(cars)}\n")

def main():
    log = Log(show_terminal=True)

    can_produce = threading.Semaphore(MAX_QUEUE_SIZE)
    can_consume = threading.Semaphore(0)

    car_queue = Queue251()
    queue_stats = [0] * MAX_QUEUE_SIZE

    factory = Factory(car_queue, can_produce, can_consume, log)
    dealer = Dealer(car_queue, can_produce, can_consume, queue_stats, log)

    log.start_timer()

    factory.start()
    dealer.start()

    factory.join()
    dealer.join()
    
    log.stop_timer(f'All {CARS_TO_PRODUCE} cars have been created')

    xaxis = [i for i in range(1, MAX_QUEUE_SIZE + 1)]
    plot = Plots()
    plot.bar(xaxis, queue_stats, title=f'{CARS_TO_PRODUCE} Produced: Count VS Queue Size',
             x_label='Queue Size', y_label='Count', filename='Production count vs queue size.png')


if __name__ == '__main__':
    main()