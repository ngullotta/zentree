from enum import IntEnum, auto
from math import ceil
from pathlib import Path
from random import choice, randint, uniform
from typing import Any, List, TypeVar

from npyscreen import BoxTitle, Pager
from npyscreen.wgwidget import Widget


class Direction(IntEnum):
    RIGHT = auto()
    LEFT = auto()


AB = TypeVar("AB", bound="Arboretum")


class Arboretum(Pager):
    grass: str = "~"

    stars: List[str] = ["*", "+", ".", "'"]

    special: List[str] = ["*━━----"]

    def __init__(self: AB, screen: Any, **kwargs: dict[str, Any]) -> None:
        super().__init__(screen, **kwargs)
        self.specials = []
        self._age = 0
        self.tree = []
        self.counter = 0
        self.tree_type = "p1"

    @property
    def age(self: AB) -> int:
        return self._age

    @age.setter
    def age(self: AB, value: int) -> int:
        self._age = value
        self.tree_type = f"p{self.clamp(ceil(self._age/5), 1, 9)}"
        self.reset()
        return self.age

    @staticmethod
    def chance(percent: float) -> bool:
        return (uniform(0, 1) * 100) > (100 - percent)

    @staticmethod
    def clamp(value: int, lower: int, upper: int) -> int:
        return max(lower, min(value, upper))

    def superImposeTree(self: AB) -> None:
        if len(self.tree) == 0:
            with open(Path(f"./trees/{self.tree_type}.txt")) as fp:
                self.tree = fp.read().split("\n")

        tcopy = self.tree.copy()
        for i in range(len(self.values) - 1, -1, -1):
            try:
                line: str = tcopy[-1]
            except (IndexError):
                continue
            new: List[str] = []
            for bc, tc in zip(
                list(self.values[i]), list(line.center(self.width - 1))
            ):
                new.append(bc)
                if tc != " ":
                    new[-1] = tc
            del tcopy[-1]
            self.values[i] = "".join(new)

    def advanceSpecials(self: AB) -> None:
        # Special objects specify which row it's in, it's start and end
        # coordinates, the original string value, and the special
        # character set. @ToDo: This should be a class
        for row, coords, original, special in self.specials:
            # The actual "row" in the pager
            #     [[a b c d e f g]
            # --> [h i j k l m n]
            #     [o p q r s t u]]
            string: str = self.values[row]

            # Start and ends guaranteed to be 0 <= x <= len(string)
            # even if the actual coordinates have gone into the
            # negatives.
            start: int = self.clamp(coords[0], 0, len(string))
            end: int = self.clamp(coords[1], 0, len(string))

            # First we decompose this string into a list of chars
            decomposed: List[str] = list(string)

            # Shift special objects down the list by one and then set
            # the end char back to the original string's char
            if start > 0:
                decomposed[start - 1 : end] = list(special)
                decomposed[end] = original[end]
            # Shift the special object down in sequential order by
            # inversing end start coordinate and then setting end char
            # back to the original end char
            elif end > 0:
                decomposed[0:end] = list(special)[-end:]
                decomposed[end] = original[end]
            # We're done here, this shouldn't be rendered anymore,
            # delete it and move on
            elif start == 0 and end == 0:
                decomposed = list(original)
                idx: int = self.specials.index(
                    (row, coords, original, special)
                )
                del self.specials[idx]
                self.counter += 1

            # Decrement coordinates
            coords[0] -= 1
            coords[1] -= 1

            # Re-join decomposed values back to a string
            self.values[row] = "".join(decomposed)

    def generateSpecialObjects(self: AB) -> None:
        self.advanceSpecials()
        self.superImposeTree()

        if len(self.specials) >= len(self.values[0:-1]):
            return

        if self.chance(5):
            special: str = choice(self.special)

            s: str = choice(self.values[0:-1])
            cs = str(s)
            idx = self.values.index(s)

            for row, _, __, ___ in self.specials:
                if row == idx:
                    return

            start = randint(0, self.width - (len(special) + 1))
            new = list(s)
            new[start : start + len(special)] = list(special)
            self.values[idx] = "".join(new)

            self.specials.append(
                (
                    idx,
                    [start, (start + len(special) - 1), Direction.RIGHT],
                    cs,
                    special,
                )
            )

        self.superImposeTree()

    def generateBackground(self: AB) -> None:
        for i, row in enumerate(self.values):
            chars: list[str] = list(row)
            for j, c in enumerate(chars):
                if c == " ":
                    if self.chance(2.5):
                        star: str = choice(self.stars)
                        chars[j : j + len(star)] = list(star)
                    continue
            self.values[i] = "".join(chars)

    def reset(self: AB) -> None:
        self.values = []
        self.tree = []
        self.anchorBottom()
        self.centerValues()
        self.generateBackground()
        for row, _, original, __ in self.specials:
            self.values[row] = original
        self.specials = []
        self.generateSpecialObjects()
        self.superImposeTree()
        self.addGrass()

    def addGrass(self: AB) -> None:
        self.values[-1] = self.grass * self.width

    def centerValues(self: AB) -> None:
        self.values = [line.center(self.width - 1) for line in self.values]

    def anchorBottom(self: AB) -> None:
        for _ in range(self.height - len(self.values)):
            self.values.insert(0, " ")


ABB = TypeVar("ABB", bound="ArboretumBox")


class ArboretumBox(BoxTitle):
    _contained_widget: Widget = Arboretum

    def update(self: ABB, clear: bool = True) -> None:
        self.name: str = f"Arboretum: Age [{self.entry_widget.age}]"
        return super().update(clear=clear)

    def resize(self: ABB) -> None:
        self.entry_widget.width = self.width - 3
        self.entry_widget.height = self.height - 2
        self.entry_widget.reset()
        return super().resize()
