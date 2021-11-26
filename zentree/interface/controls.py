from curses import KEY_SLEFT, KEY_SRIGHT
from typing import Any

from npyscreen import BoxTitle, SimpleGrid, Slider


class VolumeSlider(Slider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_handlers(
            {
                "=": self.h_increase,
                "_": self.h_decrease,
                KEY_SLEFT: self.h_decrease,
                KEY_SRIGHT: self.h_increase,
            }
        )

    def h_decrease(self, inp):
        if self.parent.player.volume <= 0:
            return
        if inp == KEY_SLEFT or chr(inp) == "_":
            self.parent.player.volume -= self.step * 10
        else:
            self.parent.player.volume -= self.step
        self.value = self.parent.player.volume

    def h_increase(self, inp):
        if self.parent.player.volume >= 100:
            return
        if inp == KEY_SRIGHT or chr(inp) == "+":
            self.parent.player.volume += self.step * 10
        else:
            self.parent.player.volume += self.step
        self.value = self.parent.player.volume


class TransportControl(SimpleGrid):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.activecontrols = ["⏮", "⏸", "⏭", "🔀"]
        self.idlecontrols = ["⏮", "▶", "⏭", "🔀"]
        self.set_grid_values_from_flat_list(self.idlecontrols)
        self.add_handlers({" ": self.h_control})
        self._control_func_map = {
            "⏮": self.rewind,
            "⏸": self.pause,
            "▶": self.play,
            "⏭": self.skip,
            "🔀": self.shuffle,
        }

    def onParentRealized(self) -> None:
        self.parent.player.observe_property(
            "core-idle", self.toggle_play_pause_icon
        )

    @property
    def current_value(self):
        row = self.selected_row()
        idx = self.edit_cell[1]
        return row[idx]

    def toggle_play_pause_icon(self, _: Any, value: bool) -> None:
        self.set_grid_values_from_flat_list(
            self.idlecontrols if value else self.activecontrols,
            reset_cursor=False,
        )

    def rewind(self) -> None:
        if self.parent.current_pos > 4:
            self.parent.player.playlist_prev(mode="force")
            return
        self.parent.player.seek(-self.parent.current_pos)

    def pause(self) -> None:
        self.parent.player.pause = True

    def play(self) -> None:
        self.parent.player.pause = False

    def skip(self) -> None:
        self.parent.player.playlist_next(mode="force")

    def shuffle(self) -> None:
        self.parent.player.playlist_shuffle()
        self.skip()

    def h_control(self, _input: int) -> None:
        func = self._control_func_map.get(self.current_value, lambda: None)
        return func()


class TransportBox(BoxTitle):
    _contained_widget = TransportControl

    def onParentRealized(self) -> None:
        callback = getattr(self.entry_widget, "onParentRealized", None)
        if callback is not None:
            callback()


class VolumeBox(BoxTitle):
    _contained_widget = VolumeSlider

    def onParentRealized(self) -> None:
        callback = getattr(self.entry_widget, "onParentRealized", None)
        if callback is not None:
            callback()
