from typing import Any, Union

from cachetools import TTLCache
from cachetools.keys import _HashedTuple


class QueryCache(TTLCache):
    def fetchlast(self: TTLCache) -> Union[Any, None]:
        with self.__timer as time:
            self.expire(time)
            try:
                key: _HashedTuple = next(iter(self.__links))
            except StopIteration:
                raise KeyError("%s is empty" % type(self).__name__) from None
            else:
                return self.get(key)
