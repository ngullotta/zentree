from threading import Event, Thread

from npyscreen import Form


class RedrawingForm(Form):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        self.exit_flag: Event = Event()
        self.draw_flag: Event = Event()

        self._redraw_thread: Thread = Thread(
            target=self.every, args=(1, self.redraw)
        )

        self._redraw_thread.start()

    def redraw(self) -> None:
        if self.draw_flag.is_set():
            self.display()

    def every(self, seconds: int, fn: callable) -> None:
        while not self.exit_flag.wait(timeout=seconds):
            try:
                fn()
            except (Exception):
                pass

    def h_display_help(self, *args, **kwargs) -> None:
        self.draw_flag.clear()
        super().h_display_help(*args, **kwargs)
        self.draw_flag.set()
