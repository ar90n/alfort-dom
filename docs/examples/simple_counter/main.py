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
