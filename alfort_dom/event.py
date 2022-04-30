from typing import Any, Callable, Generic, TypeVar

Msg = TypeVar("Msg")


class Handler(Generic[Msg]):
    def __init__(self, fun: Any, key: Any):
        self.key = key
        self.fun = fun

    def __call__(self, *args: Any, **kwargs: Any) -> Msg:
        return self.fun(*args, **kwargs)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Handler):
            return False
        if isinstance(other, type(self.key)):
            return False
        return self.key == other.key


def handler(key: Any | None = None) -> Callable[[Callable[[Any], Msg]], Handler[Msg]]:
    def _constructor(f: Callable[[Any], Msg]) -> Handler[Msg]:
        _key = key if key is not None else tuple(f.__code__.co_lines())
        return Handler[Msg](f, _key)

    return _constructor
