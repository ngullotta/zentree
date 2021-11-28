from enum import IntEnum, auto
from pathlib import Path
from random import choice, randint, uniform
from typing import List

from npyscreen import BoxTitle, Pager


class Direction(IntEnum):
    RIGHT = auto()
    LEFT = auto()


class Arboretum(Pager):
    grass: str = "~"

    stars: List[str] = ["*", "+", ".", "'"]

    special: List[str] = ["*━━----"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.specials = []
        self.tree = []

    @property
    def age(self) -> int:
        return 0

    @age.setter
    def age(self, value: int) -> int:
        return self.age

    @staticmethod
    def chance(percent: float) -> bool:
        return (uniform(0, 1) * 100) > (100 - percent)

    @staticmethod
    def clamp(value: int, lower: int, upper: int) -> int:
        return max(lower, min(value, upper))

    def superImposeTree(self, _type: str) -> None:
        if len(self.tree) == 0:
            with open(Path(f"./trees/{_type}.txt")) as fp:
                self.tree = fp.read().split("\n")

        for i, line in enumerate(self.tree):
            new: List[str] = []
            for bc, tc in zip(
                list(self.values[i]), list(line.center(self.width - 1))
            ):
                new.append(bc)
                if tc != " ":
                    new[-1] = tc
            self.values[i] = "".join(new)

    def advanceSpecials(self) -> None:
        # Special objects specify which row it's in, it's start and end
        # coordinates, and the original string value
        for row, coords, original in self.specials:
            # The actual string "row" in the pager
            string: str = self.values[row]

            # Start and ends guaranteed to be 0 <= x <= len(string)
            start: int = self.clamp(coords[0], 0, len(string))
            end: int = self.clamp(coords[1], 0, len(string))

            # This special object is no longer being drawn, delete it
            if start == 0 and end == 0:
                idx: int = self.specials.index((row, coords, original))
                del self.specials[idx]
                continue

            # First we decompose this string into a list of chars
            decomposed: List[str] = list(string)

            # Shift special objects down the list by one and then set
            # the end char back to the original string's char
            if start > 0:
                decomposed[start - 1 : end - 1] = decomposed[start:end]
                decomposed[end] = original[end]
            else:
                decomposed[0] = original[0]
                decomposed[end] = original[end]

            # Decrement coordinates
            coords[0] -= 1
            coords[1] -= 1

            # Re-join decomposed values back to a string
            self.values[row] = "".join(decomposed)

    def generateSpecialObjects(self) -> None:
        self.advanceSpecials()
        self.superImposeTree("basic")

        if len(self.specials) >= 5:
            return

        if self.chance(35):
            special: str = choice(self.special)

            s: str = choice(self.values)
            cs = str(s)
            idx = self.values.index(s)

            no_spawn = False
            if idx + 1 == len(self.values):
                no_spawn = True

            for row, _, __ in self.specials:
                if row == idx:
                    no_spawn = True

            if not no_spawn:
                start = randint(0, self.width - len(special))
                new = list(s)
                new[start : start + len(special)] = list(special)
                self.values[idx] = "".join(new)

                self.specials.append(
                    (
                        idx,
                        [start, (start + len(special) - 1), Direction.RIGHT],
                        cs,
                    )
                )

    def generateBackground(self) -> None:
        for i, row in enumerate(self.values):
            chars: list[str] = list(row)
            for j, c in enumerate(chars):
                if c == " ":
                    if self.chance(2.5):
                        star: str = choice(self.stars)
                        chars[j : j + len(star)] = list(star)
                    continue
            self.values[i] = "".join(chars)

    def reset(self) -> None:
        self.anchorBottom()
        self.centerValues()
        self.generateBackground()
        self.specials = []
        self.generateSpecialObjects()
        self.superImposeTree("basic")
        self.addGrass()

    def addGrass(self) -> None:
        self.values[-1] = self.grass * self.width

    def centerValues(self) -> None:
        self.values = [line.center(self.width - 1) for line in self.values]

    def anchorBottom(self) -> None:
        for _ in range(self.height - len(self.values)):
            self.values.insert(0, " ")


class ArboretumBox(BoxTitle):
    _contained_widget = Arboretum

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def resize(self) -> None:
        self.entry_widget.width = self.width - 3
        self.entry_widget.height = self.height - 2
        self.entry_widget.reset()
        return super().resize()
