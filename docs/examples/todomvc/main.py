# ported from https://github.com/tastejs/todomvc/blob/master/examples/elm/src/Main.elm
import functools
import json
from dataclasses import asdict, dataclass, replace
from typing import Any, TypeAlias, Union

from alfort import Dispatch, Effect, Update
from alfort.vdom import VDom, el

from alfort_dom import AlfortDom, local_storage, location
from alfort_dom.dom import HTMLElement, dom_effect
from alfort_dom.event import handler


def save_model(model: "Model") -> None:
    local_storage["todos-alfort"] = json.dumps(asdict(model))


def load_model() -> "Model":
    serialized_model: str | None = local_storage.get("todos-alfort")
    if serialized_model is None:
        return Model(entries=[], field="", uid=0, visibility="all")

    obj = json.loads(serialized_model)
    obj["entries"] = [Entry(**e) for e in obj["entries"]]
    return Model(**obj)


def with_local_storage(update: Update["Msg", "Model"]) -> Update["Msg", "Model"]:
    @functools.wraps(update)
    def _update(msg: Msg, model: Model) -> tuple[Model, list[Effect[Msg]]]:
        model, effects = update(msg, model)

        async def _save_model(_: Dispatch[Msg]) -> None:
            save_model(model)

        return model, [_save_model, *effects]

    return _update


def visibility_from_url() -> str:
    visibility = location.hash.strip("#/")
    if visibility not in ["all", "active", "completed"]:
        visibility = "all"
    return visibility


# Model


@dataclass(frozen=True)
class Entry:
    id: int
    description: str
    completed: bool
    editing: bool


@dataclass(frozen=True)
class Model:
    entries: list[Entry]
    field: str
    uid: int
    visibility: str


def init() -> tuple[Model, list[Effect["Msg"]]]:
    model = replace(load_model(), visibility=visibility_from_url())
    return (model, [])


# Update


@dataclass(frozen=True)
class NoOp:
    pass


@dataclass(frozen=True)
class UpdateField:
    field: str


@dataclass(frozen=True)
class EditingEntry:
    id: int
    is_editing: bool


@dataclass(frozen=True)
class UpdateEntry:
    id: int
    task: str


@dataclass(frozen=True)
class Add: ...


@dataclass(frozen=True)
class Delete:
    id: int


@dataclass(frozen=True)
class DeleteComplete: ...


@dataclass(frozen=True)
class Check:
    id: int
    is_completed: bool


@dataclass(frozen=True)
class CheckAll:
    is_completed: bool


@dataclass(frozen=True)
class ChangeVisibility:
    visibility: str


@dataclass(frozen=True)
class SetModel:
    model: Model


Msg: TypeAlias = Union[
    NoOp,
    UpdateField,
    EditingEntry,
    UpdateEntry,
    Add,
    Delete,
    DeleteComplete,
    Check,
    CheckAll,
    ChangeVisibility,
    SetModel,
]


@with_local_storage
def update(msg: Msg, model: Model) -> tuple[Model, list[Effect[Msg]]]:
    match msg:
        case NoOp():
            return (model, [])
        case Add():
            entries = model.entries[:]
            if model.field:
                entries.append(Entry(model.uid, model.field, False, False))
            return (replace(model, uid=model.uid + 1, field="", entries=entries), [])
        case UpdateField(field):
            return (replace(model, field=field), [])
        case EditingEntry(id_, is_editing):

            @dom_effect(f"todo-{id_}")
            def focus(dom: HTMLElement, _: Dispatch[Msg]) -> None:
                dom.focus()

            return (
                replace(
                    model,
                    entries=[
                        replace(e, editing=is_editing) if e.id == id_ else e
                        for e in model.entries
                    ],
                ),
                [focus],
            )
        case UpdateEntry(id_, task):
            return (
                replace(
                    model,
                    entries=[
                        replace(e, description=task) if e.id == id_ else e
                        for e in model.entries
                    ],
                ),
                [],
            )
        case Delete(id_):
            return (
                replace(model, entries=[e for e in model.entries if e.id != id_]),
                [],
            )
        case DeleteComplete():
            return (
                replace(model, entries=[e for e in model.entries if not e.completed]),
                [],
            )
        case Check(id_, is_completed):
            return (
                replace(
                    model,
                    entries=[
                        replace(e, completed=is_completed) if e.id == id_ else e
                        for e in model.entries
                    ],
                ),
                [],
            )
        case CheckAll(is_completed):
            return (
                replace(
                    model,
                    entries=[replace(e, completed=is_completed) for e in model.entries],
                ),
                [],
            )
        case ChangeVisibility(visibility):
            return (replace(model, visibility=visibility), [])

        case SetModel(new_model):
            return (new_model, [])

    raise ValueError(f"Unknown message: {msg}")


# View


def view(model: Model) -> VDom:
    return el(
        "div",
        {"class": "todomvc-wrapper"},
        [
            el(
                "section",
                {"class": "todoapp"},
                [
                    view_input(model.field),
                    view_entries(model.visibility, model.entries),
                    view_controls(model.visibility, model.entries),
                ],
            ),
            info_footer(),
        ],
    )


def view_input(task: str) -> VDom:
    @handler()
    def on_input(event: Any) -> Msg:
        return UpdateField(event.target.value)

    @handler()
    def on_keydown(event: Any) -> Msg:
        if event.type == "keydown" and event.key == "Enter":
            return Add()
        return NoOp()

    return el(
        "header",
        {"class": "header"},
        [
            el(
                "h1",
                {},
                ["todos"],
            ),
            el(
                "input",
                {
                    "class": "new-todo",
                    "placeholder": "What needs to be done?",
                    "autofocus": True,
                    "value": task,
                    "name": "newTodo",
                    "onkeydown": on_keydown,
                    "oninput": on_input,
                },
                [],
            ),
        ],
    )


# View all entries


def view_entries(visibility: str, entries: list[Entry]) -> VDom:
    def is_visible(todo: Entry) -> bool:
        match visibility:
            case "completed":
                return todo.completed
            case "active":
                return not todo.completed
            case _:
                return True

    all_completed = all(e.completed for e in entries)
    css_visibility = "visible" if entries else "hidden"
    return el(
        "section",
        {"class": "main", "style": {"visibility": css_visibility}},
        [
            el(
                "input",
                {
                    "class": "toggle-all",
                    "id": "toggle-all",
                    "type": "checkbox",
                    "name": "toggle",
                    "checked": all_completed,
                    "onclick": CheckAll(not all_completed),
                },
                [],
            ),
            el("label", {"for": "toggle-all"}, ["Mark all as complete"]),
            el(
                "ul",
                {"class": "todo-list"},
                [view_entry(e) for e in entries if is_visible(e)],
            ),
        ],
    )


# View individual entries


def view_entry(todo: Entry) -> VDom:
    @handler(todo.id)
    def on_input(event: Any) -> Msg:
        return UpdateEntry(todo.id, event.target.value)

    @handler(todo.id)
    def on_keydown(event: Any) -> Msg:
        if event.type == "keydown" and event.key == "Enter":
            return EditingEntry(todo.id, False)
        return NoOp()

    class_ = ""
    if todo.completed:
        class_ += "completed"
    if todo.editing:
        class_ += " editing"
    return el(
        "li",
        {"class": class_},
        [
            el(
                "div",
                {"class": "view"},
                [
                    el(
                        "input",
                        {
                            "class": "toggle",
                            "type": "checkbox",
                            "checked": todo.completed,
                            "onclick": Check(todo.id, (not todo.completed)),
                        },
                        [],
                    ),
                    el(
                        "label",
                        {"ondblclick": EditingEntry(todo.id, True)},
                        [todo.description],
                    ),
                    el("button", {"class": "destroy", "onclick": Delete(todo.id)}, []),
                ],
            ),
            el(
                "input",
                {
                    "class": "edit",
                    "value": todo.description,
                    "name": "title",
                    "id": f"todo-{todo.id}",
                    "oninput": on_input,
                    "onblur": EditingEntry(todo.id, False),
                    "onkeydown": on_keydown,
                },
                [],
            ),
        ],
    )


# View controls and footer


def view_controls(visibility: str, entries: list[Entry]) -> VDom:
    entries_completed = len([e for e in entries if e.completed])
    entries_left = len(entries) - entries_completed
    return el(
        "footer",
        {"class": "footer", "hidden": (len(entries) == 0)},
        [
            view_controls_count(entries_left),
            view_controls_filters(visibility),
            view_controls_clear(entries_completed),
        ],
    )


def view_controls_count(entries_left: int) -> VDom:
    return el(
        "span",
        {"class": "todo-count"},
        [
            el(
                "strong",
                {},
                [str(entries_left)],
            ),
            f" item{'s' if 1 < entries_left else ''} left",
        ],
    )


def view_controls_filters(visibility: str) -> VDom:
    return el(
        "ul",
        {"class": "filters"},
        [
            visibility_swap("#/", "all", visibility),
            " ",
            visibility_swap("#/active", "active", visibility),
            " ",
            visibility_swap("#/completed", "completed", visibility),
        ],
    )


def visibility_swap(url: str, visibility: str, actual_visibility: str) -> VDom:
    return el(
        "li",
        {"onclick": ChangeVisibility(visibility)},
        [
            el(
                "a",
                {
                    "href": url,
                    "class": ("selected" if visibility == actual_visibility else ""),
                },
                [visibility],
            )
        ],
    )


def view_controls_clear(entries_completed: int) -> VDom:
    message = f"Clear completed ({entries_completed})"
    hidden = entries_completed == 0
    return el(
        "button",
        {
            "class": "clear-completed",
            "hidden": hidden,
            "onclick": DeleteComplete(),
        },
        [message],
    )


def info_footer() -> VDom:
    return el(
        "footer",
        {"class": "info"},
        [
            el(
                "p",
                {},
                [
                    "Double-click to edit a todo",
                ],
            ),
            el(
                "p",
                {},
                [
                    "Written by",
                    el(
                        "a",
                        {"href": "http://github.com/ar90n"},
                        ["@ar90n"],
                    ),
                ],
            ),
        ],
    )


app = AlfortDom[Model, Msg](
    init=init,
    view=view,
    update=update,
)
app.main(root="root")
