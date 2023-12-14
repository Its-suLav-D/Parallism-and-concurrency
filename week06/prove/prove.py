"""
Course: CSE 251 
Lesson: L06 Prove
File:   prove.py
Author: Sulove Dahal

Purpose: Processing Plant

Instructions:

- Implement the necessary classes to allow gifts to be created.
"""

import random
import multiprocessing as mp
import os.path
import time
import datetime

# Include cse 251 common Python files - Don't change
from cse251 import *

CONTROL_FILENAME = 'settings.json'
BOXES_FILENAME   = 'boxes.txt'

# Settings constants
MARBLE_COUNT = 'marble-count'
CREATOR_DELAY = 'creator-delay'
NUMBER_OF_MARBLES_IN_A_BAG = 'bag-count'
BAGGER_DELAY = 'bagger-delay'
ASSEMBLER_DELAY = 'assembler-delay'
WRAPPER_DELAY = 'wrapper-delay'

# No Global variables

class Bag():
    """ bag of marbles - Don't change """

    def __init__(self):
        self.items = []

    def add(self, marble):
        self.items.append(marble)

    def get_size(self):
        return len(self.items)

    def __str__(self):
        return str(self.items)

class Gift():
    """ Gift of a large marble and a bag of marbles - Don't change """

    def __init__(self, large_marble, marbles):
        self.large_marble = large_marble
        self.marbles = marbles

    def __str__(self):
        marbles = str(self.marbles)
        marbles = marbles.replace("'", "")
        return f'Created - {datetime.now().time() }: Large marble: {self.large_marble}, marbles: {marbles[1:-1]}'


class Marble_Creator(mp.Process):
    """ This class "creates" marbles and sends them to the bagger """

    colors = ('Gold', 'Orange Peel', 'Purple Plum', 'Blue', 'Neon Silver', 
        'Tuscan Brown', 'La Salle Green', 'Spanish Orange', 'Pale Goldenrod', 'Orange Soda', 
        'Maximum Purple', 'Neon Pink', 'Light Orchid', 'Russian Violet', 'Sheen Green', 
        'Isabelline', 'Ruby', 'Emerald', 'Middle Red Purple', 'Royal Orange', 'Big Dip O’ruby', 
        'Dark Fuchsia', 'Slate Blue', 'Neon Dark Green', 'Sage', 'Pale Taupe', 'Silver Pink', 
        'Stop Red', 'Eerie Black', 'Indigo', 'Ivory', 'Granny Smith Apple', 
        'Maximum Blue', 'Pale Cerulean', 'Vegas Gold', 'Mulberry', 'Mango Tango', 
        'Fiery Rose', 'Mode Beige', 'Platinum', 'Lilac Luster', 'Duke Blue', 'Candy Pink', 
        'Maximum Violet', 'Spanish Carmine', 'Antique Brass', 'Pale Plum', 'Dark Moss Green', 
        'Mint Cream', 'Shandy', 'Cotton Candy', 'Beaver', 'Rose Quartz', 'Purple', 
        'Almond', 'Zomp', 'Middle Green Yellow', 'Auburn', 'Chinese Red', 'Cobalt Blue', 
        'Lumber', 'Honeydew', 'Icterine', 'Golden Yellow', 'Silver Chalice', 'Lavender Blue', 
        'Outrageous Orange', 'Spanish Pink', 'Liver Chestnut', 'Mimi Pink', 'Royal Red', 'Arylide Yellow', 
        'Rose Dust', 'Terra Cotta', 'Lemon Lime', 'Bistre Brown', 'Venetian Red', 'Brink Pink', 
        'Russian Green', 'Blue Bell', 'Green', 'Black Coral', 'Thulian Pink', 
        'Safety Yellow', 'White Smoke', 'Pastel Gray', 'Orange Soda', 'Lavender Purple',
        'Brown', 'Gold', 'Blue-Green', 'Antique Bronze', 'Mint Green', 'Royal Blue', 
        'Light Orange', 'Pastel Blue', 'Middle Green')

    def __init__(self, marble_count, creator_delay, bagger_input_pipe):
        mp.Process.__init__(self)
        self.marble_count = marble_count
        self.creator_delay = creator_delay
        self.bagger_input_pipe = bagger_input_pipe

    def run(self):
        for _ in range(self.marble_count):
            marble = random.choice(Marble_Creator.colors)
            self.bagger_input_pipe.send(marble)
            time.sleep(self.creator_delay)
        self.bagger_input_pipe.send(None)




class Bagger(mp.Process):
    """ Receives marbles from the marble creator, then there are enough
        marbles, the bag of marbles are sent to the assembler """
    def __init__(self, bagger_delay, bag_count, assembler_input_pipe, creator_output_pipe):
        mp.Process.__init__(self)
        self.bagger_delay = bagger_delay
        self.bag_count = bag_count
        self.assembler_input_pipe = assembler_input_pipe
        self.creator_output_pipe = creator_output_pipe

    def run(self):
        while True:
            bag = Bag()
            for _ in range(self.bag_count):
                marble = self.creator_output_pipe.recv()
                if marble is None:
                    self.assembler_input_pipe.send(None)
                    return
                bag.add(marble)
            self.assembler_input_pipe.send(bag)
            time.sleep(self.bagger_delay)


class Assembler(mp.Process):
    """ Take the set of marbles and create a gift from them.
        Sends the completed gift to the wrapper """
    marble_names = ('Lucky', 'Spinner', 'Sure Shot', 'Big Joe', 'Winner', '5-Star', 'Hercules', 'Apollo', 'Zeus')

    def __init__(self, assembler_delay, wrapper_input_pipe, bagger_output_pipe):
        mp.Process.__init__(self)
        self.assembler_delay = assembler_delay
        self.wrapper_input_pipe = wrapper_input_pipe
        self.bagger_output_pipe = bagger_output_pipe

    def run(self):
        while True:
            bag = self.bagger_output_pipe.recv()
            if bag is None:
                self.wrapper_input_pipe.send(None)
                return
            large_marble = random.choice(Assembler.marble_names)
            gift = Gift(large_marble, bag)
            self.wrapper_input_pipe.send(gift)
            time.sleep(self.assembler_delay)



class Wrapper(mp.Process):
    """ Takes created gifts and wraps them by placing them in the boxes file """

    def __init__(self, wrapper_delay, assembler_output_pipe, gift_count):
        mp.Process.__init__(self)
        self.wrapper_delay = wrapper_delay
        self.assembler_output_pipe = assembler_output_pipe
        self.gift_count = gift_count

    def run(self):
        with open(BOXES_FILENAME, 'w') as file:
            while True:
                gift = self.assembler_output_pipe.recv()
                if gift is None:
                    return
                file.write(str(gift) + '\n')
                
                self.gift_count.value += 1
                
                time.sleep(self.wrapper_delay)



def display_final_boxes(filename, log):
    """ Display the final boxes file to the log file -  Don't change """
    if os.path.exists(filename):
        log.write(f'Contents of {filename}')
        with open(filename) as boxes_file:
            for line in boxes_file:
                log.write(line.strip())
    else:
        log.write_error(f'The file {filename} doesn\'t exist.  No boxes were created.')


def setup_pipes():
    """Create and return the necessary pipes for inter-process communication."""
    creator_to_bagger, bagger_from_creator = mp.Pipe()
    bagger_to_assembler, assembler_from_bagger = mp.Pipe()
    assembler_to_wrapper, wrapper_from_assembler = mp.Pipe()
    return creator_to_bagger, bagger_from_creator, bagger_to_assembler, assembler_from_bagger, assembler_to_wrapper, wrapper_from_assembler

def delete_existing_boxes_file():
    """Delete the boxes file if it exists."""
    if os.path.exists(BOXES_FILENAME):
        os.remove(BOXES_FILENAME)

def create_and_start_processes(settings, pipes, gift_counter):
    """Create and start all necessary processes."""
    creator_to_bagger, bagger_from_creator, bagger_to_assembler, assembler_from_bagger, assembler_to_wrapper, wrapper_from_assembler = pipes

    creator = Marble_Creator(settings[MARBLE_COUNT], settings[CREATOR_DELAY], creator_to_bagger)
    bagger = Bagger(settings[BAGGER_DELAY], settings[NUMBER_OF_MARBLES_IN_A_BAG], bagger_to_assembler, bagger_from_creator)
    assembler = Assembler(settings[ASSEMBLER_DELAY], assembler_to_wrapper, assembler_from_bagger)
    wrapper = Wrapper(settings[WRAPPER_DELAY], wrapper_from_assembler, gift_counter)

    for process in [creator, bagger, assembler, wrapper]:
        process.start()

    return creator, bagger, assembler, wrapper



def main():
    """ Main function """

    log = Log(show_terminal=True)

    log.start_timer()

    # Load settings file
    settings = load_json_file(CONTROL_FILENAME)
    if settings == {}:
        log.write_error(f'Problem reading in settings file: {CONTROL_FILENAME}')
        return

    log.write(f'Marble count     = {settings[MARBLE_COUNT]}')
    log.write(f'Marble delay     = {settings[CREATOR_DELAY]}')
    log.write(f'Marbles in a bag = {settings[NUMBER_OF_MARBLES_IN_A_BAG]}') 
    log.write(f'Bagger delay     = {settings[BAGGER_DELAY]}')
    log.write(f'Assembler delay  = {settings[ASSEMBLER_DELAY]}')
    log.write(f'Wrapper delay    = {settings[WRAPPER_DELAY]}')

    pipes = setup_pipes()

    gift_count = mp.Value('i', 0)  

    delete_existing_boxes_file()

    log.write('Create the processes')

    log.write('Creating and starting processes.')
    processes = create_and_start_processes(settings, pipes, gift_count)

    log.write('Waiting for processes to finish.')

    for process in processes:
        process.join()


    display_final_boxes(BOXES_FILENAME, log)
    

    log.write(f"Total gifts created: {gift_count.value}")





if __name__ == '__main__':
    main()