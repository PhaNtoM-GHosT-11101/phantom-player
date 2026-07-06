from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Static, ProgressBar, Label, ListView, ListItem, ContentSwitcher
from textual.reactive import reactive
from textual.binding import Binding
from ytmusicapi import YTMusic
import asyncio
import json
import os
import random

from player import PhantomPlayer

PLAYLIST_FILE = "playlist.json"
EXPORTS_DIR = "exports"

class PlaylistView(ListView):
    pass
    
class SearchResultsView(ListView):
    pass
    
class LibraryView(ListView):
    pass

class SciFiAnimation(Static):
    """A rotating sci-fi CD/Globe animation."""
    
    def on_mount(self) -> None:
        self.frames = [
            " [  |  ] ",
            " [  /  ] ",
            " [  -  ] ",
            " [  \  ] "
        ]
        self.frame_idx = 0
        self.state = "stopped"
        self.buffer_frame = 0
        self.update_bars()
        self.animation_timer = self.set_interval(0.1, self.tick, pause=True)

    def tick(self) -> None:
        self.update_bars()

    def update_bars(self):
        if self.state == "stopped":
            content = " [ --- ] "
        elif self.state == "buffering":
            self.buffer_frame += 1
            dots = "." * (self.buffer_frame % 4)
            content = f" [ LOAD{dots.ljust(3)} ] "
        else:
            content = self.frames[self.frame_idx]
            self.frame_idx = (self.frame_idx + 1) % len(self.frames)
            
        self.update(f"[bold]{content}[/]")

    def play(self):
        self.state = "playing"
        self.animation_timer.resume()
        
    def buffer(self):
        self.state = "buffering"
        self.animation_timer.resume()

    def pause(self):
        self.state = "stopped"
        self.animation_timer.pause()
        self.update_bars()

class PlayerUI(App):
    """A futuristic, minimalist TUI online music player with ContentSwitcher."""
    
    CSS = """
    #now_playing {
        height: 6;
        content-align: center middle;
    }
    #visualizer {
        height: 1;
        content-align: center middle;
        margin-bottom: 1;
    }
    #volume_container {
        layout: horizontal;
        align: center middle;
        height: 1;
        width: 100%;
        margin-bottom: 1;
    }
    #volume_label {
        width: 5;
        text-align: right;
        margin-right: 1;
    }
    #volume_bar {
        width: 30;
    }
    
    #switcher {
        height: 1fr;
    }
    
    .view_container {
        height: 100%;
        padding: 0 4;
    }
    
    .view_title {
        text-style: bold;
        margin-bottom: 1;
        width: 100%;
        text-align: center;
        border-bottom: dashed;
    }
    
    Input {
        border: none;
        height: 3;
        margin-bottom: 1;
    }
    ListView {
        height: 1fr;
    }
    ListItem {
        padding: 0 1;
    }

    /* THEME: HACKER */
    Screen.theme-hacker { background: #000000; color: #00ff00; }
    Screen.theme-hacker Header { background: #000000; color: #00ff00; border-bottom: solid #005500; }
    Screen.theme-hacker Footer { background: #000000; color: #00ff00; border-top: solid #005500; }
    Screen.theme-hacker #now_playing { background: #000000; border-bottom: solid #005500; }
    Screen.theme-hacker #volume_label { color: #00ff00; }
    Screen.theme-hacker .view_title { color: #00ff00; border-bottom: dashed #005500; }
    Screen.theme-hacker Input { border-bottom: solid #00ff00; background: #000000; color: #00ff00; }
    Screen.theme-hacker Input:focus { border-bottom: double #00ff00; background: #001100; }
    Screen.theme-hacker ListView { background: #000000; }
    Screen.theme-hacker ListItem:hover { background: #001100; }
    Screen.theme-hacker ListItem:focus { background: #00ff00; color: #000000; text-style: bold; }
    Screen.theme-hacker ProgressBar > Bar { color: #00ff00; }

    /* THEME: CYBERPUNK */
    Screen.theme-cyberpunk { background: #0d0d14; color: #ff00ff; }
    Screen.theme-cyberpunk Header { background: #0d0d14; color: #ff00ff; border-bottom: solid #880088; }
    Screen.theme-cyberpunk Footer { background: #0d0d14; color: #ff00ff; border-top: solid #880088; }
    Screen.theme-cyberpunk #now_playing { background: #0d0d14; border-bottom: solid #880088; }
    Screen.theme-cyberpunk #volume_label { color: #ff00ff; }
    Screen.theme-cyberpunk .view_title { color: #ff00ff; border-bottom: dashed #880088; }
    Screen.theme-cyberpunk Input { border-bottom: solid #ff00ff; background: #0d0d14; color: #ff00ff; }
    Screen.theme-cyberpunk Input:focus { border-bottom: double #ff00ff; background: #1a1a24; }
    Screen.theme-cyberpunk ListView { background: #0d0d14; }
    Screen.theme-cyberpunk ListItem:hover { background: #1a1a24; }
    Screen.theme-cyberpunk ListItem:focus { background: #ff00ff; color: #0d0d14; text-style: bold; }
    Screen.theme-cyberpunk ProgressBar > Bar { color: #ff00ff; }

    /* THEME: NORD */
    Screen.theme-nord { background: #2e3440; color: #88c0d0; }
    Screen.theme-nord Header { background: #2e3440; color: #88c0d0; border-bottom: solid #4c566a; }
    Screen.theme-nord Footer { background: #2e3440; color: #88c0d0; border-top: solid #4c566a; }
    Screen.theme-nord #now_playing { background: #2e3440; border-bottom: solid #4c566a; }
    Screen.theme-nord #volume_label { color: #88c0d0; }
    Screen.theme-nord .view_title { color: #88c0d0; border-bottom: dashed #4c566a; }
    Screen.theme-nord Input { border-bottom: solid #88c0d0; background: #2e3440; color: #88c0d0; }
    Screen.theme-nord Input:focus { border-bottom: double #88c0d0; background: #3b4252; }
    Screen.theme-nord ListView { background: #2e3440; }
    Screen.theme-nord ListItem:hover { background: #3b4252; }
    Screen.theme-nord ListItem:focus { background: #88c0d0; color: #2e3440; text-style: bold; }
    Screen.theme-nord ProgressBar > Bar { color: #88c0d0; }

    /* THEME: VOID */
    Screen.theme-void { background: #000000; color: #ffffff; }
    Screen.theme-void Header { background: #000000; color: #ffffff; border-bottom: solid #555555; }
    Screen.theme-void Footer { background: #000000; color: #ffffff; border-top: solid #555555; }
    Screen.theme-void #now_playing { background: #000000; border-bottom: solid #555555; }
    Screen.theme-void #volume_label { color: #ffffff; }
    Screen.theme-void .view_title { color: #ffffff; border-bottom: dashed #555555; }
    Screen.theme-void Input { border-bottom: solid #ffffff; background: #000000; color: #ffffff; }
    Screen.theme-void Input:focus { border-bottom: double #ffffff; background: #111111; }
    Screen.theme-void ListView { background: #000000; }
    Screen.theme-void ListItem:hover { background: #111111; }
    Screen.theme-void ListItem:focus { background: #ffffff; color: #000000; text-style: bold; }
    Screen.theme-void ProgressBar > Bar { color: #ffffff; }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("s", "show_search", "Search", show=True),
        Binding("l", "show_library", "Library", show=True),
        Binding("u", "show_queue", "Queue", show=True),
        Binding("c", "cycle_theme", "Theme", show=True),
        Binding("space", "toggle_pause", "Pause", show=True),
        Binding("right", "seek_forward", "+10s", show=True),
        Binding("left", "seek_backward", "-10s", show=True),
        Binding("+", "vol_up", "Vol+", show=True),
        Binding("=", "vol_up", "", show=False),
        Binding("-", "vol_down", "Vol-", show=True),
        Binding("n", "play_next", "Next", show=True),
        Binding("d", "delete_item", "Delete", show=True),
        Binding("e", "export_playlist", "Export", show=True),
        Binding("i", "import_playlist", "Import", show=True),
    ]
    
    def __init__(self):
        super().__init__()
        self.player = PhantomPlayer(callback=self.on_player_update)
        self.yt = YTMusic()
        
        self.library = {"Default": []}
        self.active_library_key = "Default"
        
        self.queue = []
        self.current_index = -1
        
        self.search_results = []
        self.load_library()
        
        self.themes = ["theme-hacker", "theme-cyberpunk", "theme-nord", "theme-void"]
        self.current_theme_index = 0
        self.volume = 50
        
        if not os.path.exists(EXPORTS_DIR):
            try:
                os.makedirs(EXPORTS_DIR)
            except Exception:
                pass

    def load_library(self):
        if os.path.exists(PLAYLIST_FILE):
            try:
                with open(PLAYLIST_FILE, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.library = {"Default": data}
                    else:
                        self.library = data
            except Exception:
                self.library = {"Default": []}
        else:
            self.library = {"Default": []}
            
        if not self.library:
            self.library = {"Default": []}

    def save_library(self):
        try:
            with open(PLAYLIST_FILE, 'w') as f:
                json.dump(self.library, f)
        except Exception:
            pass

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Container(id="now_playing"):
            yield SciFiAnimation(id="visualizer")
            
            with Horizontal(id="volume_container"):
                yield Label("VOL", id="volume_label")
                yield ProgressBar(total=100, id="volume_bar", show_eta=False)
                
            yield Label("No track playing...", id="title")
            yield ProgressBar(total=100, id="progress", show_eta=False)
            
        with ContentSwitcher(initial="search_view", id="switcher"):
            with Vertical(id="search_view", classes="view_container"):
                yield Label("SEARCH DATABASE", classes="view_title")
                yield Input(placeholder="Search YouTube Music...", id="search_input")
                yield SearchResultsView(id="search_results")
                
            with Vertical(id="library_view", classes="view_container"):
                yield Label("PLAYLIST ARCHIVE", classes="view_title")
                yield Input(placeholder="Create New Playlist...", id="new_playlist_input")
                yield LibraryView(id="library_list")
                
            with Vertical(id="queue_view", classes="view_container"):
                yield Label("ACTIVE AUDIO QUEUE", classes="view_title")
                yield PlaylistView(id="active_queue")
                
        yield Footer()
        
    def on_mount(self):
        self.screen.add_class(self.themes[self.current_theme_index])
        self.refresh_library_view()
        self.query_one("#volume_bar", ProgressBar).update(progress=self.volume)
        self.query_one("#search_input", Input).focus()

    def action_show_search(self):
        self.query_one("#switcher", ContentSwitcher).current = "search_view"
        self.query_one("#search_input", Input).focus()
        
    def action_show_library(self):
        self.query_one("#switcher", ContentSwitcher).current = "library_view"
        self.query_one("#library_list", LibraryView).focus()
        
    def action_show_queue(self):
        self.query_one("#switcher", ContentSwitcher).current = "queue_view"
        self.query_one("#active_queue", PlaylistView).focus()

    def refresh_library_view(self):
        lib_view = self.query_one("#library_list", LibraryView)
        lib_view.clear()
        for pl_name in self.library.keys():
            mark = "=> " if pl_name == self.active_library_key else "   "
            lib_view.append(ListItem(Label(f"{mark}{pl_name} ({len(self.library[pl_name])} tracks)")))

    def refresh_queue_view(self):
        queue_view = self.query_one("#active_queue", PlaylistView)
        queue_view.clear()
        for item in self.queue:
            queue_view.append(ListItem(Label(item['title'])))

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        if message.control.id == "search_input":
            query = message.value
            if not query:
                return
            
            search_view = self.query_one("#search_results", SearchResultsView)
            search_view.clear()
            search_view.append(ListItem(Label("Searching...")))
            
            results = await asyncio.to_thread(self.yt.search, query, filter="songs")
            
            search_view.clear()
            self.search_results = []
            for res in results[:20]:
                title = res.get("title", "Unknown")
                artists = ", ".join([a["name"] for a in res.get("artists", []) if "name" in a])
                vid = res.get("videoId")
                if vid:
                    display = f"{title} - {artists}"
                    self.search_results.append({'title': display, 'videoId': vid})
                    search_view.append(ListItem(Label(display)))
            
            search_view.focus()
                    
        elif message.control.id == "new_playlist_input":
            pl_name = message.value.strip()
            if pl_name:
                if pl_name.startswith("import:"):
                    filename = pl_name.replace("import:", "").strip()
                    self.do_import(filename)
                elif pl_name not in self.library:
                    self.library[pl_name] = []
                    self.active_library_key = pl_name
                    self.save_library()
                    self.refresh_library_view()
            message.control.value = ""

    def do_import(self, filename: str):
        filepath = os.path.join(EXPORTS_DIR, filename)
        if not filename.endswith(".json"):
            filepath += ".json"
            
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    name = filename.replace(".json", "")
                    self.library[name] = data
                    self.save_library()
                    self.refresh_library_view()
                    self.query_one("#title", Label).update(f"Imported: {name}")
            except Exception:
                self.query_one("#title", Label).update(f"Failed to import {filename}")
        else:
            self.query_one("#title", Label).update(f"File not found: {filename}")

    def action_export_playlist(self):
        if self.query_one("#switcher", ContentSwitcher).current != "library_view":
            return
            
        lib_view = self.query_one("#library_list", LibraryView)
        if lib_view.has_focus and lib_view.index is not None:
            names = list(self.library.keys())
            if 0 <= lib_view.index < len(names):
                pl_name = names[lib_view.index]
                data = self.library[pl_name]
                filepath = os.path.join(EXPORTS_DIR, f"{pl_name}.json")
                try:
                    with open(filepath, 'w') as f:
                        json.dump(data, f)
                    self.query_one("#title", Label).update(f"Exported to {filepath}")
                except Exception:
                    self.query_one("#title", Label).update("Export failed.")

    def action_import_playlist(self):
        if self.query_one("#switcher", ContentSwitcher).current != "library_view":
            self.action_show_library()
            
        self.query_one("#new_playlist_input", Input).focus()
        self.query_one("#new_playlist_input", Input).value = "import:"
        
    def action_cycle_theme(self):
        self.screen.remove_class(self.themes[self.current_theme_index])
        self.current_theme_index = (self.current_theme_index + 1) % len(self.themes)
        self.screen.add_class(self.themes[self.current_theme_index])
        
    def action_vol_up(self):
        self.volume = min(100, self.volume + 5)
        self.player.set_volume(self.volume)
        self.query_one("#volume_bar", ProgressBar).update(progress=self.volume)
        
    def action_vol_down(self):
        self.volume = max(0, self.volume - 5)
        self.player.set_volume(self.volume)
        self.query_one("#volume_bar", ProgressBar).update(progress=self.volume)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "search_results":
            index = event.list_view.index
            if index is not None and 0 <= index < len(self.search_results):
                item = self.search_results[index]
                
                self.library[self.active_library_key].append(item)
                self.save_library()
                self.refresh_library_view()
                
                self.queue.append(item)
                self.refresh_queue_view()
                
                if self.current_index == -1:
                    self.play_track(len(self.queue) - 1)
        
        elif event.list_view.id == "library_list":
            index = event.list_view.index
            if index is not None:
                names = list(self.library.keys())
                if 0 <= index < len(names):
                    self.active_library_key = names[index]
                    self.refresh_library_view()
                    
                    self.queue = list(self.library[self.active_library_key])
                    self.refresh_queue_view()
                    self.current_index = -1
                    self.player.stop()
                    self.query_one("#title", Label).update(f"Loaded {self.active_library_key} into Queue.")
                    self.query_one("#progress", ProgressBar).update(progress=0)
                    self.query_one("#visualizer", SciFiAnimation).pause()
                    
                    if self.queue:
                        self.play_track(0)
                        
        elif event.list_view.id == "active_queue":
            index = event.list_view.index
            if index is not None:
                self.play_track(index)

    def play_track(self, index: int):
        if 0 <= index < len(self.queue):
            self.current_index = index
            item = self.queue[index]
            url = f"https://www.youtube.com/watch?v={item['videoId']}"
            
            self.query_one("#title", Label).update(f"Buffering: {item['title']}...")
            self.query_one("#progress", ProgressBar).update(progress=0)
            self.query_one("#visualizer", SciFiAnimation).buffer()
            
            self.player.play(url)
            self.player.set_volume(self.volume) 

    def action_play_next(self):
        if self.current_index + 1 < len(self.queue):
            self.play_track(self.current_index + 1)
        else:
            self.current_index = -1
            self.query_one("#title", Label).update("Queue Finished.")
            self.query_one("#progress", ProgressBar).update(progress=0)
            self.query_one("#visualizer", SciFiAnimation).pause()
            
    def action_toggle_pause(self):
        is_paused = self.player.pause_toggle()
        vis = self.query_one("#visualizer", SciFiAnimation)
        if is_paused:
            vis.pause()
        else:
            if self.current_index != -1:
                vis.play()
                
    def action_seek_forward(self):
        self.player.seek(10)
        
    def action_seek_backward(self):
        self.player.seek(-10)
        
    def action_delete_item(self):
        current_view = self.query_one("#switcher", ContentSwitcher).current
        
        if current_view == "queue_view":
            queue_view = self.query_one("#active_queue", PlaylistView)
            if queue_view.has_focus and queue_view.index is not None:
                index = queue_view.index
                if 0 <= index < len(self.queue):
                    del self.queue[index]
                    self.refresh_queue_view()
                    
                    if self.current_index == index:
                        self.player.stop()
                        self.query_one("#title", Label).update("Track deleted. Stopped.")
                        self.query_one("#progress", ProgressBar).update(progress=0)
                        self.query_one("#visualizer", SciFiAnimation).pause()
                        self.current_index = -1
                    elif self.current_index > index:
                        self.current_index -= 1
                        
        elif current_view == "library_view":
            lib_view = self.query_one("#library_list", LibraryView)
            if lib_view.has_focus and lib_view.index is not None:
                index = lib_view.index
                names = list(self.library.keys())
                if 0 <= index < len(names):
                    pl_name = names[index]
                    if len(self.library) > 1:
                        del self.library[pl_name]
                        if self.active_library_key == pl_name:
                            self.active_library_key = list(self.library.keys())[0]
                        self.save_library()
                        self.refresh_library_view()
        
    def on_player_update(self, event_name, value):
        if event_name == 'percent_pos':
            def update_progress():
                try:
                    vis = self.query_one("#visualizer", SciFiAnimation)
                    if vis.state == "buffering":
                        vis.play()
                    progress = self.query_one("#progress", ProgressBar)
                    progress.update(progress=value)
                except Exception:
                    pass
            self.call_from_thread(update_progress)
            
        elif event_name == 'metadata':
            def update_meta():
                if 0 <= self.current_index < len(self.queue):
                    title = self.queue[self.current_index]['title']
                    self.query_one("#title", Label).update(f"Now Playing: {title}")
            self.call_from_thread(update_meta)
            
        elif event_name == 'eof':
            self.call_from_thread(self.action_play_next)

    def on_unmount(self):
        self.player.stop()
