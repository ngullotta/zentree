import logging
from typing import Tuple, TypeVar

from cachetools import cached
from pytube import Search, YouTube
from pytube.exceptions import LiveStreamError, PytubeError
from pytube.streams import Stream
from zentree.players.cache import QueryCache
from zentree.players.player import QueryablePlayer
from zentree.utils import Singleton

YTP = TypeVar("YTP", bound="YouTubePlayer")


class YouTubePlayer(QueryablePlayer, Singleton):
    base = "https://www.youtube.com/watch"

    logger = logging.getLogger("player.youtube")

    _cache = QueryCache(maxsize=0x400, ttl=60 * 15)

    def _get_playable_url(self: YTP, result: YouTube) -> str:
        try:
            audio: Stream = result.streams.get_audio_only()
            if audio is not None:
                return audio.url
        except (LiveStreamError) as ex:
            return self.make_url(v=ex.video_id) or ""
        except (PytubeError) as ex:
            self.logger.error("Error fetching playable URL:", ex)
        return ""

    def search(self: YTP, query: str) -> Tuple[str, str]:
        if results := Search(query).results:
            for res in results:
                yield res.title, self._get_playable_url(res)

    @cached(_cache)
    def query(self: YTP, query: str) -> dict[str, str]:
        return {title: url for title, url in self.search(query)}

    def play_first_found(self: YTP, query: str) -> None:
        for _, v in self.query(query).items():
            self.play(v)
            break

    def play_from_results(self: YTP, key: str) -> None:
        if (last := self._cache.fetchlast()) is not None:
            if (url := last.get(key)) is not None:
                self.play(url)
