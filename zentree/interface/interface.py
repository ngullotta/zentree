from npyscreen import NPSAppManaged
from zentree.interface.player import Player


class Zentree(NPSAppManaged):
    __interface_map: dict = {"main": Player}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state: int = 0

    def set_flag(self, flag: int, yn: bool = True) -> bool:
        if yn:
            if not self.state & flag:
                self.state |= flag
                return self.has_flag(flag)
        else:
            if self.state & flag:
                self.state &= ~flag
                return not self.has_flag(flag)
        return False

    def has_flag(self, flag: int) -> bool:
        return bool(self.state & flag)

    def onStart(self) -> None:
        for name, interface in self.__interface_map.items():
            self.addForm(name.upper(), interface)
