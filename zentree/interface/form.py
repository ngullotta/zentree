from threading import Event, Thread

from npyscreen import Form


class RedrawingForm(Form):
    HELP: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        self.exit_flag: Event = Event()
        self.draw_flag: Event = Event()

        self.thread: Thread = Thread(target=self.every, args=(1, self.display))
        self.thread.start()

        self.help: str = self.HELP

    def every(self, seconds: int, fn: callable) -> None:
        while not self.exit_flag.wait(timeout=seconds):
            if self.draw_flag.is_set():
                try:
                    fn()
                except (Exception) as ex:
                    pass

    def h_display_help(self, *args, **kwargs) -> None:
        self.draw_flag.clear()
        super().h_display_help(*args, **kwargs)
        self.draw_flag.set()
