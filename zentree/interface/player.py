from datetime import datetime, timedelta
from pathlib import Path
from signal import SIGINT, signal
from threading import Event, Thread
from traceback import StackSummary
from typing import Any, Union

from npyscreen import ButtonPress, TitleMultiSelect, TitleText
from zentree.interface.controls import TransportBox, VolumeBox
from zentree.interface.form import RedrawingForm
from zentree.interface.tree import ArboretumBox
from zentree.players.youtube import YouTubePlayer


class Timer(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stop = Event()

    def run(self):
        while not self.stop.is_set():
            super().run()


class PomodoroTimer(ButtonPress):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time = 0
        self.active_flag: Event = Event()
        self.active_flag.set()
        self.exit_flag: Event = Event()

        self.timer = Timer(target=self.every, args=(1, self.tick))
        self.timer.start()

        self.counter = 0
        self.bt = 0
        self._break = datetime.utcnow()

    def every(self, seconds: int, fn: callable) -> None:
        while not self.exit_flag.wait(timeout=seconds):
            if self.active_flag.is_set():
                try:
                    fn()
                except (Exception):
                    pass

    def pomodoro(self):
        self.counter += 1
        self.name = "Break started"
        self.parent.tree.entry_widget.age = (
            self.parent.tree.entry_widget.age + 1
        )
        if self.counter > 3:
            self.counter = 0
            self.bt = 25
        else:
            self.bt = 10
        self._break = datetime.utcnow() + timedelta(seconds=self.bt * 60)

    def tick(self):
        if self.bt > 0:
            delta = self._break - datetime.utcnow()
            if datetime.utcnow() >= self._break:
                self._break = datetime.utcfromtimestamp(0)
                self.bt = 0
            self.name = f"{timedelta(seconds=delta.seconds)} P={self.counter}"
        else:
            self.time += 1
            self.name = f"{timedelta(seconds=self.time)} P={self.counter}"
            if self.time >= 20 * 60:
                self.time = 0
                self.pomodoro()
        return self.time

    def whenPressed(self):
        if self.timer.stop.is_set():
            self.timer.stop.clear()
            self.active_flag.set()
        else:
            self.timer.stop.set()
            self.active_flag.clear()
            self.time = 0
            self.name = "Start Timer"


class Player(RedrawingForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.name: str = "Player: Not Playing"
        self._current_track: str = "N/A"
        self._current_pos: float = 0.0
        self._playing: bool = False
        self.draw_flag.set()

        YouTubePlayer.locale()
        self.player: YouTubePlayer = YouTubePlayer(
            ytdl=True,
            video=False,
            input_default_bindings=True,
            input_vo_keyboard=True,
            script_opts="ytdl_hook-ytdl_path=yt-dlp",
        )

        for prop, func in [
            ("media-title", self._update_title),
            ("time-pos", self._update_time_pos),
            ("core-idle", self._update_playing),
        ]:
            self.player.observe_property(prop, func)

        self.juj = Thread(
            target=self.every,
            args=(1, self.tree.entry_widget.generateSpecialObjects),
        )
        self.juj.start()

        for sig in [SIGINT]:
            signal(sig, self.shutdown)

        self.onRealized()

    def find_previous_editable(self, *args):
        if (self.editw + 1) == len(self._widgets__):
            self.editw = 0
        return super().find_previous_editable(*args)

    def _update_title(self, _: Any, name: str) -> None:
        self.current_track = name

    def _update_time_pos(self, _: Any, pos: float) -> None:
        self.current_pos = pos or 0.0

    def _update_playing(self, _: Any, value: bool) -> None:
        self._playing = not bool(value)

    @property
    def current_track(self) -> str:
        return self._current_track or "Not Playing"

    @current_track.setter
    def current_track(self, value: Union[str, None]) -> str:
        if self._current_track != value:
            self._current_track = value
        return self.current_track

    @property
    def current_pos(self) -> float:
        return self._current_pos

    @current_pos.setter
    def current_pos(self, value: float) -> float:
        if self._current_pos != value:
            self._current_pos = round(value, 2)
        return self.current_pos

    @property
    def playing(self) -> bool:
        return bool(self._playing)

    @playing.setter
    def playing(self, value: bool) -> bool:
        if self._playing != value:
            self._playing = bool(value)
        return self.playing

    def shutdown(self, signum: int, frame: StackSummary) -> None:
        self.exit_flag.set()
        if self.player.check_core_alive():
            self.player.stop()
            del self.player
        exit()

    def display(self, *args, **kwargs) -> None:
        self.name = self._update_name()
        return super().display(*args, **kwargs)

    def _update_name(self) -> str:
        parts = []
        if not self.player._core_shutdown:
            parts.append("Player:")
            if self.playing:
                parts.append("Now Playing ->")
                parts.append(self.current_track)
                # Buffering
                if self.current_pos < 0:
                    parts.append("[buffering...]")
                else:
                    parts.append(f"[{self.current_pos}]")
            else:
                parts.append("Not Playing")
        else:
            parts.append("Core Inactive")

        return " ".join(parts)

    def onRealized(self) -> None:
        for w in self._widgets__:
            callback = getattr(w, "onParentRealized", None)
            if callback is not None:
                callback()

    def create(self):
        self.controls = self.add(TransportBox, max_height=3)
        self.slider = self.add(VolumeBox, max_height=3, value=100)
        self.search = self.add(TitleText, name="Search", max_height=1)
        self.results = self.add(TitleMultiSelect, hidden=True, max_height=10)
        self.timer = self.add(PomodoroTimer, name="Start Timer")
        self.ager = self.add(ButtonPress, name="Advance Age")
        self.tree = self.add(ArboretumBox)

    def afterEditing(self):
        if query := self.search.get_value():
            if self.results.hidden:
                path = Path(query)
                if path.exists():
                    self.player.play(str(path.resolve()))
                    return self.parentApp.setNextForm("MAIN")
                self.name = "Searching..."
                self.draw_flag.clear()
                self.results.set_values(list(self.player.query(query).keys()))
                self.results.hidden = False
                self.results.first_display = True

        if not self.results.hidden:
            if (selected := self.results.get_selected_objects()) is not None:
                self.player.play_from_results(selected[-1])
                self.draw_flag.set()
                self.results.value = None
                self.results.hidden = True
            elif not self.results.first_display:
                self.results.hidden = True
            else:
                self.results.first_display = False
                self.draw_flag.set()
        return self.parentApp.setNextForm("MAIN")

    def h_display_help(self, *args, **kwargs):
        super().h_display_help(*args, **kwargs)
