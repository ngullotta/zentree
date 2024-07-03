import curses
import numpy as np
from functools import reduce

from pathlib import Path

class Screen:
    def __init__(self) -> None:
        self.stdscr = None
        self.rows, self.cols = 0, 0
        self.layers = []

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
                start = cc - len(line)
                for c in line:
                    output[row][start] = c
                    start += 1
                row -= 1
        return output

    def initialize_layers(self):
        for layer in [
            np.array([
                    ['-' for i in range(self.cols)] 
                    for i in range(self.rows)
                ]
            ),
            self.make_tree_layer(9)
        ]:
            self.layers.append(layer)

    def start(self) -> None:
        self.stdscr = curses.initscr()
        self.rows, self.cols = self.stdscr.getmaxyx()

        self.initialize_layers()

        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

        while True:
            blit = self.layers[0]
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
            # if c != ord('q'):
                # self.stdscr.addch(c)
            if c == ord('q'):
                break  # Exit the while loop
            elif c == curses.KEY_HOME:
                x = y = 0

    def stop(self) -> None:
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()