from typing import Tuple

from cachetools import TTLCache, cached
from pytube import Search, YouTube
from pytube.exceptions import LiveStreamError, PytubeError
from zentree.players.player import Player
from zentree.utils import Singleton


class YouTubePlayer(Player, Singleton):
    base = "https://www.youtube.com/watch"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.results_cache = {}

    def _get_playable_url(self, res: YouTube) -> str:
        try:
            audio = res.streams.get_audio_only()
            if audio is not None:
                return audio.url
        except (LiveStreamError) as ex:
            return self.make_url(v=ex.video_id) or ""
        except (PytubeError) as ex:
            print(ex)
        return ""

    def search(self, query: str) -> Tuple[str, str]:
        for res in Search(query).results:
            yield res.title, self._get_playable_url(res)

    @cached(cache=TTLCache(maxsize=0x400, ttl=60 * 15))
    def query(self, query: str) -> dict:
        res = {title: url for title, url in self.search(query)}
        self.results_cache.update(res)
        return res

    def play_first_found(self, query: str):
        for _, v in self.query(query).items():
            self.play(v)

    def play_from_results(self, key: str) -> None:
        url = self.results_cache.get(key)
        if url is not None:
            self.play(url)
