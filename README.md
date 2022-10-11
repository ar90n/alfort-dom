# Alfort-DOM
[![Build][build-shiled]][build-url]
[![Version][version-shield]][version-url]
[![Downloads][download-shield]][download-url]
[![Contributors][contributors-shield]][contributors-url]
[![Issues][issues-shield]][issues-url]
[![Codecov][codecov-shield]][codecov-url]
[![Apache License 2.0 License][license-shield]][license-url]

Alfort-DOM is Elm-like web application framework for Python. It uses [Alfort](https://github.com/ar90n/alfort) to handle Vritual DOM and [Pyodide](https://pyodide.org/en/stable/) to run its codes on browser.

## Installation
```bash
$ pip install alfort-dom
```

## Example
```python
from dataclasses import dataclass
from typing import TypeAlias

from alfort import Effect
from alfort.vdom import VDom, el

from alfort_dom import AlfortDom


@dataclass(frozen=True)
class CountUp:
    value: int = 1


@dataclass(frozen=True)
class CountDown:
    value: int = 1


Msg: TypeAlias = CountUp | CountDown


def title(text: str) -> VDom:
    return el("h1", {}, [text])


def count(cnt: int) -> VDom:
    return el("div", {"style": {"margin": "8px"}}, [str(cnt)])


def buttons() -> VDom:
    button_style = {"margin": "4px", "width": "50px"}
    return el(
        "div",
        {},
        [
            el("button", {"style": button_style, "onclick": CountDown(10)}, ["-10"]),
            el("button", {"style": button_style, "onclick": CountDown()}, ["-"]),
            el("button", {"style": button_style, "onclick": CountUp()}, ["+"]),
            el("button", {"style": button_style, "onclick": CountUp(10)}, ["+10"]),
        ],
    )


def view(state: dict[str, int]) -> VDom:
    return el(
        "div",
        {
            "style": {
                "display": "flex",
                "justify-content": "center",
                "align-items": "center",
                "flex-flow": "column",
            }
        },
        [title("Simple Counter"), count(state["count"]), buttons()],
    )


def init() -> tuple[dict[str, int], list[Effect[Msg]]]:
    return ({"count": 0}, [])


def update(msg: Msg, state: dict[str, int]) -> tuple[dict[str, int], list[Effect[Msg]]]:
    match msg:
        case CountUp(value):
            return ({**state, "count": state["count"] + value}, [])
        case CountDown(value):
            return ({**state, "count": state["count"] - value}, [])


app = AlfortDom[dict[str, int], Msg](
    init=init,
    view=view,
    update=update,
)
app.main(root="root")

```

![simple counter](https://raw.githubusercontent.com/ar90n/alfort-dom/assets/images/example.gif)

If you need more exmplaes, please check the [examples](https://github.com/ar90n/alfort-dom/tree/main/docs/examples).

## For development
### Install Poery plugins
```bash
$ poetry self add "poethepoet[poetry_plugin]"
```

### Run tests
```bash
$ poetry poe test
```

### Run linter and formatter
```bash
$ poetry poe check
```
### Run examples
```bash
$ poetry poe run-example
```

## See Also
* [Elm](https://elm-lang.org/)
* [Pyodide](https://pyodide.org/en/stable/)
* [Alfort](https://github.com/ar90n/alfort)

## License
[Apache-2.0](https://github.com/ar90n/alfort-dom/blob/main/LICENSE)


[download-shield]: https://img.shields.io/pypi/dm/alfort-dom?style=flat
[download-url]: https://pypi.org/project/alfort-dom/
[version-shield]: https://img.shields.io/pypi/v/alfort-dom?style=flat
[version-url]: https://pypi.org/project/alfort-dom/
[build-shiled]: https://img.shields.io/github/workflow/status/ar90n/alfort-dom/CI%20testing/main
[build-url]: https://github.com/ar90n/alfort-dom/actions/workflows/ci.yml
[contributors-shield]: https://img.shields.io/github/contributors/ar90n/alfort-dom.svg?style=flat
[contributors-url]: https://github.com/ar90n/alfort-dom/graphs/contributors
[issues-shield]: https://img.shields.io/github/issues/ar90n/alfort-dom.svg?style=flat
[issues-url]: https://github.com/ar90n/alfort-dom/issues
[license-shield]: https://img.shields.io/github/license/ar90n/alfort-dom.svg?style=flat
[license-url]: https://github.com/ar90n/alfort-dom/blob/master/LICENSE.txt
[codecov-shield]: https://codecov.io/gh/ar90n/alfort-dom/branch/main/graph/badge.svg?token=8GKU96ODLY
[codecov-url]: https://codecov.io/gh/ar90n/alfort-dom
