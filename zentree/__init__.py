import curses
import numpy as np
from functools import reduce
import copy
from random import choice, randint, uniform

from pathlib import Path

class Screen:
    grass: str = "~"

    stars = ["*", "+", ".", "'"]

    special = ["*━━----"]
    def __init__(self) -> None:
        self.stdscr = None
        self.rows, self.cols = 0, 0
        self.layers = []
        self.age = 0
    
    @staticmethod
    def chance(percent: float) -> bool:
        return (uniform(0, 1) * 100) > (100 - percent)

    def make_background_layer(self, stars: bool = True) -> np.ndarray:
        output = np.array(
            [
                [' ' for i in range(self.cols)] 
                for i in range(self.rows)
            ]
        )

        for row in output:
            for i in range(0, len(row)):
                if self.chance(2.5):
                    row[i] = choice(self.stars)

        return output


    def make_tree_layer(self, height: int = 1) -> np.ndarray:
        cr, cc = self.rows // 2, self.cols // 2

        # Initialize array to empty
        output = np.array(
            [
                [' ' for i in range(self.cols)] 
                for i in range(self.rows)
            ]
        )

        with open(Path(f"./trees/p{height}.txt")) as fp:
            treelines = fp.read().split("\n")
            row = len(output) - 1
            for i, line in enumerate(treelines[::-1]):
                if not line:
                    continue
                beginning = cc - (len(line) // 2)
                for j, c in enumerate(line):
                    output[row][beginning + j] = c
                row -= 1
        return output

    def initialize_layers(self):
        for layer in [
            self.make_background_layer(),
            self.make_tree_layer(self.age)
        ]:
            self.layers.append(layer)

    def start(self) -> None:
        self.stdscr = curses.initscr()
        self.rows, self.cols = self.stdscr.getmaxyx()

        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        self.initialize_layers()

        while True:
            # Tree layer
            self.layers[1] = self.make_tree_layer(self.age)
            blit = copy.deepcopy(self.layers[0])
            for layer in self.layers[1:]:
                blit = np.where(layer != ' ', layer, blit)
            for i in range(self.rows):
                for j in range(self.cols - 1):
                    try:
                        char = ord(blit[i][j])
                    except TypeError:
                        char = ord(' ')
                    self.stdscr.addch(i, j, char)
            c = self.stdscr.getch()
            if c == ord('q'):
                break  # Exit the while loop
            elif c == ord(' '):
                if self.age < 9:
                    self.age += 1
                else:
                    self.age = 0

    def stop(self) -> None:
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()