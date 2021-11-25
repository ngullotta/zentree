from typing import Union
from urllib.parse import urlencode

from mpv import MPV
from requests import PreparedRequest


class Player(MPV):
    base = ""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.locale()

    @staticmethod
    def locale():
        # Stupid hack to override locale stomping
        import locale

        locale.setlocale(locale.LC_NUMERIC, "C")

    @classmethod
    def make_url(cls, **args: dict) -> Union[str, None]:
        req = PreparedRequest()
        req.prepare_url(cls.base, urlencode(args))
        return req.url

    def query() -> None:
        raise NotImplementedError("Derived classes must implement this")

    def play(self, *args, **kwargs) -> None:
        self.current_track = kwargs.pop("name", "")
        super().play(*args, **kwargs)
        self.wait_until_playing()
        return
