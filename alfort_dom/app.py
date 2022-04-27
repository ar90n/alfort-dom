from typing import Any, Callable, Generic, TypeVar

from alfort import Alfort, Dispatch, Init, Update, View
from alfort.vdom import (
    Node,
    Patch,
    PatchInsertChild,
    PatchProps,
    PatchRemoveChild,
    PatchText,
    Props,
)
from js import document  # type: ignore
from pyodide import JsProxy, create_proxy, to_js  # type: ignore

S = TypeVar("S")
M = TypeVar("M")


class DomNode(Node, Generic[M]):
    dom: JsProxy
    dispatch: Dispatch[M]
    handlers: dict[str, Callable[[Any], None]]
    listener: JsProxy

    def __init__(self, dom: JsProxy, dispatch: Dispatch[M]) -> None:
        self.dom = dom
        self.dispatch = dispatch
        self.handlers = {}

        def _listener(event: Any) -> None:
            handler = self.handlers.get(event.type)
            if handler is not None:
                self.dispatch(handler(event))

        self.listener = create_proxy(_listener)

    def apply(self, patch: Patch) -> None:
        match patch:
            case PatchInsertChild(child, None) if isinstance(child, DomNode):
                self.dom.insertBefore(child.dom, to_js(None))
            case PatchInsertChild(child, reference) if isinstance(
                child, DomNode
            ) and isinstance(reference, DomNode):
                self.dom.insertBefore(child.dom, reference.dom)
            case PatchRemoveChild(child) if isinstance(child, DomNode):
                self.dom.removeChild(child.dom)
            case PatchProps(remove_keys, add_props):
                if isinstance(add_props.get("style"), dict):
                    style = add_props.pop("style")
                    for k, v in style.items():
                        setattr(self.dom.style, k, v)

                for k in remove_keys:
                    if k.startswith("on"):
                        event_type = k[2:].lower()
                        self.dom.removeEventListener(event_type, self.listener)
                        del self.handlers[event_type]
                    else:
                        self.dom.removeAttribute(k)

                for k, v in add_props.items():
                    if k.startswith("on"):
                        event_type = k[2:].lower()
                        if v is not None:
                            if event_type in self.handlers:
                                self.dom.removeEventListener(event_type, self.listener)
                                del self.handlers[event_type]
                            if callable(v):
                                self.handlers[event_type] = v
                            else:
                                self.handlers[event_type] = lambda _: v
                            self.dom.addEventListener(event_type, self.listener)
                        else:
                            self.dom.removeEventListener(event_type, self.listener)
                            del self.handlers[event_type]
                    elif hasattr(self.dom, k):
                        setattr(self.dom, k, v)
                    else:
                        self.dom.setAttribute(k, v)
            case PatchText():
                self.dom.nodeValue = patch.value
            case _:
                raise ValueError(f"Unknown patch: {patch}")


class AlfortDom(Alfort[S, M, DomNode[M]]):
    @classmethod
    def create_text(
        cls,
        text: str,
        dispatch: Dispatch[M],
    ) -> DomNode[M]:
        return DomNode(document.createTextNode(text), dispatch)

    @classmethod
    def create_element(
        cls,
        tag: str,
        props: Props,
        children: list[DomNode[M]],
        dispatch: Dispatch[M],
    ) -> DomNode[M]:
        dom_node = DomNode(document.createElement(tag, to_js({})), dispatch)

        for c in children:
            dom_node.apply(PatchInsertChild(c, None))

        dom_node.apply(PatchProps(remove_keys=[], add_props=props))
        return dom_node

    @classmethod
    def main(
        cls,
        init: Init[S, M],
        view: View[S],
        update: Update[M, S],
        root: str,
    ) -> None:
        def mount(node: Node) -> None:
            if not isinstance(node, DomNode):
                raise ValueError("node must be a DomNode")
            dom = node.dom
            document.getElementById(root).appendChild(dom)

        cls._main(
            mount=mount,
            init=init,
            view=view,
            update=update,
        )
