import micropip  # type: ignore # noqa: F401

try:
    # try to use development version
    await micropip.install("../dist/alfort_dom-0.0.0dev0-py3-none-any.whl")  # type: ignore # noqa: F704
except ValueError:
    await micropip.install("alfort-dom")  # type: ignore # noqa: F704
