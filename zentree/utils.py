from typing import Any


class Singleton(object):
    def __new__(cls, *args, **kwargs) -> Any:
        instance: Any = cls.__dict__.get("__instance__")
        if instance is not None:
            return instance
        cls.__instance__ = instance = object.__new__(cls)
        instance.init(*args, **kwargs)
        return instance

    def init(self, *args, **kwargs) -> None:
        pass
