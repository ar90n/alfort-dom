from dataclasses import dataclass
from typing import Any, Callable, Coroutine, TypeAlias
from urllib.parse import ParseResult as URL
from urllib.parse import urlparse

from alfort import Dispatch, Effect
from alfort.vdom import VDom, el
from pyodide import http

from alfort_dom import AlfortDom


@dataclass(frozen=True)
class Photo:
    album_id: int
    id: int
    title: str
    url: URL
    thumbnail_url: URL


@dataclass(frozen=True)
class State:
    album_id: int
    is_fetching: bool
    photos: list[Photo]


@dataclass(frozen=True)
class SelectAlbum:
    alumb_id: int


@dataclass(frozen=True)
class ReceivePhotos:
    photos: list[Photo]


Msg: TypeAlias = SelectAlbum | ReceivePhotos


async def fetch_photos(album_id: int) -> list[Photo]:
    url = f"https://jsonplaceholder.typicode.com/albums/{album_id}/photos"
    res = await http.pyfetch(url)
    return [
        Photo(
            album_id=obj["albumId"],
            id=obj["id"],
            title=obj["title"],
            url=urlparse(obj["url"]),
            thumbnail_url=urlparse(obj["thumbnailUrl"]),
        )
        for obj in await res.json()
    ]


def title(text: str) -> VDom:
    return el("h1", {}, [text])


def album_selector(album_id: int) -> VDom:
    def _on_change(e: Any) -> Msg:
        return SelectAlbum(e.target.value)

    return el(
        "div",
        {"style": {"margin": "15px"}},
        [
            el("label", {"style": {"margin-right": "8px"}}, ["Album ID"]),
            el(
                "select",
                {
                    "onchange": _on_change,
                },
                [
                    el(
                        "option",
                        {
                            "value": i,
                            "selected": album_id == i,
                        },
                        [str(i)],
                    )
                    for i in range(15)
                ],
            ),
        ],
    )


def album_photos(photos: list[Photo]) -> VDom:
    photo_elms: list[VDom] = []
    for photo in photos:
        photo_elms.append(
            el(
                "img",
                {"src": photo.thumbnail_url.geturl(), "style": {"margin": "3px"}},
                [],
            )
        )

    return el("div", {"style": {"width": "75%", "line-height": "0px"}}, photo_elms)


def fetching_dialog() -> VDom:
    return el("div", {}, ["Loading..."])


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
            title("Simple Photo Album"),
            album_selector(state.album_id),
            fetching_dialog() if state.is_fetching else album_photos(state.photos),
        ],
    )


def create_fetch_effect(
    album_id: int,
) -> Callable[[Dispatch[Msg]], Coroutine[None, None, Any]]:
    async def _fetch(dispatch: Dispatch[Msg]) -> None:
        recv_photos = await fetch_photos(album_id=album_id)
        dispatch(ReceivePhotos(recv_photos))

    return _fetch


def init() -> tuple[State, list[Effect[Msg]]]:
    return (State(album_id=1, is_fetching=True, photos=[]), [create_fetch_effect(1)])


def update(msg: Msg, state: State) -> tuple[State, list[Effect[Msg]]]:
    match msg:
        case SelectAlbum(album_id):
            state = State(album_id=album_id, is_fetching=True, photos=[])
            return (state, [create_fetch_effect(album_id=album_id)])
        case ReceivePhotos(photos):
            state = State(album_id=state.album_id, is_fetching=False, photos=photos)
            return (state, [])


app = AlfortDom[State, Msg](
    init=init,
    view=view,
    update=update,
)
app.main(root="root")
