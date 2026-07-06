"""
PHANTOM PLAYER - ULTIMATE SCI-FI TUI
A single-terminal music player with live ASCII animations
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Input, Static, ProgressBar,
    Label, ListView, ListItem, ContentSwitcher, Rule
)
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.reactive import reactive
from textual import work
from ytmusicapi import YTMusic
import asyncio
import json
import os
import time

from player import PhantomPlayer

PLAYLIST_FILE = "playlist.json"
EXPORTS_DIR   = "exports"

# ─────────────────────────────────────────────────────
#  ASCII ART FRAMES
# ─────────────────────────────────────────────────────

GLOBE_FRAMES = [
r"""
    .-~~~-.
  (  · · ·  )
 ( ·  ───  · )
(  · /   \ ·  )
(  ·|  ☆  |·  )
 ( ·  ───  · )
  (  · · ·  )
    '~-──-~'
""",
r"""
    .-~~~-.
  (  · · ·  )
 ( · ──── · )
(  ·/     \·  )
( · |  ☆  | · )
 ( · ──── · )
  (  · · ·  )
    '~-──-~'
""",
r"""
    .-~~~-.
  (  · · ·  )
 ( ─── · ─── )
(  \  · · ·  /  )
(   | ·☆· |   )
 ( ─── · ─── )
  (  · · ·  )
    '~-──-~'
""",
r"""
    .-~~~-.
  (  · · ·  )
 ( · ──── · )
(  ·\     /·  )
( · |  ☆  | · )
 ( · ──── · )
  (  · · ·  )
    '~-──-~'
""",
]

CD_FRAMES = [
r"""
      ╭───────╮
     ╱ ╭─────╮ ╲
    │  │  ●  │  │
    │  │ ─/─ │  │
     ╲ ╰─────╯ ╱
      ╰───────╯
""",
r"""
      ╭───────╮
     ╱ ╭─────╮ ╲
    │  │  ●  │  │
    │  │  |  │  │
     ╲ ╰─────╯ ╱
      ╰───────╯
""",
r"""
      ╭───────╮
     ╱ ╭─────╮ ╲
    │  │  ●  │  │
    │  │ ─\─ │  │
     ╲ ╰─────╯ ╱
      ╰───────╯
""",
r"""
      ╭───────╮
     ╱ ╭─────╮ ╲
    │  │  ●  │  │
    │  │  ─  │  │
     ╲ ╰─────╯ ╱
      ╰───────╯
""",
]

LOADING_FRAMES = [
    " ◐ LOADING ",
    " ◓ LOADING ",
    " ◑ LOADING ",
    " ◒ LOADING ",
]

IDLE_ART = r"""
  ╔═══════════════╗
  ║  P H A N T O M  ║
  ║   P L A Y E R   ║
  ║                 ║
  ║   ▶ READY  ◀   ║
  ╚═══════════════╝
"""

# ─────────────────────────────────────────────────────
#  MODAL: Pick a playlist to save a track
# ─────────────────────────────────────────────────────

class PlaylistSelectModal(ModalScreen):
    BINDINGS = [Binding("escape", "dismiss", "Cancel")]

    def __init__(self, playlists: list[str]):
        super().__init__()
        self.playlists = playlists

    def compose(self) -> ComposeResult:
        with Vertical(id="modal_box"):
            yield Label("  ADD TO PLAYLIST  ", id="modal_title")
            yield Rule()
            yield ListView(
                *(ListItem(Label(f"  {p}"), name=p) for p in self.playlists),
                id="modal_list"
            )
            yield Label("  [Esc] Cancel", id="modal_hint")

    def on_list_view_selected(self, event: ListView.Selected):
        self.dismiss(event.item.name)

    def action_dismiss(self):
        self.dismiss(None)


# ─────────────────────────────────────────────────────
#  VISUALIZER WIDGET
# ─────────────────────────────────────────────────────

class Visualizer(Static):
    """Animated sci-fi visualizer cycling between globe and CD frames."""

    def on_mount(self):
        self._state   = "idle"     # idle | buffering | playing
        self._fidx    = 0
        self._lidx    = 0
        self._use_globe = True     # alternate between globe/CD each song
        self._timer   = self.set_interval(0.13, self._tick, pause=True)

    # ── public API ──────────────────────────────────

    def set_idle(self):
        self._state = "idle"
        self._timer.pause()
        self._render()

    def set_buffering(self):
        self._state = "buffering"
        self._fidx  = 0
        self._timer.resume()

    def set_playing(self, toggle_art=False):
        if toggle_art:
            self._use_globe = not self._use_globe
            self._fidx = 0
        self._state = "playing"
        self._timer.resume()

    # ── internal ────────────────────────────────────

    def _tick(self):
        self._render()

    def _render(self):
        if self._state == "idle":
            self.update(f"[bold]{IDLE_ART}[/]")
        elif self._state == "buffering":
            frame = LOADING_FRAMES[self._lidx % len(LOADING_FRAMES)]
            self._lidx += 1
            self.update(f"[bold]{frame}[/]")
        else:
            frames = GLOBE_FRAMES if self._use_globe else CD_FRAMES
            art = frames[self._fidx % len(frames)]
            self._fidx += 1
            self.update(f"[bold]{art}[/]")


# ─────────────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────────────

class PhantomUI(App):
    """Phantom Player — single-terminal sci-fi music player."""

    TITLE = "PHANTOM PLAYER"

    CSS = r"""
/* ── LAYOUT ─────────────────────────────────────── */
Screen {
    layers: base overlay;
}
#root {
    layout: horizontal;
    height: 100%;
}

/* LEFT COLUMN — Animation + Now Playing */
#left_col {
    width: 36;
    height: 100%;
    layout: vertical;
    border-right: solid;
    padding: 0 1;
}
#visualizer {
    height: 12;
    content-align: center middle;
    text-align: center;
}
#now_playing_box {
    height: auto;
    padding: 1 0;
}
#track_title {
    text-align: center;
    text-style: bold;
    height: 2;
    content-align: center middle;
    overflow: hidden;
}
#track_artist {
    text-align: center;
    height: 1;
    color: $text-muted;
}
#progress_label {
    text-align: center;
    height: 1;
    margin-top: 1;
}
#progress {
    height: 1;
    margin: 0 1;
}
#vol_row {
    layout: horizontal;
    align: center middle;
    height: 1;
    margin-top: 1;
}
#vol_label {
    width: 8;
    text-align: right;
}
#vol_bar {
    width: 1fr;
}
#status_bar {
    height: 1;
    text-align: center;
    margin-top: 1;
    text-style: italic;
}
Rule {
    margin: 1 0;
}

/* RIGHT COLUMN — Tabs + Content */
#right_col {
    width: 1fr;
    height: 100%;
    layout: vertical;
}
#tab_bar {
    height: 3;
    layout: horizontal;
    align: center middle;
}
.tab_btn {
    width: 1fr;
    height: 3;
    content-align: center middle;
    text-align: center;
    text-style: bold;
    border: solid;
}
.tab_btn.active {
    text-style: bold reverse;
}
#content_area {
    height: 1fr;
}

/* SEARCH VIEW */
#search_view {
    height: 100%;
    layout: vertical;
    padding: 1 2;
}
#search_input {
    height: 3;
    border: round;
}
#search_hint {
    height: 1;
    color: $text-muted;
    text-align: center;
    margin-bottom: 1;
}
#search_results {
    height: 1fr;
    border: round;
}

/* LIBRARY VIEW */
#library_view {
    height: 100%;
    layout: horizontal;
}
#playlist_col {
    width: 40%;
    height: 100%;
    layout: vertical;
    padding: 1 1;
    border-right: dashed;
}
#tracks_col {
    width: 1fr;
    height: 100%;
    layout: vertical;
    padding: 1 1;
}
#new_pl_input {
    height: 3;
    border: round;
}
#pl_hint {
    height: 1;
    color: $text-muted;
    text-align: center;
}
#library_list {
    height: 1fr;
    border: round;
}
#playlist_detail_title {
    height: 2;
    text-align: center;
    text-style: bold;
    content-align: center middle;
}
#playlist_detail_list {
    height: 1fr;
    border: round;
}

/* QUEUE VIEW */
#queue_view {
    height: 100%;
    layout: vertical;
    padding: 1 2;
}
#queue_title {
    height: 2;
    text-align: center;
    text-style: bold;
    content-align: center middle;
}
#active_queue {
    height: 1fr;
    border: round;
}
#queue_hint {
    height: 1;
    color: $text-muted;
    text-align: center;
}

/* LIST ITEMS */
ListView {
    scrollbar-size: 1 1;
}
ListItem {
    padding: 0 1;
}

/* MODAL */
PlaylistSelectModal {
    align: center middle;
    background: $background 70%;
    layer: overlay;
}
#modal_box {
    width: 50;
    height: auto;
    max-height: 30;
    border: double;
    padding: 1 2;
}
#modal_title {
    text-style: bold;
    text-align: center;
}
#modal_hint {
    text-align: center;
    color: $text-muted;
    margin-top: 1;
}
#modal_list {
    height: auto;
    max-height: 20;
    border: round;
}

/* ── THEMES ──────────────────────────────────────── */

/* HACKER */
Screen.hacker { background: #000000; color: #00ff41; }
Screen.hacker Header { background: #000000; color: #00ff41; }
Screen.hacker Footer { background: #0a0a0a; color: #00ff41; }
Screen.hacker #left_col { border-right: solid #00aa00; }
Screen.hacker #tab_bar { background: #050505; }
Screen.hacker .tab_btn { border: solid #005500; color: #009900; }
Screen.hacker .tab_btn.active { background: #002200; color: #00ff41; border: solid #00ff41; }
Screen.hacker #search_input { border: round #00aa00; background: #000800; color: #00ff41; }
Screen.hacker #search_input:focus { border: round #00ff41; }
Screen.hacker #search_results { border: round #005500; background: #000500; }
Screen.hacker ListItem:hover { background: #001100; }
Screen.hacker ListItem.--highlight { background: #003300; color: #00ff41; }
Screen.hacker #new_pl_input { border: round #00aa00; background: #000800; color: #00ff41; }
Screen.hacker #library_list { border: round #005500; background: #000500; }
Screen.hacker #playlist_detail_list { border: round #005500; background: #000500; }
Screen.hacker #active_queue { border: round #005500; background: #000500; }
Screen.hacker Rule { color: #005500; }
Screen.hacker ProgressBar > Bar > .bar--bar { color: #00ff41; }
Screen.hacker ProgressBar > Bar { background: #002200; }
Screen.hacker #modal_box { border: double #00ff41; background: #000a00; }
Screen.hacker #modal_list { border: round #005500; background: #000500; }

/* CYBERPUNK */
Screen.cyberpunk { background: #0d0014; color: #ff00ff; }
Screen.cyberpunk Header { background: #0d0014; color: #ff00ff; }
Screen.cyberpunk Footer { background: #120018; color: #ff00ff; }
Screen.cyberpunk #left_col { border-right: solid #880088; }
Screen.cyberpunk #tab_bar { background: #0a0010; }
Screen.cyberpunk .tab_btn { border: solid #440044; color: #cc00cc; }
Screen.cyberpunk .tab_btn.active { background: #220022; color: #ff00ff; border: solid #ff00ff; }
Screen.cyberpunk #search_input { border: round #cc00cc; background: #120014; color: #ff00ff; }
Screen.cyberpunk #search_input:focus { border: round #ff00ff; }
Screen.cyberpunk #search_results { border: round #440044; background: #0a000f; }
Screen.cyberpunk ListItem:hover { background: #1a0022; }
Screen.cyberpunk ListItem.--highlight { background: #330033; color: #ff00ff; }
Screen.cyberpunk #new_pl_input { border: round #cc00cc; background: #120014; color: #ff00ff; }
Screen.cyberpunk #library_list { border: round #440044; background: #0a000f; }
Screen.cyberpunk #playlist_detail_list { border: round #440044; background: #0a000f; }
Screen.cyberpunk #active_queue { border: round #440044; background: #0a000f; }
Screen.cyberpunk Rule { color: #440044; }
Screen.cyberpunk ProgressBar > Bar > .bar--bar { color: #ff00ff; }
Screen.cyberpunk ProgressBar > Bar { background: #220022; }
Screen.cyberpunk #modal_box { border: double #ff00ff; background: #0d0014; }
Screen.cyberpunk #modal_list { border: round #440044; background: #0a000f; }

/* NORD */
Screen.nord { background: #2e3440; color: #eceff4; }
Screen.nord Header { background: #2e3440; color: #88c0d0; }
Screen.nord Footer { background: #272c36; color: #88c0d0; }
Screen.nord #left_col { border-right: solid #4c566a; }
Screen.nord #tab_bar { background: #272c36; }
Screen.nord .tab_btn { border: solid #3b4252; color: #81a1c1; }
Screen.nord .tab_btn.active { background: #3b4252; color: #88c0d0; border: solid #88c0d0; }
Screen.nord #search_input { border: round #4c566a; background: #3b4252; color: #eceff4; }
Screen.nord #search_input:focus { border: round #88c0d0; }
Screen.nord #search_results { border: round #4c566a; background: #2e3440; }
Screen.nord ListItem:hover { background: #3b4252; }
Screen.nord ListItem.--highlight { background: #4c566a; color: #eceff4; }
Screen.nord #new_pl_input { border: round #4c566a; background: #3b4252; color: #eceff4; }
Screen.nord #library_list { border: round #4c566a; background: #2e3440; }
Screen.nord #playlist_detail_list { border: round #4c566a; background: #2e3440; }
Screen.nord #active_queue { border: round #4c566a; background: #2e3440; }
Screen.nord Rule { color: #4c566a; }
Screen.nord ProgressBar > Bar > .bar--bar { color: #88c0d0; }
Screen.nord ProgressBar > Bar { background: #4c566a; }
Screen.nord #modal_box { border: double #88c0d0; background: #3b4252; }
Screen.nord #modal_list { border: round #4c566a; background: #2e3440; }

/* VOID */
Screen.void { background: #080808; color: #e0e0e0; }
Screen.void Header { background: #080808; color: #ffffff; }
Screen.void Footer { background: #050505; color: #aaaaaa; }
Screen.void #left_col { border-right: solid #444444; }
Screen.void #tab_bar { background: #050505; }
Screen.void .tab_btn { border: solid #2a2a2a; color: #888888; }
Screen.void .tab_btn.active { background: #1a1a1a; color: #ffffff; border: solid #ffffff; }
Screen.void #search_input { border: round #444444; background: #111111; color: #e0e0e0; }
Screen.void #search_input:focus { border: round #ffffff; }
Screen.void #search_results { border: round #2a2a2a; background: #0c0c0c; }
Screen.void ListItem:hover { background: #1a1a1a; }
Screen.void ListItem.--highlight { background: #2a2a2a; color: #ffffff; }
Screen.void #new_pl_input { border: round #444444; background: #111111; color: #e0e0e0; }
Screen.void #library_list { border: round #2a2a2a; background: #0c0c0c; }
Screen.void #playlist_detail_list { border: round #2a2a2a; background: #0c0c0c; }
Screen.void #active_queue { border: round #2a2a2a; background: #0c0c0c; }
Screen.void Rule { color: #333333; }
Screen.void ProgressBar > Bar > .bar--bar { color: #ffffff; }
Screen.void ProgressBar > Bar { background: #222222; }
Screen.void #modal_box { border: double #ffffff; background: #111111; }
Screen.void #modal_list { border: round #2a2a2a; background: #0c0c0c; }
"""

    BINDINGS = [
        Binding("ctrl+q", "quit",         "Quit",     show=True),
        Binding("1",       "tab_search",   "Search",   show=True),
        Binding("2",       "tab_library",  "Library",  show=True),
        Binding("3",       "tab_queue",    "Queue",    show=True),
        Binding("space",   "toggle_pause", "Pause",    show=True),
        Binding("n",       "play_next",    "Next",     show=True),
        Binding("right",   "seek_fwd",     "+10s",     show=False),
        Binding("left",    "seek_back",    "-10s",     show=False),
        Binding("+",       "vol_up",       "Vol+",     show=True),
        Binding("=",       "vol_up",       "",         show=False),
        Binding("-",       "vol_down",     "Vol-",     show=True),
        Binding("a",       "add_track",    "Add→PL",   show=True),
        Binding("d",       "delete_item",  "Delete",   show=True),
        Binding("t",       "cycle_theme",  "Theme",    show=True),
        Binding("e",       "export_pl",    "Export",   show=False),
    ]

    # ── reactive state ──────────────────────────────
    current_tab: reactive[str] = reactive("search")
    volume:      reactive[int] = reactive(60)

    def __init__(self):
        super().__init__()
        self.player  = PhantomPlayer(callback=self._player_cb)
        self.yt      = YTMusic()
        self.library: dict[str, list] = {"Default": []}
        self.active_pl   = "Default"
        self.queue:  list = []
        self.queue_idx   = -1
        self.search_results: list = []
        self._paused = False
        self._themes = ["hacker", "cyberpunk", "nord", "void"]
        self._tidx   = 0
        os.makedirs(EXPORTS_DIR, exist_ok=True)
        self._load_library()

    # ── library persistence ─────────────────────────

    def _load_library(self):
        if os.path.exists(PLAYLIST_FILE):
            try:
                data = json.loads(open(PLAYLIST_FILE).read())
                self.library = data if isinstance(data, dict) else {"Default": data}
            except Exception:
                pass
        if not self.library:
            self.library = {"Default": []}

    def _save_library(self):
        try:
            open(PLAYLIST_FILE, "w").write(json.dumps(self.library, indent=2))
        except Exception:
            pass

    # ── compose ─────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="root"):

            # ── LEFT: visualizer + now-playing ──────
            with Vertical(id="left_col"):
                yield Visualizer(id="visualizer")
                yield Rule()
                with Container(id="now_playing_box"):
                    yield Label("PHANTOM PLAYER", id="track_title")
                    yield Label("ready to stream", id="track_artist")
                    yield Label("─── : ───", id="progress_label")
                    yield ProgressBar(total=100, id="progress", show_eta=False)
                    with Horizontal(id="vol_row"):
                        yield Label("VOL ", id="vol_label")
                        yield ProgressBar(total=100, id="vol_bar", show_eta=False)
                    yield Label("● IDLE", id="status_bar")

            # ── RIGHT: tabs + content ────────────────
            with Vertical(id="right_col"):
                with Horizontal(id="tab_bar"):
                    yield Static(" [1] SEARCH ", id="tab_search_btn",   classes="tab_btn active")
                    yield Static(" [2] LIBRARY ", id="tab_library_btn", classes="tab_btn")
                    yield Static(" [3] QUEUE ", id="tab_queue_btn",    classes="tab_btn")

                with ContentSwitcher(initial="search_view", id="content_area"):

                    # SEARCH
                    with Vertical(id="search_view"):
                        yield Input(
                            placeholder="  🔍  Search YouTube Music and press Enter...",
                            id="search_input"
                        )
                        yield Label(
                            "Enter → Play instantly    |    a → Add to playlist",
                            id="search_hint"
                        )
                        yield ListView(id="search_results")

                    # LIBRARY
                    with Horizontal(id="library_view"):
                        with Vertical(id="playlist_col"):
                            yield Label("PLAYLISTS", id="pl_section_label", classes="tab_btn")
                            yield Input(placeholder="  + New playlist name…", id="new_pl_input")
                            yield Label("Enter → Open    d → Delete    e → Export", id="pl_hint")
                            yield ListView(id="library_list")
                        with Vertical(id="tracks_col"):
                            yield Label("─── SELECT A PLAYLIST ───", id="playlist_detail_title")
                            yield ListView(id="playlist_detail_list")

                    # QUEUE
                    with Vertical(id="queue_view"):
                        yield Label("NOW IN QUEUE", id="queue_title")
                        yield ListView(id="active_queue")
                        yield Label("Enter → Jump    d → Remove", id="queue_hint")

        yield Footer()

    # ── mount ───────────────────────────────────────

    def on_mount(self):
        self.screen.add_class(self._themes[self._tidx])
        self._refresh_library_view()
        self.query_one("#vol_bar", ProgressBar).update(progress=self.volume)
        self.query_one("#search_input", Input).focus()

    # ── tab switching ────────────────────────────────

    def _switch_tab(self, tab: str):
        self.current_tab = tab
        sw = self.query_one("#content_area", ContentSwitcher)
        sw.current = f"{tab}_view"
        for btn_id, name in [
            ("tab_search_btn", "search"),
            ("tab_library_btn", "library"),
            ("tab_queue_btn", "queue"),
        ]:
            btn = self.query_one(f"#{btn_id}", Static)
            if name == tab:
                btn.add_class("active")
            else:
                btn.remove_class("active")

        # auto-focus
        if tab == "search":
            self.query_one("#search_input", Input).focus()
        elif tab == "library":
            self.query_one("#library_list", ListView).focus()
        elif tab == "queue":
            self.query_one("#active_queue", ListView).focus()

    def action_tab_search(self):  self._switch_tab("search")
    def action_tab_library(self): self._switch_tab("library")
    def action_tab_queue(self):   self._switch_tab("queue")

    # ── volume reactive ─────────────────────────────

    def watch_volume(self, val: int):
        try:
            self.query_one("#vol_bar", ProgressBar).update(progress=val)
            self.query_one("#vol_label", Label).update(f"VOL {val:3d}")
        except Exception:
            pass

    def action_vol_up(self):
        self.volume = min(130, self.volume + 5)
        self.player.set_volume(self.volume)

    def action_vol_down(self):
        self.volume = max(0, self.volume - 5)
        self.player.set_volume(self.volume)

    # ── theme ────────────────────────────────────────

    def action_cycle_theme(self):
        self.screen.remove_class(self._themes[self._tidx])
        self._tidx = (self._tidx + 1) % len(self._themes)
        self.screen.add_class(self._themes[self._tidx])

    # ── search ───────────────────────────────────────

    async def on_input_submitted(self, event: Input.Submitted):
        if event.control.id == "search_input":
            await self._do_search(event.value.strip())
        elif event.control.id == "new_pl_input":
            self._create_playlist(event.value.strip())
            event.control.value = ""

    @work(exclusive=True)
    async def _do_search(self, query: str):
        if not query:
            return
        self._set_status("Searching…")
        sv = self.query_one("#search_results", ListView)
        sv.clear()
        sv.append(ListItem(Label("  ◐ Searching…"), name="loading"))

        try:
            results = await asyncio.to_thread(self.yt.search, query, filter="songs")
        except Exception as exc:
            sv.clear()
            sv.append(ListItem(Label(f"  Error: {exc}"), name="err"))
            self._set_status("Search failed")
            return

        sv.clear()
        self.search_results = []
        for res in results[:25]:
            title   = res.get("title", "Unknown")
            artists = ", ".join(a["name"] for a in res.get("artists", []) if "name" in a)
            vid     = res.get("videoId")
            dur     = res.get("duration", "")
            if vid:
                display = f"{title}  —  {artists}"
                self.search_results.append({"title": display, "videoId": vid, "dur": dur})
                sv.append(ListItem(Label(f"  {display}  [{dur}]"), name=vid))

        self._set_status(f"{len(self.search_results)} results")
        sv.focus()

    # ── list events ──────────────────────────────────

    def on_list_view_selected(self, event: ListView.Selected):
        lid = event.list_view.id

        if lid == "search_results":
            idx = event.list_view.index
            if idx is not None and 0 <= idx < len(self.search_results):
                track = self.search_results[idx]
                self.queue     = [track]
                self.queue_idx = -1
                self._refresh_queue_view()
                self._play_track(0)

        elif lid == "library_list":
            idx = event.list_view.index
            if idx is not None:
                names = list(self.library.keys())
                if 0 <= idx < len(names):
                    self.active_pl = names[idx]
                    self._refresh_library_view()
                    self._refresh_detail_view()
                    self.query_one("#playlist_detail_list", ListView).focus()

        elif lid == "playlist_detail_list":
            idx = event.list_view.index
            if idx is not None and self.active_pl in self.library:
                self.queue     = list(self.library[self.active_pl])
                self.queue_idx = -1
                self._refresh_queue_view()
                self._play_track(idx)
                self._switch_tab("queue")

        elif lid == "active_queue":
            idx = event.list_view.index
            if idx is not None:
                self._play_track(idx)

    # ── playback ─────────────────────────────────────

    def _play_track(self, idx: int):
        if not (0 <= idx < len(self.queue)):
            return
        self.queue_idx = idx
        track = self.queue[idx]
        url   = f"https://www.youtube.com/watch?v={track['videoId']}"

        self.query_one("#track_title", Label).update(track["title"])
        self.query_one("#track_artist", Label).update("Buffering…")
        self.query_one("#progress", ProgressBar).update(progress=0)
        self.query_one("#visualizer", Visualizer).set_buffering()
        self._set_status("● BUFFERING")
        self._paused = False

        self.player.play(url)
        self.player.set_volume(self.volume)

    def action_play_next(self):
        if self.queue_idx + 1 < len(self.queue):
            self._play_track(self.queue_idx + 1)
        else:
            self.queue_idx = -1
            self.query_one("#track_title", Label).update("Queue finished")
            self.query_one("#track_artist", Label).update("")
            self.query_one("#visualizer", Visualizer).set_idle()
            self._set_status("● IDLE")

    def action_toggle_pause(self):
        self._paused = self.player.pause_toggle()
        vis = self.query_one("#visualizer", Visualizer)
        if self._paused:
            vis.set_idle()
            self._set_status("⏸ PAUSED")
        else:
            vis.set_playing()
            self._set_status("▶ PLAYING")

    def action_seek_fwd(self):  self.player.seek(10)
    def action_seek_back(self): self.player.seek(-10)

    # ── add track to playlist ─────────────────────────

    def action_add_track(self):
        if self.current_tab != "search":
            return
        sv  = self.query_one("#search_results", ListView)
        idx = sv.index
        if idx is None or not (0 <= idx < len(self.search_results)):
            self._set_status("Select a search result first")
            return
        track = self.search_results[idx]
        pls   = list(self.library.keys())

        def _cb(pl_name):
            if pl_name:
                self.library[pl_name].append(track)
                self._save_library()
                self._refresh_library_view()
                self._set_status(f"Added to «{pl_name}»")

        self.push_screen(PlaylistSelectModal(pls), _cb)

    # ── library/playlist management ───────────────────

    def _create_playlist(self, name: str):
        if not name or name in self.library:
            return
        self.library[name] = []
        self._save_library()
        self._refresh_library_view()
        self._set_status(f"Created playlist «{name}»")

    def action_delete_item(self):
        tab = self.current_tab

        if tab == "queue":
            lv  = self.query_one("#active_queue", ListView)
            idx = lv.index
            if idx is not None and 0 <= idx < len(self.queue):
                del self.queue[idx]
                self._refresh_queue_view()
                if self.queue_idx == idx:
                    self.player.stop()
                    self.query_one("#visualizer", Visualizer).set_idle()
                    self._set_status("● IDLE")
                    self.queue_idx = -1
                elif self.queue_idx > idx:
                    self.queue_idx -= 1

        elif tab == "library":
            detail_lv = self.query_one("#playlist_detail_list", ListView)
            lib_lv    = self.query_one("#library_list", ListView)

            if detail_lv.has_focus:
                idx = detail_lv.index
                pl  = self.library.get(self.active_pl, [])
                if idx is not None and 0 <= idx < len(pl):
                    del pl[idx]
                    self._save_library()
                    self._refresh_detail_view()
                    self._refresh_library_view()
            elif lib_lv.has_focus:
                idx   = lib_lv.index
                names = list(self.library.keys())
                if idx is not None and 0 <= idx < len(names) and len(self.library) > 1:
                    del self.library[names[idx]]
                    if self.active_pl == names[idx]:
                        self.active_pl = list(self.library.keys())[0]
                    self._save_library()
                    self._refresh_library_view()
                    self._refresh_detail_view()

    def action_export_pl(self):
        lv  = self.query_one("#library_list", ListView)
        idx = lv.index
        if idx is None:
            return
        names = list(self.library.keys())
        if 0 <= idx < len(names):
            name = names[idx]
            path = os.path.join(EXPORTS_DIR, f"{name}.json")
            try:
                open(path, "w").write(json.dumps(self.library[name], indent=2))
                self._set_status(f"Exported → {path}")
            except Exception:
                self._set_status("Export failed")

    # ── view refresh helpers ──────────────────────────

    def _refresh_library_view(self):
        lv = self.query_one("#library_list", ListView)
        lv.clear()
        for name in self.library:
            prefix = "▶ " if name == self.active_pl else "  "
            count  = len(self.library[name])
            lv.append(ListItem(Label(f"{prefix}{name}  ({count} tracks)"), name=name))

    def _refresh_detail_view(self):
        lv = self.query_one("#playlist_detail_list", ListView)
        lv.clear()
        title_lbl = self.query_one("#playlist_detail_title", Label)
        if self.active_pl not in self.library:
            title_lbl.update("─── SELECT A PLAYLIST ───")
            return
        title_lbl.update(f"── {self.active_pl} ──")
        for track in self.library[self.active_pl]:
            lv.append(ListItem(Label(f"  {track['title']}"), name=track["videoId"]))

    def _refresh_queue_view(self):
        lv = self.query_one("#active_queue", ListView)
        lv.clear()
        for i, track in enumerate(self.queue):
            marker = "▶ " if i == self.queue_idx else "  "
            lv.append(ListItem(Label(f"{marker}{track['title']}"), name=track["videoId"]))

    # ── status bar helper ─────────────────────────────

    def _set_status(self, msg: str):
        try:
            self.query_one("#status_bar", Label).update(msg)
        except Exception:
            pass

    # ── player callback (from background thread) ──────

    def _player_cb(self, event: str, value):
        if event == "percent_pos":
            def _upd():
                try:
                    vis = self.query_one("#visualizer", Visualizer)
                    if vis._state == "buffering":
                        vis.set_playing(toggle_art=True)
                        self.query_one("#track_artist", Label).update(
                            self.queue[self.queue_idx]["title"].split("—")[-1].strip()
                            if self.queue_idx >= 0 else ""
                        )
                        self._set_status("▶ PLAYING")
                    self.query_one("#progress", ProgressBar).update(progress=value)
                except Exception:
                    pass
            self.call_from_thread(_upd)

        elif event == "eof":
            self.call_from_thread(self.action_play_next)

    def on_unmount(self):
        self.player.stop()
