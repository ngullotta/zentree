from npyscreen import NPSAppManaged
from zentree.interface.player import Player
from zentree.interface.states import InterfaceStates


class Interface(NPSAppManaged):
    __interface_map = {"MAIN": Player}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = 0

    def set_flag(self, flag, yn: bool = True) -> bool:
        if yn:
            if not self.state & flag:
                self.state |= flag
                return True
        else:
            if self.state & flag:
                self.state &= ~flag
                return True
        return False

    def has_flag(self, flag) -> bool:
        return bool(self.state & flag)

    def set_nothing(self, yn: bool = True) -> bool:
        return self.set_flag(InterfaceStates.NOTHING, yn)

    def set_playing(self, yn: bool = True) -> bool:
        return self.set_flag(InterfaceStates.PLAYING, yn)

    def set_searching(self, yn: bool = True) -> bool:
        return self.set_flag(InterfaceStates.SEARCHING, yn)

    def set_finished_searching(self, yn: bool = True) -> bool:
        return self.set_flag(InterfaceStates.FINISHED_SEARCHING, yn)

    def get_finished_searching(self) -> bool:
        return self.has_flag(InterfaceStates.FINISHED_SEARCHING)

    def get_nothing(self) -> bool:
        return self.has_flag(InterfaceStates.NOTHING)

    def get_playing(self) -> bool:
        return self.has_flag(InterfaceStates.PLAYING)

    def get_searching(self) -> bool:
        return self.has_flag(InterfaceStates.SEARCHING)

    def onStart(self):
        for name, interface in self.__interface_map.items():
            self.addForm(name.upper(), interface)
