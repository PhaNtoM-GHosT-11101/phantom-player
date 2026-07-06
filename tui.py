"""
PHANTOM PLAYER — Sci-Fi Terminal Music Player
Full-screen animation · Overlay search · Dual-color animations · System stats
"""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Input, Static, ProgressBar, Label, ListView, ListItem
from textual.screen import ModalScreen
from textual.binding import Binding
from textual import work
from ytmusicapi import YTMusic
import asyncio
import math
import psutil
import os

from player import PhantomPlayer

# ─────────────────────────────────────────────────────────────────────────────
#  THEME DEFINITIONS  (bg, dark, accent1, accent2, muted)
# ─────────────────────────────────────────────────────────────────────────────

THEMES = {
    "hacker": {
        "bg":      "#000000",
        "bg2":     "#010a01",
        "a1":      "#00ff41",
        "a2":      "#aaff00",
        "muted":   "#005511",
        "rule":    "#003300",
        "footer":  "#001a00",
    },
    "cyberpunk": {
        "bg":      "#05000f",
        "bg2":     "#0a0018",
        "a1":      "#00f5ff",
        "a2":      "#ff00ff",
        "muted":   "#004455",
        "rule":    "#110022",
        "footer":  "#0a0018",
    },
    "synthwave": {
        "bg":      "#0d0010",
        "bg2":     "#130018",
        "a1":      "#ff6b2b",
        "a2":      "#ff2d78",
        "muted":   "#551133",
        "rule":    "#2a0022",
        "footer":  "#100014",
    },
    "void": {
        "bg":      "#070710",
        "bg2":     "#0c0c1a",
        "a1":      "#c8d6e5",
        "a2":      "#4a90d9",
        "muted":   "#2a3a55",
        "rule":    "#141428",
        "footer":  "#050510",
    },
}

THEME_ORDER = ["hacker", "cyberpunk", "synthwave", "void"]

# ─────────────────────────────────────────────────────────────────────────────
#  VISUALIZER — procedural animations with dual-color Rich markup
# ─────────────────────────────────────────────────────────────────────────────

class Visualizer(Static):
    """Procedural sci-fi visualizer: BARS | WAVE | RADAR | PULSE.

    CPU-efficient: all frames are pre-computed once in a thread; the
    60 Hz tick only does a list-index read and a widget.update() call.
    """

    MODES   = ["BARS", "WAVE", "RADAR", "PULSE"]
    W       = 46      # columns  (was 60 — 40% fewer pixels)
    H       = 11      # rows     (was 16 — 30% fewer pixels)
    NFRAMES = 40      # pre-computed frames per mode
    TICK    = 0.12    # seconds between ticks (~8 fps, was 16 fps)

    def __init__(self, *args, **kwargs):
        super().__init__("", *args, **kwargs)
        self._fidx   = 0
        self._mode   = 0
        self._state  = "idle"
        self._buf    = 0
        self._a1     = "#00ff41"
        self._a2     = "#aaff00"
        # mode-index → list of pre-rendered frame strings
        self._cache: dict[int, list[str]] = {}
        self._idle_cache: list[str] = []
        self._idle_tick  = 0

    def on_mount(self):
        self._precompute()                          # kick off background build
        self.set_interval(self.TICK, self._tick)

    # ── public API ────────────────────────────────────────────────────────────

    def set_colors(self, a1: str, a2: str):
        self._a1, self._a2 = a1, a2
        self._cache.clear()          # invalidate; new colors need rebuild
        self._idle_cache.clear()
        self._precompute()

    def set_playing(self):
        self._state = "playing"
        self._fidx  = 0

    def set_buffering(self):
        self._state = "buffering"
        self._buf   = 0

    def set_idle(self):
        self._state = "idle"

    def cycle_mode(self) -> str:
        self._mode  = (self._mode + 1) % len(self.MODES)
        self._fidx  = 0
        return self.MODES[self._mode]

    # ── background pre-computation ────────────────────────────────────────────

    @work(exclusive=True, thread=True)
    def _precompute(self):
        """Build all frame caches in a worker thread — never blocks the UI."""
        a1, a2 = self._a1, self._a2

        # idle breathing rings
        idle = []
        for i in range(self.NFRAMES):
            t = i * (math.pi * 2 / self.NFRAMES)
            idle.append(self._build_idle(t, a1, a2))
        self._idle_cache = idle

        # each animation mode
        for m in range(len(self.MODES)):
            frames = []
            for i in range(self.NFRAMES):
                t = i * (self.TICK * 1.4)   # slightly faster feel
                if   m == 0: frames.append(self._build_bars(t, a1, a2))
                elif m == 1: frames.append(self._build_wave(t, a1, a2))
                elif m == 2: frames.append(self._build_radar(t, a1, a2))
                else:        frames.append(self._build_pulse(t, a1, a2))
            self._cache[m] = frames

    # ── tick — zero math, pure list lookup ───────────────────────────────────

    def _tick(self):
        if self._state == "playing":
            frames = self._cache.get(self._mode)
            if frames:
                self.update(frames[self._fidx % len(frames)])
                self._fidx += 1
        elif self._state == "idle":
            # Update idle every 5 ticks (~1.6 s per cycle) — very cheap
            self._idle_tick += 1
            if self._idle_tick % 3 == 0 and self._idle_cache:
                idx = (self._idle_tick // 3) % len(self._idle_cache)
                self.update(self._idle_cache[idx])
        elif self._state == "buffering":
            self._buf += 1
            sp = "◐◓◑◒"[self._buf % 4]
            self.update(
                f"\n\n\n\n\n"
                f"[bold {self._a1}]      {sp}  BUFFERING…[/]\n\n\n\n\n"
            )

    # ── frame builders (called once per frame slot at startup) ─────────────────

    @staticmethod
    def _build_idle(t: float, a1: str, a2: str) -> str:
        W, H = 46, 11
        cx, cy = W / 2, H / 2
        r  = math.sin(t) * 9 + 11
        r2 = math.sin(t + 1.2) * 5 + 5
        rows = []
        for y in range(H):
            row = ""
            for x in range(W):
                dx = x - cx; dy = (y - cy) * 2.6
                dist = math.sqrt(dx*dx + dy*dy)
                d  = abs(dist - r)
                d2 = abs(dist - r2)
                if dist < 1.0:    row += f"[bold {a2}]◉[/]"
                elif d  < 0.5:    row += f"[{a1}]█[/]"
                elif d  < 1.1:    row += f"[{a1}]▒[/]"
                elif d2 < 0.5:    row += f"[{a2}]▓[/]"
                elif d2 < 1.1:    row += f"[{a2}]░[/]"
                else:             row += " "
            rows.append(row)
        return "\n".join(rows)

    @staticmethod
    def _build_bars(t: float, a1: str, a2: str) -> str:
        W, H = 46, 11
        N    = W // 2
        RAMP = " ░▒▓█"
        hs   = [max(1, int((
                    abs(math.sin(t * 2.3 + i * 0.55)) * 0.50 +
                    abs(math.sin(t * 1.6 + i * 0.82)) * 0.30 +
                    abs(math.sin(t * 3.7 + i * 0.27)) * 0.20
                ) * H)) for i in range(N)]
        mid  = H // 2
        rows = []
        for row in range(H - 1, -1, -1):
            col  = a2 if row >= mid else a1
            line = f"[{col}] "
            for h in hs:
                if h > row:
                    pct = (h - row) / max(1, h)
                    line += RAMP[max(1, min(4, int(pct * 4) + 1))] + " "
                else:
                    line += "  "
            line += "[/]"
            rows.append(line)
        return "\n".join(rows)

    @staticmethod
    def _build_wave(t: float, a1: str, a2: str) -> str:
        W, H = 46, 11
        cy   = H / 2
        rows = []
        for y in range(H):
            col  = a2 if y < cy else a1
            line = f"[{col}]"
            for x in range(W):
                wv = (
                    math.sin(x * 0.22 - t * 2.8) * 0.42 +
                    math.sin(x * 0.38 - t * 1.9) * 0.30 +
                    math.sin(x * 0.60 - t * 3.5) * 0.12
                ) * H * 0.45
                d = abs(y - cy - wv)
                line += ("█" if d < 0.35
                         else "▓" if d < 0.80
                         else "▒" if d < 1.50
                         else "░" if d < 2.40
                         else " ")
            line += "[/]"
            rows.append(line)
        return "\n".join(rows)

    @staticmethod
    def _build_radar(t: float, a1: str, a2: str) -> str:
        W, H  = 46, 11
        cx, cy = W / 2, H / 2
        R      = min(cx, cy * 2.4) - 1
        sweep  = (t * 2.2) % (2 * math.pi)
        rows   = []
        for y in range(H):
            line = ""
            for x in range(W):
                dx, dy = x - cx, (y - cy) * 2.4
                dist   = math.sqrt(dx*dx + dy*dy)
                if dist > R + 0.8:          line += " ";  continue
                if dist < 0.9:              line += f"[bold {a2}]◎[/]"; continue
                if (abs(dist-R*0.33)<0.55 or
                        abs(dist-R*0.66)<0.55 or
                        abs(dist-R)<0.55):  line += f"[{a1}]·[/]"; continue
                ang  = math.atan2(dy, dx) % (2 * math.pi)
                diff = (sweep - ang) % (2 * math.pi)
                if   diff < 0.18: line += f"[bold {a2}]█[/]"
                elif diff < 0.55: line += f"[{a2}]▓[/]"
                elif diff < 1.30: line += f"[{a1}]▒[/]"
                elif diff < 2.80: line += f"[{a1}]░[/]"
                else:             line += " "
            rows.append(line)
        return "\n".join(rows)

    @staticmethod
    def _build_pulse(t: float, a1: str, a2: str) -> str:
        W, H  = 46, 11
        cx, cy = W / 2, H / 2
        # Pre-compute ring radii for this frame
        rings  = [
            (abs(math.sin(t * 2.1 + k * math.pi * 0.4)) * 8 + k * 2.5 + 1.5,
             a2 if k % 2 == 0 else a1)
            for k in range(5)
        ]
        rows   = []
        for y in range(H):
            line = ""
            for x in range(W):
                dx, dy = x - cx, (y - cy) * 2.5
                dist   = math.sqrt(dx*dx + dy*dy)
                if dist < 1.0:
                    line += f"[bold {a2}]◉[/]"; continue
                c = " "; col = a1
                for r, rc in rings:
                    d = abs(dist - r)
                    if   d < 0.45: c = "█"; col = rc; break
                    elif d < 0.90: c = "▓"; col = rc; break
                    elif d < 1.70: c = "░"; col = rc; break
                line += f"[bold {col}]{c}[/]" if c != " " else " "
            rows.append(line)
        return "\n".join(rows)


# ─────────────────────────────────────────────────────────────────────────────
#  SEARCH OVERLAY  (modal screen on top of the running animation)
# ─────────────────────────────────────────────────────────────────────────────

class SearchOverlay(ModalScreen):
    """Full-screen search overlay. Animation keeps running beneath."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
    ]

    CSS = """
SearchOverlay {
    align: center middle;
}
#overlay_box {
    width: 80%;
    height: 80%;
    layout: vertical;
    border: double;
    padding: 1 2;
}
#overlay_title {
    height: 1;
    text-align: center;
    text-style: bold;
    margin-bottom: 1;
}
#overlay_input {
    height: 3;
    border: round;
    margin-bottom: 1;
}
#overlay_results {
    height: 1fr;
    border: round;
}
#overlay_hint {
    height: 1;
    text-align: center;
    margin-top: 1;
}
"""

    def __init__(self, theme_name: str, **kwargs):
        super().__init__(**kwargs)
        self._theme = theme_name
        self._results: list = []

    def compose(self) -> ComposeResult:
        th = THEMES[self._theme]
        with Vertical(id="overlay_box"):
            yield Label("  ›  SEARCH YOUTUBE MUSIC", id="overlay_title")
            yield Input(
                placeholder="  type song name and press Enter…",
                id="overlay_input"
            )
            yield ListView(id="overlay_results")
            yield Label("  [Esc] Close  ·  [Enter] Play", id="overlay_hint")

    def on_mount(self):
        th = THEMES[self._theme]
        self.query_one("#overlay_box").styles.border = ("double", th["a1"])
        self.query_one("#overlay_box").styles.background = th["bg2"]
        self.query_one("#overlay_title").styles.color = th["a1"]
        self.query_one("#overlay_input").styles.border = ("round", th["a1"])
        self.query_one("#overlay_input").styles.background = th["bg"]
        self.query_one("#overlay_input").styles.color = th["a1"]
        self.query_one("#overlay_results").styles.border = ("round", th["muted"])
        self.query_one("#overlay_results").styles.background = th["bg"]
        self.query_one("#overlay_hint").styles.color = th["muted"]
        self.query_one("#overlay_input").focus()

    async def on_input_submitted(self, event: Input.Submitted):
        q = event.value.strip()
        if not q:
            return
        lv = self.query_one("#overlay_results", ListView)
        lv.clear()
        lv.append(ListItem(Label("  ◐  Searching…")))
        self._search(q)

    @work(exclusive=True)
    async def _search(self, q: str):
        try:
            yt = YTMusic()
            raw = await asyncio.to_thread(yt.search, q, filter="songs")
        except Exception as e:
            lv = self.query_one("#overlay_results", ListView)
            lv.clear()
            lv.append(ListItem(Label(f"  ✗  {e}")))
            return

        tracks = []
        for r in raw[:20]:
            vid = r.get("videoId")
            if not vid:
                continue
            title   = r.get("title", "Unknown")
            artists = ", ".join(a["name"] for a in r.get("artists", []) if "name" in a)
            dur     = r.get("duration", "?:??")
            display = f"{title}  —  {artists}" if artists else title
            tracks.append({"title": display, "videoId": vid, "dur": dur})

        self._results = tracks
        lv = self.query_one("#overlay_results", ListView)
        lv.clear()
        for t in tracks:
            lv.append(ListItem(Label(f"  {t['title']}  [{t.get('dur', '')}]")))
        if tracks:
            lv.focus()

    def on_list_view_selected(self, event: ListView.Selected):
        idx = event.list_view.index
        if idx is None or not (0 <= idx < len(self._results)):
            return
        self.dismiss(self._results[idx])

    def action_dismiss(self):
        self.dismiss(None)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class PhantomUI(App):
    """Phantom Player — animation-first, single screen, overlay search."""

    TITLE = "PHANTOM PLAYER"

    BINDINGS = [
        Binding("ctrl+q", "quit",    "Quit",   show=True),
        Binding("s",      "search",  "Search", show=True),
        Binding("space",  "pause",   "Pause",  show=True),
        Binding("n",      "next",    "Next",   show=True),
        Binding("+",      "vol_up",  "Vol+",   show=True),
        Binding("=",      "vol_up",  "",       show=False),
        Binding("-",      "vol_down","Vol-",   show=True),
        Binding("v",      "anim",    "Anim",   show=True),
        Binding("t",      "theme",   "Theme",  show=True),
        Binding("r",      "radio",   "Radio",  show=True),
        Binding("right",  "seek_fwd","",       show=False),
        Binding("left",   "seek_back","",      show=False),
    ]

    # Inline CSS — generated dynamically per theme in on_mount
    CSS = """
Screen { layout: vertical; }

#viz {
    height: 1fr;
    content-align: center middle;
    text-align: center;
}

#bottom_strip {
    height: auto;
    layout: vertical;
    padding: 0 2;
}

#track_line {
    height: 1;
    text-align: center;
    text-style: bold;
    margin-bottom: 0;
}

#progress {
    height: 1;
    margin: 0 0;
}

#meta_row {
    height: 1;
    layout: horizontal;
    align: center middle;
}

#vol_label { width: 12; }
#vol_bar   { width: 18; }
#spacer    { width: 1fr; }
#sys_label { width: 24; text-align: right; }

#status {
    height: 1;
    text-align: center;
    text-style: italic;
    margin-top: 0;
}

Footer { height: 1; }

/* ── HACKER ───────────────────────────────────────── */
Screen.hacker                      { background: #000000; color: #00ff41; }
Screen.hacker #bottom_strip        { background: #010a01; border-top: solid #003300; }
Screen.hacker #track_line          { color: #00ff41; }
Screen.hacker #vol_label           { color: #aaff00; }
Screen.hacker #sys_label           { color: #005511; }
Screen.hacker #status              { color: #005511; }
Screen.hacker Footer               { background: #001a00; color: #005511; }
Screen.hacker ProgressBar > Bar > .bar--bar { color: #00ff41; }
Screen.hacker ProgressBar > Bar    { background: #003300; }

/* ── CYBERPUNK ────────────────────────────────────── */
Screen.cyberpunk                   { background: #05000f; color: #00f5ff; }
Screen.cyberpunk #bottom_strip     { background: #0a0018; border-top: solid #110022; }
Screen.cyberpunk #track_line       { color: #00f5ff; }
Screen.cyberpunk #vol_label        { color: #ff00ff; }
Screen.cyberpunk #sys_label        { color: #004455; }
Screen.cyberpunk #status           { color: #004455; }
Screen.cyberpunk Footer            { background: #0a0018; color: #004455; }
Screen.cyberpunk ProgressBar > Bar > .bar--bar { color: #00f5ff; }
Screen.cyberpunk ProgressBar > Bar { background: #110022; }

/* ── SYNTHWAVE ────────────────────────────────────── */
Screen.synthwave                   { background: #0d0010; color: #ff6b2b; }
Screen.synthwave #bottom_strip     { background: #130018; border-top: solid #2a0022; }
Screen.synthwave #track_line       { color: #ff6b2b; }
Screen.synthwave #vol_label        { color: #ff2d78; }
Screen.synthwave #sys_label        { color: #551133; }
Screen.synthwave #status           { color: #551133; }
Screen.synthwave Footer            { background: #100014; color: #551133; }
Screen.synthwave ProgressBar > Bar > .bar--bar { color: #ff6b2b; }
Screen.synthwave ProgressBar > Bar { background: #2a0022; }

/* ── VOID ─────────────────────────────────────────── */
Screen.void                        { background: #070710; color: #c8d6e5; }
Screen.void #bottom_strip          { background: #0c0c1a; border-top: solid #141428; }
Screen.void #track_line            { color: #c8d6e5; }
Screen.void #vol_label             { color: #4a90d9; }
Screen.void #sys_label             { color: #2a3a55; }
Screen.void #status                { color: #2a3a55; }
Screen.void Footer                 { background: #050510; color: #2a3a55; }
Screen.void ProgressBar > Bar > .bar--bar { color: #c8d6e5; }
Screen.void ProgressBar > Bar      { background: #141428; }
"""

    def __init__(self):
        super().__init__()
        self.player  = PhantomPlayer(callback=self._player_cb)
        self.yt      = YTMusic()
        self.queue:  list = []
        self.queue_idx    = -1
        self._paused      = False
        self._radio       = True
        self._volume      = 70
        self._tidx        = 0
        self._proc        = psutil.Process(os.getpid())

    def compose(self) -> ComposeResult:
        yield Visualizer(id="viz")
        with Vertical(id="bottom_strip"):
            yield Label("♪  PHANTOM PLAYER  ·  By Aditya Priyadarshi  ♪", id="track_line")
            yield ProgressBar(total=100, id="progress", show_eta=False)
            with Horizontal(id="meta_row"):
                yield Label("VOL  70", id="vol_label")
                yield ProgressBar(total=130, id="vol_bar", show_eta=False)
                yield Label("", id="spacer")
                yield Label("CPU 0%  RAM 0MB", id="sys_label")
            yield Label("● IDLE  ·  [s] Search  ·  📻 Radio ON", id="status")
        yield Footer()

    def on_mount(self):
        self._apply_theme()
        self.query_one("#vol_bar", ProgressBar).update(progress=self._volume)
        # Start system stats updater
        self.set_interval(2.0, self._update_sys_stats)
        self._update_sys_stats()

    # ── theming ──────────────────────────────────────────────────────────────

    def _apply_theme(self):
        name = THEME_ORDER[self._tidx]
        th   = THEMES[name]

        # Remove all theme classes, add current one
        for t in THEME_ORDER:
            self.screen.remove_class(t)
        self.screen.add_class(name)

        # Pass accent colors to visualizer for Rich markup coloring
        self.query_one("#viz", Visualizer).set_colors(th["a1"], th["a2"])

    # ── search overlay ────────────────────────────────────────────────────────

    def action_search(self):
        name = THEME_ORDER[self._tidx]
        def _on_result(track):
            if track:
                self.queue     = [track]
                self.queue_idx = -1
                self._play_track(0)
        self.push_screen(SearchOverlay(name), _on_result)

    # ── playback ──────────────────────────────────────────────────────────────

    def _play_track(self, idx: int):
        if not (0 <= idx < len(self.queue)):
            return
        self.queue_idx = idx
        track = self.queue[idx]
        url   = f"https://www.youtube.com/watch?v={track['videoId']}"

        self.query_one("#viz",        Visualizer).set_buffering()
        self.query_one("#track_line", Label).update(f"⌛  {track['title']}")
        self.query_one("#progress",   ProgressBar).update(progress=0)
        self._set_status("● BUFFERING…")
        self._paused = False

        self.player.play(url)
        self.player.set_volume(self._volume)

    def action_next(self):
        nxt = self.queue_idx + 1
        if nxt < len(self.queue):
            self._play_track(nxt)
            if self._radio and nxt >= len(self.queue) - 2:
                self._fetch_radio()
        elif self._radio and self.queue:
            self._fetch_radio()
        else:
            self._go_idle()

    def _go_idle(self):
        self.queue_idx = -1
        self.player.stop()
        self.query_one("#viz",        Visualizer).set_idle()
        self.query_one("#track_line", Label).update("♪  PHANTOM PLAYER  ·  By Aditya Priyadarshi  ♪")
        self.query_one("#progress",   ProgressBar).update(progress=0)
        self._set_status("● IDLE  ·  [s] Search  ·  📻 Radio " +
                         ("ON" if self._radio else "OFF"))

    def action_pause(self):
        self._paused = self.player.pause_toggle()
        vis = self.query_one("#viz", Visualizer)
        if self._paused:
            vis.set_idle()
            self._set_status("⏸  PAUSED  ·  [Space] Resume")
        else:
            vis.set_playing()
            self._set_status("▶  PLAYING")

    def action_seek_fwd(self):  self.player.seek(10)
    def action_seek_back(self): self.player.seek(-10)

    def action_vol_up(self):
        self._volume = min(130, self._volume + 5)
        self.player.set_volume(self._volume)
        self._refresh_vol()

    def action_vol_down(self):
        self._volume = max(0, self._volume - 5)
        self.player.set_volume(self._volume)
        self._refresh_vol()

    def _refresh_vol(self):
        self.query_one("#vol_bar",   ProgressBar).update(progress=self._volume)
        self.query_one("#vol_label", Label).update(f"VOL {self._volume:3d}")

    # ── radio ─────────────────────────────────────────────────────────────────

    def action_radio(self):
        self._radio = not self._radio
        self._set_status("📻 Radio " + ("ON" if self._radio else "OFF"))

    @work(exclusive=False)
    async def _fetch_radio(self):
        try:
            seed = next(
                (t["videoId"] for t in reversed(self.queue) if t.get("videoId")),
                None
            )
            if not seed:
                return
            res = await asyncio.to_thread(self.yt.get_watch_playlist, seed)
            existing = {t["videoId"] for t in self.queue}
            new_tracks = []
            for t in res.get("tracks", []):
                vid   = t.get("videoId")
                title = t.get("title", "")
                if not vid or vid in existing or not title:
                    continue
                artists = ", ".join(a["name"] for a in t.get("artists", []) if "name" in a)
                display = f"{title}  —  {artists}" if artists else title
                new_tracks.append({"title": display, "videoId": vid})
                existing.add(vid)
                if len(new_tracks) >= 5:
                    break
            if new_tracks:
                was_empty = self.queue_idx == -1
                self.queue.extend(new_tracks)
                self._set_status(f"📻 Radio: +{len(new_tracks)} tracks")
                if was_empty:
                    self._play_track(0)
        except Exception:
            pass

    # ── theme & animation ─────────────────────────────────────────────────────

    def action_theme(self):
        self._tidx = (self._tidx + 1) % len(THEME_ORDER)
        self._apply_theme()

    def action_anim(self):
        name = self.query_one("#viz", Visualizer).cycle_mode()
        self._set_status(f"Animation: {name}")

    # ── system stats ──────────────────────────────────────────────────────────

    def _update_sys_stats(self):
        try:
            # Main UI process stats
            cpu = self._proc.cpu_percent(interval=None)
            ram = self._proc.memory_info().rss
            
            # Add child processes (like mpv)
            for child in self._proc.children(recursive=True):
                try:
                    cpu += child.cpu_percent(interval=None)
                    ram += child.memory_info().rss
                except psutil.NoSuchProcess:
                    pass
                    
            ram_mb = ram // (1024 * 1024)
            self.query_one("#sys_label", Label).update(
                f"APP CPU {cpu:.1f}%  RAM {ram_mb}MB"
            )
        except Exception:
            pass

    # ── player callback (from background thread) ──────────────────────────────

    def _player_cb(self, event: str, value):
        if event == "percent_pos":
            def _upd():
                try:
                    vis = self.query_one("#viz", Visualizer)
                    if vis._state == "buffering":
                        vis.set_playing()
                        if 0 <= self.queue_idx < len(self.queue):
                            title = self.queue[self.queue_idx]["title"]
                            self.query_one("#track_line", Label).update(
                                f"♪  {title}  ♪"
                            )
                        self._set_status(
                            "▶  PLAYING  ·  📻 Radio " +
                            ("ON" if self._radio else "OFF")
                        )
                    self.query_one("#progress", ProgressBar).update(progress=value)
                except Exception:
                    pass
            self.call_from_thread(_upd)
        elif event == "eof":
            self.call_from_thread(self.action_next)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _set_status(self, msg: str):
        try:
            self.query_one("#status", Label).update(msg)
        except Exception:
            pass

    def on_unmount(self):
        self.player.stop()
