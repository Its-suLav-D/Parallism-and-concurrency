"""
Course: CSE 251 
Lesson: L09 Prove Part 1
File:   prove_part_1.py
Author: Sulove Dahal

Purpose: Part 1 of prove 9, finding the path to the end of a maze using recursion.

Instructions:

- Do not create classes for this assignment, just functions.
- Do not use any other Python modules other than the ones included.
- Complete any TODO comments.
"""

import math
from screen import Screen
from maze import Maze
import cv2
import sys

# Include cse 251 files
from cse251 import *

SCREEN_SIZE = 800
COLOR = (0, 0, 255)
SLOW_SPEED = 100
FAST_SPEED = 1
speed = SLOW_SPEED

def is_end_of_maze(maze, row, col):
    """Check if the current position is the end of the maze."""
    return maze.at_end(row, col)

def mark_path(maze, row, col, color):
    """Mark the current position with the specified color."""
    maze.move(row, col, color)

def mark_visited(maze, row, col):
    """Mark the current position as visited."""
    maze.restore(row, col)

def explore_moves(maze, current_row, current_col):
    """Explore all possible moves from the current position."""
    for next_row, next_col in maze.get_possible_moves(current_row, current_col):
        if maze.can_move_here(next_row, next_col):
            # Recursively solve the maze from the next position
            path = solve_path(maze, next_row, next_col)
            if path:
                # Path found, return it with the current position included
                return [(current_row, current_col)] + path
    return None

def solve_path(maze, row=None, col=None):
    """Solve the maze recursively to find a path from start to end."""

    if row is None and col is None:
        row, col = maze.get_start_pos()

    if is_end_of_maze(maze, row, col):
        mark_path(maze, row, col, COLOR)
        return [(row, col)]

    if not maze.can_move_here(row, col):
        return []

    mark_path(maze, row, col, COLOR)

    path = explore_moves(maze, row, col)
    if path:
        return path

    mark_visited(maze, row, col)
    return []



def get_path(log, filename):
    """ Do not change this function """
    # 'Maze: Press "q" to quit, "1" slow drawing, "2" faster drawing, "p" to play again'
    global speed

    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename)

    path = solve_path(maze)

    log.write(f'Drawing commands to solve = {screen.get_command_count()}')

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

    return path


def find_paths(log):
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
    log.write('Part 1')
    for filename in files:
        filename = f'./mazes/{filename}'
        log.write()
        log.write(f'File: {filename}')
        path = get_path(log, filename)
        log.write(f'Found path has length     = {len(path)}')
    log.write('*' * 40)


def main():
    """ Do not change this function """
    sys.setrecursionlimit(5000)
    log = Log(show_terminal=True)
    find_paths(log)


if __name__ == "__main__":
    main()