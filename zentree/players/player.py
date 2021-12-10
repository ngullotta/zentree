from typing import Any, List, Type, TypeVar, Union
from urllib.parse import urlencode

from mpv import MPV
from requests import PreparedRequest

P = TypeVar("P", bound="Player")


class Player(MPV):
    def __init__(self: P, *args: List[str], **kwargs: dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
        self.locale()

    @staticmethod
    def locale() -> None:
        # Stupid hack to override locale stomping
        import locale

        locale.setlocale(locale.LC_NUMERIC, "C")

    def play(self: P, filename: str) -> None:
        super().play(filename)
        self.wait_until_playing()


QP = TypeVar("QP", bound="QueryablePlayer")


class QueryablePlayer(Player):
    base = "http://localhost:80"

    @classmethod
    def make_url(cls: Type[QP], **params: dict[str, Any]) -> Union[str, None]:
        request: PreparedRequest = PreparedRequest()
        request.prepare_url(cls.base, urlencode(params))
        return request.url

    def query() -> None:
        raise NotImplementedError("Derived classes must implement this")
