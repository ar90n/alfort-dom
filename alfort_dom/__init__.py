from importlib.metadata import PackageNotFoundError, version

try:
    __version__: str = version(__name__)
except PackageNotFoundError:
    __version__: str = "unknown"

from .app import AlfortDom

__all__ = ["AlfortDom"]
