"""
PHANTOM PLAYER — Clean Sci-Fi Terminal Music Player
Search · Play · Autoplay Radio · Procedural Animations
"""

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Footer, Input, Static, ProgressBar, Label, ListView, ListItem
from textual.binding import Binding
from textual import work
from ytmusicapi import YTMusic
import asyncio
import math
import os

from player import PhantomPlayer

# ─────────────────────────────────────────────────────────────────────────────
#  IDLE SPLASH ART
# ─────────────────────────────────────────────────────────────────────────────

IDLE_ART = """\

 ██████╗ ██╗  ██╗ █████╗ ███╗  ██╗████████╗ ██████╗ ███╗  ███╗
 ██╔══██╗██║  ██║██╔══██╗████╗ ██║╚══██╔══╝██╔═══██╗████╗████║
 ██████╔╝███████║███████║██╔██╗██║   ██║   ██║   ██║██╔████╔██║
 ██╔═══╝ ██╔══██║██╔══██║██║╚████║   ██║   ██║   ██║██║╚██╔╝██║
 ██║     ██║  ██║██║  ██║██║ ╚███║   ██║   ╚██████╔╝██║ ╚═╝ ██║
 ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚══╝  ╚═╝    ╚═════╝ ╚═╝     ╚═╝

                     P L A Y E R
                   ▶  READY TO STREAM  ◀
"""

# ─────────────────────────────────────────────────────────────────────────────
#  VISUALIZER  —  4 procedural animation modes
# ─────────────────────────────────────────────────────────────────────────────

class Visualizer(Static):
    """Procedural sci-fi music visualizer (BARS / WAVE / RADAR / PULSE)."""

    MODES = ["BARS", "WAVE", "RADAR", "PULSE"]
    W = 54   # render width in characters
    H = 10   # render height in rows

    def __init__(self, *args, **kwargs):
        super().__init__(IDLE_ART, *args, **kwargs)
        self._t     = 0.0
        self._mode  = 0
        self._state = "idle"   # idle | buffering | playing
        self._buf   = 0

    def on_mount(self):
        self.set_interval(0.07, self._tick)

    # ── public API ────────────────────────────────────────────────────────────

    def set_playing(self):
        self._state = "playing"

    def set_buffering(self):
        self._state = "buffering"
        self._buf = 0

    def set_idle(self):
        self._state = "idle"
        self.update(IDLE_ART)

    def cycle_mode(self) -> str:
        self._mode = (self._mode + 1) % len(self.MODES)
        self._t = 0.0
        return self.MODES[self._mode]

    # ── internal tick ─────────────────────────────────────────────────────────

    def _tick(self):
        if self._state == "playing":
            self._t += 0.07
            self.update(self._frame())
        elif self._state == "buffering":
            self._buf += 1
            sp = "◐◓◑◒"[self._buf % 4]
            self.update(f"\n\n\n\n      {sp}  LOADING…\n\n\n\n\n")

    def _frame(self):
        m = self._mode
        if m == 0: return self._bars()
        if m == 1: return self._wave()
        if m == 2: return self._radar()
        return self._pulse()

    # ── BARS ─────────────────────────────────────────────────────────────────

    def _bars(self):
        t, N, H = self._t, self.W // 2, self.H
        RAMP = " ░▒▓█"

        hs = []
        for i in range(N):
            v = (
                abs(math.sin(t * 2.3 + i * 0.55)) * 0.50 +
                abs(math.sin(t * 1.6 + i * 0.82)) * 0.30 +
                abs(math.sin(t * 3.7 + i * 0.27)) * 0.20
            )
            hs.append(max(1, int(v * H)))

        rows = []
        for row in range(H - 1, -1, -1):
            line = " "
            for h in hs:
                if h > row:
                    pct = (h - row) / max(1, h)
                    lvl = max(1, min(4, int(pct * 4) + 1))
                    line += RAMP[lvl] + " "
                else:
                    line += "  "
            rows.append(line)
        return "\n".join(rows)

    # ── WAVE ─────────────────────────────────────────────────────────────────

    def _wave(self):
        t, W, H = self._t, self.W, self.H
        cy = H / 2
        rows = []
        for y in range(H):
            line = ""
            for x in range(W):
                w = (
                    math.sin(x * 0.22 - t * 2.8) * 0.42 +
                    math.sin(x * 0.38 - t * 1.9) * 0.30 +
                    math.sin(x * 0.60 - t * 3.5) * 0.12
                ) * H * 0.48
                d = abs(y - cy - w)
                c = ("█" if d < 0.35
                     else "▓" if d < 0.80
                     else "▒" if d < 1.50
                     else "░" if d < 2.40
                     else " ")
                line += c
            rows.append(line)
        return "\n".join(rows)

    # ── RADAR ─────────────────────────────────────────────────────────────────

    def _radar(self):
        t, W, H = self._t, self.W, self.H
        cx, cy = W / 2, H / 2
        aspect = 2.4          # terminal char aspect ratio correction
        R = min(cx, cy * aspect) - 1
        sweep = (t * 2.2) % (2 * math.pi)
        rows = []
        for y in range(H):
            line = ""
            for x in range(W):
                dx, dy = x - cx, (y - cy) * aspect
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > R + 0.8:
                    line += " "
                    continue
                if dist < 0.9:
                    line += "◎"
                    continue
                if (abs(dist - R * 0.33) < 0.55 or
                        abs(dist - R * 0.66) < 0.55 or
                        abs(dist - R) < 0.55):
                    line += "·"
                    continue
                ang  = math.atan2(dy, dx) % (2 * math.pi)
                diff = (sweep - ang) % (2 * math.pi)
                c = ("█" if diff < 0.18
                     else "▓" if diff < 0.55
                     else "▒" if diff < 1.30
                     else "░" if diff < 2.80
                     else " ")
                line += c
            rows.append(line)
        return "\n".join(rows)

    # ── PULSE ─────────────────────────────────────────────────────────────────

    def _pulse(self):
        t, W, H = self._t, self.W, self.H
        cx, cy = W / 2, H / 2
        rows = []
        for y in range(H):
            line = ""
            for x in range(W):
                dx, dy = x - cx, (y - cy) * 2.5
                dist = math.sqrt(dx * dx + dy * dy)
                c = " "
                for k in range(5):
                    phase = k * math.pi * 0.4
                    r = abs(math.sin(t * 2.1 + phase)) * 10 + k * 2.8 + 1.5
                    d = abs(dist - r)
                    if d < 0.45:   c = "█"; break
                    elif d < 0.90: c = "▓"; break
                    elif d < 1.70: c = "░"; break
                if dist < 1.0:
                    c = "◉"
                line += c
            rows.append(line)
        return "\n".join(rows)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────────────────────────────────────

class PhantomUI(App):
    """Phantom Player — minimal, single-screen sci-fi music terminal."""

    TITLE = "PHANTOM PLAYER"

    CSS = """
/* ── BASE LAYOUT ─────────────────────────────────────────────────────── */
Screen {
    layout: vertical;
}

#viz {
    height: 12;
    text-align: center;
    content-align: center middle;
    padding: 0 1;
}

#info_bar {
    height: 2;
    text-align: center;
    content-align: center middle;
    text-style: bold;
    padding: 0 2;
}

#progress {
    height: 1;
    margin: 0 4;
}

Horizontal#vol_row {
    height: 1;
    align: center middle;
    margin: 0 4 1 4;
}

#vol_label {
    width: 8;
    height: 1;
}

#vol_bar {
    width: 24;
    height: 1;
}

#status {
    height: 1;
    text-align: center;
    text-style: italic;
}

#divider {
    height: 1;
    margin: 0;
}

#search {
    height: 3;
    border: none;
    padding: 0 2;
}

#results {
    height: 1fr;
}

ListItem {
    padding: 0 2;
}

/* ── THEME: HACKER (default) ──────────────────────────────────────────── */
Screen.hacker                         { background: #000000; color: #00ff41; }
Screen.hacker Header                  { background: #000000; color: #00ff41; }
Screen.hacker Footer                  { background: #001100; color: #009922; }
Screen.hacker #viz                    { color: #00ff41; }
Screen.hacker #info_bar               { color: #00cc33; }
Screen.hacker #status                 { color: #007711; }
Screen.hacker #divider                { color: #003300; }
Screen.hacker #search                 { background: #000800; color: #00ff41; border-bottom: solid #00ff41; }
Screen.hacker #search:focus           { border-bottom: double #00ff41; }
Screen.hacker ListView                { background: #000000; }
Screen.hacker ListItem:hover          { background: #001a00; }
Screen.hacker ListItem.--highlight    { background: #002200; color: #00ff41; }
Screen.hacker ProgressBar > Bar > .bar--bar { color: #00ff41; }
Screen.hacker ProgressBar > Bar       { background: #002200; }

/* ── THEME: CYBERPUNK ────────────────────────────────────────────────── */
Screen.cyberpunk                      { background: #06000d; color: #ff2fff; }
Screen.cyberpunk Footer               { background: #0d0014; color: #cc00cc; }
Screen.cyberpunk #viz                 { color: #ff00ff; }
Screen.cyberpunk #info_bar            { color: #ff55ff; }
Screen.cyberpunk #status              { color: #660066; }
Screen.cyberpunk #divider             { color: #330033; }
Screen.cyberpunk #search              { background: #0d0014; color: #ff00ff; border-bottom: solid #ff00ff; }
Screen.cyberpunk #search:focus        { border-bottom: double #ff00ff; }
Screen.cyberpunk ListView             { background: #06000d; }
Screen.cyberpunk ListItem:hover       { background: #1a0022; }
Screen.cyberpunk ListItem.--highlight { background: #220033; color: #ff00ff; }
Screen.cyberpunk ProgressBar > Bar > .bar--bar { color: #ff00ff; }
Screen.cyberpunk ProgressBar > Bar    { background: #330033; }

/* ── THEME: NORD ─────────────────────────────────────────────────────── */
Screen.nord                           { background: #2e3440; color: #d8dee9; }
Screen.nord Footer                    { background: #272c36; color: #81a1c1; }
Screen.nord #viz                      { color: #88c0d0; }
Screen.nord #info_bar                 { color: #88c0d0; }
Screen.nord #status                   { color: #4c566a; }
Screen.nord #divider                  { color: #3b4252; }
Screen.nord #search                   { background: #3b4252; color: #eceff4; border-bottom: solid #88c0d0; }
Screen.nord #search:focus             { border-bottom: double #88c0d0; }
Screen.nord ListView                  { background: #2e3440; }
Screen.nord ListItem:hover            { background: #3b4252; }
Screen.nord ListItem.--highlight      { background: #4c566a; color: #eceff4; }
Screen.nord ProgressBar > Bar > .bar--bar { color: #88c0d0; }
Screen.nord ProgressBar > Bar         { background: #3b4252; }

/* ── THEME: VOID ─────────────────────────────────────────────────────── */
Screen.void                           { background: #080808; color: #cccccc; }
Screen.void Footer                    { background: #050505; color: #666666; }
Screen.void #viz                      { color: #aaaaaa; }
Screen.void #info_bar                 { color: #ffffff; }
Screen.void #status                   { color: #333333; }
Screen.void #divider                  { color: #1a1a1a; }
Screen.void #search                   { background: #111111; color: #cccccc; border-bottom: solid #aaaaaa; }
Screen.void #search:focus             { border-bottom: double #ffffff; }
Screen.void ListView                  { background: #080808; }
Screen.void ListItem:hover            { background: #141414; }
Screen.void ListItem.--highlight      { background: #1e1e1e; color: #ffffff; }
Screen.void ProgressBar > Bar > .bar--bar { color: #cccccc; }
Screen.void ProgressBar > Bar         { background: #222222; }
"""

    BINDINGS = [
        Binding("ctrl+q", "quit",       "Quit",    show=True),
        Binding("space",  "pause",      "Pause",   show=True),
        Binding("n",      "next",       "Next",    show=True),
        Binding("+",      "vol_up",     "Vol+",    show=True),
        Binding("=",      "vol_up",     "",        show=False),
        Binding("-",      "vol_down",   "Vol-",    show=True),
        Binding("v",      "anim",       "Anim",    show=True),
        Binding("t",      "theme",      "Theme",   show=True),
        Binding("r",      "radio",      "Radio",   show=True),
        Binding("right",  "seek_fwd",   "+10s",    show=False),
        Binding("left",   "seek_back",  "-10s",    show=False),
    ]

    def __init__(self):
        super().__init__()
        self.player  = PhantomPlayer(callback=self._player_cb)
        self.yt      = YTMusic()
        self.queue:   list = []
        self.queue_idx    = -1
        self.results: list = []
        self._paused      = False
        self._radio       = True
        self._volume      = 70
        self._themes      = ["hacker", "cyberpunk", "nord", "void"]
        self._tidx        = 0

    # ── compose ──────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Visualizer(id="viz")
        yield Label("", id="info_bar")
        yield ProgressBar(total=100, id="progress", show_eta=False)
        with Horizontal(id="vol_row"):
            yield Label("VOL  ", id="vol_label")
            yield ProgressBar(total=130, id="vol_bar", show_eta=False)
        yield Label("● IDLE  ·  📻 Radio ON", id="status")
        yield Label("─" * 60, id="divider")
        yield Input(placeholder="  ›  Search YouTube Music and press Enter…", id="search")
        yield ListView(id="results")
        yield Footer()

    def on_mount(self):
        self.screen.add_class(self._themes[self._tidx])
        self.query_one("#vol_bar", ProgressBar).update(progress=self._volume)
        self.query_one("#vol_label", Label).update(f"VOL {self._volume:3d}")
        self.query_one("#search", Input).focus()

    # ── search ────────────────────────────────────────────────────────────────

    async def on_input_submitted(self, event: Input.Submitted):
        q = event.value.strip()
        if not q:
            return
        lv = self.query_one("#results", ListView)
        lv.clear()
        lv.append(ListItem(Label("  ◐  Searching…")))
        self._do_search(q)

    @work(exclusive=True)
    async def _do_search(self, q: str):
        try:
            raw = await asyncio.to_thread(self.yt.search, q, filter="songs")
        except Exception as e:
            self.call_from_thread(self._show_err, str(e))
            return

        tracks = []
        for r in raw[:25]:
            vid = r.get("videoId")
            if not vid:
                continue
            title   = r.get("title", "Unknown")
            artists = ", ".join(a["name"] for a in r.get("artists", []) if "name" in a)
            dur     = r.get("duration", "?:??")
            display = f"{title}  —  {artists}" if artists else title
            tracks.append({"title": display, "videoId": vid, "dur": dur})

        self.call_from_thread(self._show_results, tracks)

    def _show_results(self, tracks: list):
        self.results = tracks
        lv = self.query_one("#results", ListView)
        lv.clear()
        for t in tracks:
            lv.append(ListItem(
                Label(f"  {t['title']}  [{t.get('dur', '')}]")
            ))
        if tracks:
            lv.focus()

    def _show_err(self, msg: str):
        lv = self.query_one("#results", ListView)
        lv.clear()
        lv.append(ListItem(Label(f"  ✗  {msg}")))

    # ── list selection ────────────────────────────────────────────────────────

    def on_list_view_selected(self, event: ListView.Selected):
        idx = event.list_view.index
        if idx is None or not (0 <= idx < len(self.results)):
            return
        track = self.results[idx]
        self.queue     = [track]
        self.queue_idx = -1
        self._play_track(0)

    # ── playback ──────────────────────────────────────────────────────────────

    def _play_track(self, idx: int):
        if not (0 <= idx < len(self.queue)):
            return
        self.queue_idx = idx
        track = self.queue[idx]
        url   = f"https://www.youtube.com/watch?v={track['videoId']}"

        self.query_one("#viz",      Visualizer).set_buffering()
        self.query_one("#info_bar", Label).update(f"⌛  {track['title']}")
        self.query_one("#progress", ProgressBar).update(progress=0)
        self._set_status("● BUFFERING")
        self._paused = False

        self.player.play(url)
        self.player.set_volume(self._volume)

    def action_next(self):
        """Advance to next queued track, or fetch radio if near end."""
        nxt = self.queue_idx + 1
        if nxt < len(self.queue):
            self._play_track(nxt)
            if self._radio and nxt >= len(self.queue) - 2:
                self._fetch_radio()
        elif self._radio and self.queue:
            self._fetch_radio()
        else:
            self._idle()

    def _idle(self):
        self.queue_idx = -1
        self.player.stop()
        self.query_one("#viz",      Visualizer).set_idle()
        self.query_one("#info_bar", Label).update("")
        self.query_one("#progress", ProgressBar).update(progress=0)
        self._set_status("● IDLE  ·  📻 Radio " + ("ON" if self._radio else "OFF"))

    def action_pause(self):
        self._paused = self.player.pause_toggle()
        vis = self.query_one("#viz", Visualizer)
        if self._paused:
            vis.set_idle()
            self._set_status("⏸  PAUSED")
        else:
            vis.set_playing()
            self._set_status("▶  PLAYING")

    def action_seek_fwd(self):  self.player.seek(10)
    def action_seek_back(self): self.player.seek(-10)

    def action_vol_up(self):
        self._volume = min(130, self._volume + 5)
        self.player.set_volume(self._volume)
        self._update_volume()

    def action_vol_down(self):
        self._volume = max(0, self._volume - 5)
        self.player.set_volume(self._volume)
        self._update_volume()

    def _update_volume(self):
        self.query_one("#vol_bar",   ProgressBar).update(progress=self._volume)
        self.query_one("#vol_label", Label).update(f"VOL {self._volume:3d}")

    # ── radio autoplay ─────────────────────────────────────────────────────────

    def action_radio(self):
        self._radio = not self._radio
        label = "ON" if self._radio else "OFF"
        self._set_status(f"📻 Radio {label}")

    @work(exclusive=False)
    async def _fetch_radio(self):
        """Background worker: fetch related tracks via YTMusic watch playlist."""
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
                def _add():
                    was_empty = self.queue_idx == -1
                    self.queue.extend(new_tracks)
                    self._set_status(f"📻 Radio: +{len(new_tracks)} tracks added")
                    if was_empty and self.queue:
                        self._play_track(0)
                self.call_from_thread(_add)
        except Exception:
            pass  # Radio is best-effort

    # ── theme & animation ──────────────────────────────────────────────────────

    def action_theme(self):
        self.screen.remove_class(self._themes[self._tidx])
        self._tidx = (self._tidx + 1) % len(self._themes)
        self.screen.add_class(self._themes[self._tidx])

    def action_anim(self):
        name = self.query_one("#viz", Visualizer).cycle_mode()
        self._set_status(f"Animation: {name}")

    # ── player callback (from background thread) ───────────────────────────────

    def _player_cb(self, event: str, value):
        if event == "percent_pos":
            def _upd():
                try:
                    vis = self.query_one("#viz", Visualizer)
                    # Transition from buffering → playing on first position update
                    if vis._state == "buffering":
                        vis.set_playing()
                        if 0 <= self.queue_idx < len(self.queue):
                            title = self.queue[self.queue_idx]["title"]
                            self.query_one("#info_bar", Label).update(
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

    # ── helpers ────────────────────────────────────────────────────────────────

    def _set_status(self, msg: str):
        try:
            self.query_one("#status", Label).update(msg)
        except Exception:
            pass

    def on_unmount(self):
        self.player.stop()
