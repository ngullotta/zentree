from enum import IntFlag, auto


class InterfaceStates(IntFlag):
    NOTHING = auto()
    PLAYING = auto()
    SEARCHING = auto()
    FINISHED_SEARCHING = auto()
