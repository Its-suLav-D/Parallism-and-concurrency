"""
Course: CSE 251 
Lesson: L09 Prove Part 2
File:   prove_part_2.py
Author: Sulove Dahal

Purpose: Part 2 of prove 9, finding the path to the end of a maze using recursion.

Instructions:
- Do not create classes for this assignment, just functions.
- Do not use any other Python modules other than the ones included.
- You MUST use recursive threading to find the end of the maze.
- Each thread MUST have a different color than the previous thread:
    - Use get_color() to get the color for each thread; you will eventually have duplicated colors.
    - Keep using the same color for each branch that a thread is exploring.
    - When you hit an intersection spin off new threads for each option and give them their own colors.

This code is not interested in tracking the path to the end position. Once you have completed this
program however, describe how you could alter the program to display the found path to the exit
position:

What would be your strategy?

My strategy would be to use a shared dictionary to track the paths of each thread. As threads explore the maze, they would add their current position to a list in this dictionary. When a thread finds the end, we would use its path from the dictionary for display.

Why would it work?

This approach is effective because it allows threads to record their paths in real-time without interrupting their search process. Once the end is found, the successful path is already available in the dictionary, making it straightforward to retrieve and display.

"""

import math
import threading 
from screen import Screen
from maze import Maze
import sys
import cv2

# Include cse 251 files
from cse251 import *

SCREEN_SIZE = 700
COLOR = (0, 0, 255)
COLORS = (
    (0,0,255),
    (0,255,0),
    (255,0,0),
    (255,255,0),
    (0,255,255),
    (255,0,255),
    (128,0,0),
    (128,128,0),
    (0,128,0),
    (128,0,128),
    (0,128,128),
    (0,0,128),
    (72,61,139),
    (143,143,188),
    (226,138,43),
    (128,114,250)
)
SLOW_SPEED = 100
FAST_SPEED = 0

# Globals
current_color_index = 0
thread_count = 0
stop = False
speed = SLOW_SPEED

def get_color():
    """ Returns a different color when called """
    global current_color_index
    if current_color_index >= len(COLORS):
        current_color_index = 0
    color = COLORS[current_color_index]
    current_color_index += 1
    return color

def is_end_position(maze, row, col):
    """Check if the current position is the end of the maze."""
    return maze.at_end(row, col)

def mark_position(maze, row, col, color):
    """Mark the current position on the maze."""
    maze.move(row, col, color)

def create_threads_for_forks(maze, moves, current_color):
    """Create new threads for each forked path except one."""
    for next_row, next_col in moves[:-1]:
        new_color = get_color()
        threading.Thread(target=explore_maze, args=(maze, next_row, next_col, new_color)).start()

def explore_maze(maze, row, col, color):
    global stop

    if stop or not maze.can_move_here(row, col):
        return

    mark_position(maze, row, col, color)

    if is_end_position(maze, row, col):
        stop = True
        return

    moves = maze.get_possible_moves(row, col)
    if len(moves) > 1:
        create_threads_for_forks(maze, moves, color)
        next_row, next_col = moves[-1]
    elif moves:
        next_row, next_col = moves[0]
    else:
        return

    explore_maze(maze, next_row, next_col, color)

def solve_find_end(maze):
    global stop
    stop = False
    start_row, start_col = maze.get_start_pos()
    initial_color = get_color()
    explore_maze(maze, start_row, start_col, initial_color)



def find_end(log, filename, delay):
    """ Do not change this function """

    global thread_count
    global speed

    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename, delay=delay)

    solve_find_end(maze)

    log.write(f'Number of drawing commands = {screen.get_command_count()}')
    log.write(f'Number of threads created  = {thread_count}')

    done = False
    while not done:
        if screen.play_commands(speed): 
            key = cv2.waitKey(0)
            if key == ord('1'):
                speed = SLOW_SPEED
            elif key == ord('2'):
                speed = FAST_SPEED
            elif key == ord('q'):
                exit()
            elif key != ord('p'):
                done = True
        else:
            done = True


def find_ends(log):
    """ Do not change this function """

    files = (
        'very-small.bmp',
        'very-small-loops.bmp',
        'small.bmp',
        'small-loops.bmp',
        'small-odd.bmp',
        'small-open.bmp',
        'large.bmp',
        'large-loops.bmp',
        # 'large-squares.bmp',
        # 'large-open.bmp'
    )

    log.write('*' * 40)
    log.write('Part 2')
    for filename in files:
        filename = f'./mazes/{filename}'
        log.write()
        log.write(f'File: {filename}')
        find_end(log, filename,0.01)
        # log.write(f'Found path has length     = {len(path)}')
    log.write('*' * 40)


def main():
    """ Do not change this function """
    sys.setrecursionlimit(5000)
    log = Log(show_terminal=True)
    find_ends(log)


if __name__ == "__main__":
    main()




# paths = {}

# def explore_maze_memoized(maze, row, col, color, thread_id=0):
#     global stop, paths

#   
#     if stop:
#         return

#     if not maze.can_move_here(row, col):
#         return

#     
#     if thread_id not in paths:
#         paths[thread_id] = []
#     paths[thread_id].append((row, col))

#     # Mark the current position
#     maze.move(row, col, color)

#     if maze.at_end(row, col):
#        
#         maze.move(row, col, color)  # Mark the end position
#         stop = True
#       
#         display_path(maze, paths[thread_id], color)
#         return

#     
#     moves = maze.get_possible_moves(row, col)

#     if len(moves) > 1:
#       
#         for next_row, next_col in moves[:-1]:
#             new_color = get_color()
#             new_thread_id = len(paths)  
#             threading.Thread(target=explore_maze_memoized, args=(maze, next_row, next_col, new_color, new_thread_id)).start()

#       
#         next_row, next_col = moves[-1]
#         explore_maze_memoized(maze, next_row, next_col, color, thread_id)
#     elif moves:
#         # Only one path, continue
#         next_row, next_col = moves[0]
#         explore_maze_memoized(maze, next_row, next_col, color, thread_id)

# def display_path(maze, path, color):
#     for row, col in path:
#         maze.move(row, col, color)  # Use a distinct color to display the path

