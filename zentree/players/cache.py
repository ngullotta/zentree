from collections import OrderedDict
from typing import Any, TypeVar, Union

from cachetools import TTLCache
from cachetools.keys import _HashedTuple


class _TTLCache(TTLCache):
    @property
    def links(self: TTLCache) -> OrderedDict:
        return self.__links


QC = TypeVar("QC", bound="QueryCache")


class QueryCache(_TTLCache):
    def fetchlast(self: QC) -> Union[Any, None]:
        with self.timer as time:
            self.expire(time)
            try:
                key: _HashedTuple = next(iter(self.links))
            except StopIteration:
                raise KeyError("%s is empty" % type(self).__name__) from None
            else:
                return self.get(key)
