import curses
import numpy as np
import copy
import collections
from random import choice, randint, uniform
from pathlib import Path
from typing import List, Any
from time import sleep
from threading import Thread

class LayerView(np.ndarray):
    def roll(
        self,
        direction: int = 1,
        stride: int = 1,
        axis: np.shape = None,
        nowrap: bool = True
    ) -> None:
        # This is the best way I could come up with do this inplace
        # Since ndarray data is basically immutable (outside of direct
        # index access), we can't just roll ourself and supplant the
        # data which would be *far* easier
        new = np.roll(self, direction * stride, axis=axis)
        # One dimensional
        if len(self.shape) == 1:
            for i in range(0, self.shape[0]):
                self[i] = new[i]
            # snip the ends
            if nowrap:
                self[0] = ' '
                self[-1] = ' '
        # Multi dimensional
        else:
            for i in range(0, self.shape[0]):
                for j in range(0, self.shape[1]):
                    self[i][j] = new[i][j]
                # snip the ends
                if nowrap:
                    self[i][0] = ' '
                    self[i][-1] = ' '


class Screen:
    grass: str = "~"

    stars: List[str] = ["*", "+", ".", "'"]

    # specials: List[str] = ["*━━----", ">~~"]
    shooters: List[str] = [
            "*---", 
            "+~~", 
            "<==", 
            "-----", 
            "~~-~~", 
            "=====", 
            "~~", 
            "==", 
            "---"
        ]

    heads: List[str] = ["*", "+"]

    def __init__(self, cycle_time: float = 0.1) -> None:
        self.age: int = 0
        self.stdscr: Any = None
        self.rows: int = 0
        self.cols: int = 0
        self.shape = (0, 0)
        self.layers: List[np.ndarray] = []
        self.layers: dict = {}
        self.cycle_time: float = cycle_time
        self.cycles: int = 0
        self.enabled: bool = True
        self.log_buffer: collections.deque = collections.deque(maxlen=5)

    def blit(self, buffer: np.ndarray):
        for i, row in enumerate(buffer):
            for j, col in enumerate(row):
                try:
                    char = ord(buffer[i][j])
                except TypeError:
                    char = ord(' ')

                # Don't care :^)
                try:
                    self.stdscr.addch(i, j, char)
                except curses.error:
                    pass

    def fill_random(
        self,
        array: np.ndarray,
        choices: List[str],
        chance: float,
        break_first: bool = False
    ) -> None:
        # One dimensional
        if len(array.shape) == 1:
            for i, col in enumerate(array):
                if self.chance(chance):
                    for j, c in enumerate(choice(choices)):
                        if i + j >= array.shape[-1]:
                            continue
                        if i + j < len(array):
                            array[i + j] = c
                    if break_first:
                        break
        # Multi dimensional
        else:
            for i, row in enumerate(array):
                for j, col in enumerate(row):
                    if self.chance(chance):
                        for k, c in enumerate(choice(choices)):
                            if j + k < len(array[i]):
                                array[i][j + k] = c
                        if break_first:
                            break

    def fill(self, name: str) -> None:
        layer = self.layers.get(name)
        if layer is None:
            return
        data = layer["data"]
        center = self.shape[-1] // 2
        match name:
            # Special cases
            case "background":
                self.fill_random(layer["data"], self.stars, 2.5)
            case "shooting-stars" | "shooting-stars-alt":
                self.fill_random(layer["data"], self.shooters, 0.1)
            case "tree":
                path = Path(f"./trees/p{self.age}.txt")
                if not path.exists():
                    return
                with open(path) as fp:
                    treelines = fp.read().split("\n")
                    row = len(layer["data"]) - 1
                    for i, line in enumerate(treelines[::-1]):
                        if not line:
                            continue
                        beginning = center - (len(line) // 2)
                        for j, c in enumerate(line):
                            if beginning + j < len(layer["data"][row]):
                                layer["data"][row][beginning + j] = c
                        row -= 1
            case "cycles":
                label = str(self.cycles)
                pos = center - (len(label) // 2)
                for i, c in enumerate(label):
                    if pos + i < len(layer["data"][0]):
                        layer["data"][0][pos + i] = c
            case "log":
                label = ' '.join(self.log_buffer)
                ypos = center - (len(label) // 2)
                xpos = self.shape[0] // 2
                for i, c in enumerate(label):
                    if ypos + i < len(layer["data"][xpos]):
                        layer["data"][xpos][ypos + i] = c
            case _:
                return

    def new_layer(
        self,
        name: str,
        z_index: int = None,
        roll: bool = False,
        shape: np.shape = None,
        randomize_directions: bool = False,
        fill_value: str = ' ',
        auto_fill: bool = True,
        update_on_tick: bool = False,
        full_refresh_on_tick: bool = False,
        **kwargs # unused
    ) -> np.ndarray:
        shape = shape or self.shape
        z = z_index or len(self.layers)

        # Create a new "layer" and track it
        self.layers[name] = {
            "z-index": z,
            "data": np.full(
                shape=shape,
                fill_value=fill_value
            ).view(LayerView),
            "roll": roll,
            "directionMap": {
                i: choice([-1, 1]) if randomize_directions else 1
                for i in range(0, shape[0])
            },
            "update-on-tick": update_on_tick,
            "full-refresh-on-tick": full_refresh_on_tick
        }

        if auto_fill:
            self.fill(name)

        # Re-sort the layers dict
        self.layers = {
            k: v for k, v in sorted(
                self.layers.items(), key=lambda item: item[1]["z-index"]
            )
        }

        return self.layers[name]

    def tick(self, delta: float) -> None:
        refresh = []
        for name, layer in self.layers.items():
            if layer["roll"]:
                data = layer["data"]
                for i, row in enumerate(layer["data"]):
                    if (row == ' ').all():
                        self.fill_random(row, self.shooters, 0.003)
                        continue
                    row.roll(layer["directionMap"][i])

            if layer["update-on-tick"]:
                self.fill(name)

            # Mark for refresh
            if layer["full-refresh-on-tick"]:
                refresh.append(name)

        # Do the actual refresh
        for name in refresh:
            kwargs = {
                k.replace("-", "_"): v 
                for k, v in self.layers[name].items()
            }
            del self.layers[name]
            self.new_layer(name, **kwargs)

    @staticmethod
    def chance(percent: float) -> bool:
        return (uniform(0, 1) * 100) > (100 - percent)

    def start(self) -> None:
        self.stdscr = curses.initscr()
        curses.curs_set(0)
        self.stdscr.box()
        self.stdscr.refresh()
        self.rows, self.cols = self.stdscr.getmaxyx()
        self.shape = (self.rows, self.cols)
        self.stdscr.nodelay(True)

        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

        self.new_layer("background")
        self.new_layer("shooting-stars", roll=True, randomize_directions=True)
        self.new_layer("tree", full_refresh_on_tick=True)
        self.new_layer("cycles", update_on_tick=True)
        self.new_layer("log", full_refresh_on_tick=True)
    
    def run(self):
        while True:
            # Handle key events
            ch = self.stdscr.getch()
            if ch == ord('q'):
                self.stop()
                break
            elif ch == ord(' '):
                self.enabled = not self.enabled
            elif ch == -1:
                pass
            elif ch == curses.KEY_RESIZE:
                self.stdscr.clear()
                self.layers = {}
                self.start()
            elif ch == ord('='):
                self.cycle_time -= 0.005
                if self.cycle_time <= 0:
                    self.cycle_time = 0.1
                self.log("Cycle time: %f" % self.cycle_time)
            elif ch == ord('-'):
                self.cycle_time += 0.005
                self.log("Cycle time: %f" % self.cycle_time)
            else:
                self.log("Unknown key %s" % chr(ch))

            if not self.enabled:
                continue

            # Handle log events
            if self.cycles % 10 == 0 and len(self.log_buffer) > 0:
                self.log_buffer.pop()
                self.fill("log")

            if self.cycles % 100 == 0:
                self.age += 1
                if self.age >= 9:
                    self.age = 0

            blit = np.full(self.shape, fill_value=' ')
            for name, layer in self.layers.items():
                buffer = layer["data"]
                blit = np.where(buffer != ' ', buffer, blit)

            self.blit(blit)

            self.stdscr.refresh()

            sleep(self.cycle_time)

            self.tick(self.cycle_time)

            self.cycles += 1

    def log(self, message: str):
        self.log_buffer.append(message)

    def stop(self) -> None:
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.curs_set(1)
        
        # No idea why this can fail but I don't care :^)
        try:
            curses.endwin()
        except curses.error:
            pass
