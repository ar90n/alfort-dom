from dataclasses import dataclass
from typing import Any, TypeAlias

from alfort import Effect
from alfort.sub import Subscription
from alfort.vdom import VDom, el

from alfort_dom import AlfortDom
from alfort_dom.event import on_keypress, on_keyup, on_mousemove

State: TypeAlias = dict[str, Any]


@dataclass(frozen=True)
class MouseMoved:
    x: int
    y: int


@dataclass(frozen=True)
class KeyPressed:
    c: str


@dataclass(frozen=True)
class KeyUp:
    c: str


Msg: TypeAlias = MouseMoved | KeyPressed | KeyUp


def title(text: str) -> VDom:
    return el("h1", {}, [text])


def mouse_position(x: int, y: int) -> VDom:
    return el(
        "div", {"style": {"margin": "8px"}}, [f"Mouse position: {str(x)}, {str(y)}"]
    )


def press_keys(keys: list[str]) -> VDom:
    return el("div", {"style": {"margin": "8px"}}, [f"Pressed keys: {','.join(keys)}"])


def view(state: State) -> VDom:
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
        [
            title("Key and Mouse Event"),
            mouse_position(state["x"], state["y"]),
            press_keys(state["keys"]),
        ],
    )


def init() -> tuple[State, list[Effect[Msg]]]:
    return ({"x": 0, "y": 0, "keys": []}, [])


def update(msg: Msg, state: State) -> tuple[State, list[Effect[Msg]]]:
    match msg:
        case MouseMoved(x, y):
            return ({**state, "x": x, "y": y}, [])
        case KeyPressed(c):
            keys = list(sorted({*state["keys"], c}))
            return ({**state, "keys": keys}, [])
        case KeyUp(c):
            keys = state["keys"]
            p = keys.index(c)
            keys = [*keys[:p], *keys[p + 1 :]]
            return ({**state, "keys": keys}, [])


def subscriptions(state: State) -> list[Subscription[Msg]]:
    return [
        on_mousemove(lambda e: MouseMoved(e.pageX, e.pageY)),
        on_keypress(lambda e: KeyPressed(e.code)),
        on_keyup(lambda e: KeyUp(e.code)),
    ]


app = AlfortDom[State, Msg](
    init=init, view=view, update=update, subscriptions=subscriptions
)
app.main(root="root")
