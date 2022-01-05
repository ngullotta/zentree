from typing import Any, Dict, Hashable, List, TypeVar

S = TypeVar("S", bound="Singleton")


class Singleton(object):
    def __new__(
        cls: Any, *args: List[Any], **kwargs: Dict[Hashable, Any]
    ) -> Any:
        instance: Any = cls.__dict__.get("__instance__")
        if instance is not None:
            return instance
        cls.__instance__ = instance = object.__new__(cls)
        instance.init(*args, **kwargs)
        return instance

    def init(self: S, *args, **kwargs) -> None:
        pass
