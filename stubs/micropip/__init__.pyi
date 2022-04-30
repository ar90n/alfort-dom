from asyncio import Future
from typing import Any

def install(requirements: str | list[str], keep_going: bool = ...) -> Future[Any]: ...
