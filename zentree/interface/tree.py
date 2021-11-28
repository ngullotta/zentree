from pathlib import Path
from random import choice, randint, uniform
from typing import List

from npyscreen import BoxTitle, Pager


class TreeDisplay(Pager):
    grass: str = "~"

    stars: List[str] = ["*", "+", ".", "'"]

    special: List[str] = ["*━━----"]

    extras: List[str] = [
        """
                 '
            *          .
                   *       '
              *                *
        """,
        """
   *   '*
           *
                *
                       *
               *
                     *
        """,
        """
         .                      .
         .                      ;
         :                  - --+- -
         !           .          !
         |        .             .
         |_         +
      ,  | `.
--- --+-<#>-+- ---  --  -
      `._|_,'
         T
         |
         !
         :         . :
         .       *
        """,
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.specials = []
        with open(Path("./trees/basic.txt")) as fp:
            self.values = fp.read().split("\n")

    @property
    def age(self) -> int:
        return 0

    @age.setter
    def age(self, value: int) -> int:
        return self.age

    @staticmethod
    def chance(percent: float) -> bool:
        return (uniform(0, 1) * 100) > (100 - percent)

    def superImposeTree(self) -> None:
        pass

    def zhuzhItUp(self) -> None:
        if len(self.specials) < 5:
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
                        (idx, [start, start + len(special), "R"], cs)
                    )

        for row, coords, original in self.specials:
            start, end = coords[0], coords[1]
            string: str = self.values[row]
            decomposed = list(string)
            if start > 0:
                decomposed[start - 1 : end - 1] = decomposed[start:end]
            else:
                decomposed[0] = original[0]
            decomposed[end] = original[end]

            coords[0] -= 1
            coords[1] -= 1
            self.values[row] = "".join(decomposed)

            if start < 0 and end < 0:
                try:
                    idx = self.specials.index((row, coords, original))
                    del self.specials[idx]
                except (ValueError):
                    pass

    def generateBackground(self):
        for i, row in enumerate(self.values):
            chars = list(row)
            for j, c in enumerate(chars):
                if c == " ":
                    if self.chance(2.5):
                        star: str = choice(self.stars)
                        chars[j : j + len(star)] = list(star)
                    continue
                chars[j] = " "
            self.values[i] = "".join(chars)

    def reset(self):
        self.anchorBottom()
        self.centerValues()
        self.generateBackground()
        self.zhuzhItUp()
        self.addGrass()

    def addGrass(self):
        self.values[-1] = self.grass * self.width

    def centerValues(self):
        self.values = [line.center(self.width - 1) for line in self.values]

    def anchorBottom(self):
        for _ in range(self.height - len(self.values)):
            self.values.insert(0, " ")


class Arboretum(BoxTitle):
    _contained_widget = TreeDisplay

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def resize(self):
        self.entry_widget.width = self.width - 3
        self.entry_widget.height = self.height - 2
        self.entry_widget.reset()
        return super().resize()
