from datetime import datetime, timedelta
from threading import Event, Thread
from typing import Any, TypeVar

from npyscreen import ButtonPress

TT = TypeVar("TT", bound="Timer")


class Timer(Thread):
    def __init__(self: TT, **kwargs: dict[str, Any]) -> None:
        super().__init__(**kwargs)
        self.stop: Event = Event()

    def run(self: TT) -> None:
        while not self.stop.is_set():
            super().run()


PT = TypeVar("PT", bound="PomodoroTimer")


class PomodoroTimer(ButtonPress):
    def __init__(self: PT, screen: Any, **kwargs: dict[str, Any]) -> None:
        super().__init__(screen, **kwargs)
        self.time: int = 0
        self.active_flag: Event = Event()
        self.active_flag.set()
        self.exit_flag: Event = Event()

        self.timer: Timer = Timer(target=self.every, args=(1, self.tick))
        self.timer.start()

        self.counter: int = 0
        self.bt: int = 0
        self._break: datetime = datetime.utcnow()

    def every(self: PT, seconds: int, fn: callable) -> None:
        while not self.exit_flag.wait(timeout=seconds):
            if self.active_flag.is_set():
                try:
                    fn()
                except (Exception):
                    pass

    def pomodoro(self: PT) -> None:
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

    def tick(self: PT) -> None:
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

    def whenPressed(self: PT) -> None:
        if self.timer.stop.is_set():
            self.timer.stop.clear()
            self.active_flag.set()
        else:
            self.timer.stop.set()
            self.active_flag.clear()
            self.time = 0
            self.name = "Start Timer"
