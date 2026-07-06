from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Static, ProgressBar, Label, ListView, ListItem, TabbedContent, TabPane
from textual.reactive import reactive
from textual.binding import Binding
from ytmusicapi import YTMusic
import asyncio
import json
import os
import random

from player import PhantomPlayer

PLAYLIST_FILE = "playlist.json"

class PlaylistView(ListView):
    pass
    
class SearchResultsView(ListView):
    pass

class ASCIIVisualizer(Static):
    """An animated ASCII equalizer."""
    
    def on_mount(self) -> None:
        self.bars = [' ', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        self.num_bars = 40
        self.animating = False
        self.update_bars()
        self.animation_timer = self.set_interval(0.1, self.tick, pause=True)

    def tick(self) -> None:
        self.update_bars()

    def update_bars(self):
        if not self.animating:
            content = " ".join([' ' for _ in range(self.num_bars)])
        else:
            content = " ".join([random.choice(self.bars) for _ in range(self.num_bars)])
        self.update(f"[bold #ff00ff]{content}[/]")

    def play(self):
        self.animating = True
        self.animation_timer.resume()

    def pause(self):
        self.animating = False
        self.animation_timer.pause()
        self.update_bars()

class PlayerUI(App):
    """A premium Cyberpunk TUI online music player using mpv."""
    
    CSS = """
    Screen {
        background: #0d0d14;
        color: #00ffff;
    }
    
    Header {
        background: #ff00ff;
        color: #0d0d14;
        text-style: bold;
    }
    
    Footer {
        background: #00ffff;
        color: #0d0d14;
        text-style: bold;
    }
    
    #now_playing {
        height: 8;
        border: round #ff00ff;
        background: #11001a;
        padding: 1;
        content-align: center middle;
        margin: 1;
    }
    
    #visualizer {
        height: 1;
        content-align: center middle;
        margin-bottom: 1;
    }
    
    TabbedContent {
        margin: 0 1;
    }
    
    TabPane {
        border: solid #00ffff;
        background: #0a111a;
        padding: 1;
    }
    
    Input {
        border: round #ff00ff;
        background: #0d0d14;
        color: #00ffff;
        margin-bottom: 1;
    }
    
    Input:focus {
        border: double #00ffff;
    }
    
    ListView {
        background: #0a111a;
    }
    
    ListItem {
        padding: 0 1;
    }
    
    ListItem:hover {
        background: #1a2b40;
    }
    
    ListItem:focus {
        background: #ff00ff;
        color: #0d0d14;
        text-style: bold;
    }
    
    .title {
        text-style: bold;
        color: #00ffff;
        margin-bottom: 1;
    }
    
    ProgressBar > Bar {
        color: #ff00ff;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("space", "toggle_pause", "Pause/Play", show=True),
        Binding("right", "seek_forward", "Seek +10s", show=True),
        Binding("left", "seek_backward", "Seek -10s", show=True),
        Binding("n", "play_next", "Next Track", show=True),
        Binding("d", "delete_item", "Delete Selected", show=True),
    ]
    
    def __init__(self):
        super().__init__()
        self.player = PhantomPlayer(callback=self.on_player_update)
        self.yt = YTMusic()
        
        self.playlists = {"Default": []}
        self.active_playlist_name = "Default"
        
        self.search_results = []
        self.current_index = -1
        self.load_playlists()

    def load_playlists(self):
        if os.path.exists(PLAYLIST_FILE):
            try:
                with open(PLAYLIST_FILE, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.playlists = {"Default": data}
                    else:
                        self.playlists = data
            except Exception:
                self.playlists = {"Default": []}
        else:
            self.playlists = {"Default": []}
            
        if not self.playlists:
            self.playlists = {"Default": []}
        if self.active_playlist_name not in self.playlists:
            self.active_playlist_name = list(self.playlists.keys())[0]

    def save_playlists(self):
        try:
            with open(PLAYLIST_FILE, 'w') as f:
                json.dump(self.playlists, f)
        except Exception:
            pass

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Container(id="now_playing"):
            yield ASCIIVisualizer(id="visualizer")
            yield Label("No track playing...", id="title", classes="title")
            yield ProgressBar(total=100, id="progress", show_eta=False)
            
        with TabbedContent():
            with TabPane("Queue", id="tab_queue"):
                yield PlaylistView(id="playlist")
                
            with TabPane("Search", id="tab_search"):
                yield Input(placeholder="Search YouTube Music...", id="search_input")
                yield SearchResultsView(id="search_results")
                
            with TabPane("Playlists", id="tab_playlists"):
                yield ListView(id="all_playlists_list")
                yield Input(placeholder="Type new playlist name & hit Enter...", id="new_playlist_input")
                
        yield Footer()
        
    def on_mount(self):
        self.refresh_queue_view()
        self.refresh_playlists_view()

    def refresh_queue_view(self):
        playlist_view = self.query_one("#playlist", PlaylistView)
        playlist_view.clear()
        queue = self.playlists.get(self.active_playlist_name, [])
        for item in queue:
            playlist_view.append(ListItem(Label(item['title'])))
            
    def refresh_playlists_view(self):
        pl_view = self.query_one("#all_playlists_list", ListView)
        pl_view.clear()
        for pl_name in self.playlists.keys():
            mark = "=> " if pl_name == self.active_playlist_name else "   "
            pl_view.append(ListItem(Label(f"{mark}{pl_name} ({len(self.playlists[pl_name])} songs)")))

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
                    
        elif message.control.id == "new_playlist_input":
            pl_name = message.value.strip()
            if pl_name and pl_name not in self.playlists:
                self.playlists[pl_name] = []
                self.save_playlists()
                self.refresh_playlists_view()
                message.control.value = ""

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "search_results":
            index = event.list_view.index
            if index is not None and 0 <= index < len(self.search_results):
                item = self.search_results[index]
                self.add_to_queue(item)
                
                queue = self.playlists.get(self.active_playlist_name, [])
                if self.current_index == -1:
                    self.play_track(len(queue) - 1)
        
        elif event.list_view.id == "playlist":
            index = event.list_view.index
            if index is not None:
                self.play_track(index)
                
        elif event.list_view.id == "all_playlists_list":
            index = event.list_view.index
            if index is not None:
                names = list(self.playlists.keys())
                if 0 <= index < len(names):
                    self.active_playlist_name = names[index]
                    self.current_index = -1
                    self.player.stop()
                    self.query_one("#title", Label).update(f"Loaded Playlist: {self.active_playlist_name}")
                    self.query_one("#progress", ProgressBar).update(progress=0)
                    self.query_one("#visualizer", ASCIIVisualizer).pause()
                    self.refresh_queue_view()
                    self.refresh_playlists_view()

    def add_to_queue(self, item: dict):
        self.playlists[self.active_playlist_name].append(item)
        self.save_playlists()
        self.refresh_queue_view()
        self.refresh_playlists_view()

    def play_track(self, index: int):
        queue = self.playlists.get(self.active_playlist_name, [])
        if 0 <= index < len(queue):
            self.current_index = index
            item = queue[index]
            url = f"https://www.youtube.com/watch?v={item['videoId']}"
            
            self.query_one("#title", Label).update(f"Buffering: {item['title']}...")
            self.query_one("#progress", ProgressBar).update(progress=0)
            self.query_one("#visualizer", ASCIIVisualizer).play()
            
            self.player.play(url)

    def action_play_next(self):
        queue = self.playlists.get(self.active_playlist_name, [])
        if self.current_index + 1 < len(queue):
            self.play_track(self.current_index + 1)
        else:
            self.current_index = -1
            self.query_one("#title", Label).update("Finished Playlist.")
            self.query_one("#progress", ProgressBar).update(progress=0)
            self.query_one("#visualizer", ASCIIVisualizer).pause()
            
    def action_toggle_pause(self):
        is_paused = self.player.pause_toggle()
        vis = self.query_one("#visualizer", ASCIIVisualizer)
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
        queue_view = self.query_one("#playlist", PlaylistView)
        playlists_view = self.query_one("#all_playlists_list", ListView)
        
        if queue_view.has_focus and queue_view.index is not None:
            index = queue_view.index
            queue = self.playlists.get(self.active_playlist_name, [])
            if 0 <= index < len(queue):
                # Remove from data
                del queue[index]
                self.save_playlists()
                
                # Update UI
                self.refresh_queue_view()
                self.refresh_playlists_view()
                
                # Handle playing track getting deleted
                if self.current_index == index:
                    self.player.stop()
                    self.query_one("#title", Label).update("Track deleted. Stopped.")
                    self.query_one("#progress", ProgressBar).update(progress=0)
                    self.query_one("#visualizer", ASCIIVisualizer).pause()
                    self.current_index = -1
                elif self.current_index > index:
                    self.current_index -= 1
                    
        elif playlists_view.has_focus and playlists_view.index is not None:
            index = playlists_view.index
            names = list(self.playlists.keys())
            if 0 <= index < len(names):
                pl_name = names[index]
                if len(self.playlists) > 1:
                    del self.playlists[pl_name]
                    if self.active_playlist_name == pl_name:
                        self.active_playlist_name = list(self.playlists.keys())[0]
                        self.current_index = -1
                        self.player.stop()
                        self.query_one("#title", Label).update(f"Loaded Playlist: {self.active_playlist_name}")
                        self.query_one("#progress", ProgressBar).update(progress=0)
                        self.query_one("#visualizer", ASCIIVisualizer).pause()
                        self.refresh_queue_view()
                    self.save_playlists()
                    self.refresh_playlists_view()
        
    def on_player_update(self, event_name, value):
        if event_name == 'percent_pos':
            def update_progress():
                try:
                    progress = self.query_one("#progress", ProgressBar)
                    progress.update(progress=value)
                except Exception:
                    pass
            self.call_from_thread(update_progress)
            
        elif event_name == 'metadata':
            def update_meta():
                queue = self.playlists.get(self.active_playlist_name, [])
                if 0 <= self.current_index < len(queue):
                    title = queue[self.current_index]['title']
                    self.query_one("#title", Label).update(f"Now Playing: {title}")
            self.call_from_thread(update_meta)
            
        elif event_name == 'eof':
            self.call_from_thread(self.action_play_next)

    def on_unmount(self):
        self.player.stop()
