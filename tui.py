from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Static, ProgressBar, Label, ListView, ListItem
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
        self.num_bars = 20
        self.animating = False
        self.update_bars()
        self.animation_timer = self.set_interval(0.1, self.tick, pause=True)

    def tick(self) -> None:
        self.update_bars()

    def update_bars(self):
        if not self.animating:
            # Flat line when paused/stopped
            content = " ".join([' ' for _ in range(self.num_bars)])
        else:
            content = " ".join([random.choice(self.bars) for _ in range(self.num_bars)])
        self.update(f"[bold #00ff00]{content}[/]")

    def play(self):
        self.animating = True
        self.animation_timer.resume()

    def pause(self):
        self.animating = False
        self.animation_timer.pause()
        self.update_bars()

class PlayerUI(App):
    """A minimal, hacker-style TUI online music player using mpv."""
    
    CSS = """
    Screen {
        background: #000000;
        color: #00ff00;
    }
    #left_pane {
        width: 40%;
        height: 100%;
        border-right: solid #00ff00;
        background: #001100;
    }
    #search_input {
        border: solid #00ff00;
        background: #000000;
        color: #00ff00;
        height: 3;
    }
    #main_area {
        width: 60%;
        height: 100%;
        background: #000000;
    }
    #now_playing {
        height: 30%;
        border-bottom: solid #00ff00;
        padding: 1;
        content-align: center middle;
    }
    #visualizer {
        height: 3;
        content-align: center middle;
        margin-bottom: 1;
    }
    #playlist {
        height: 70%;
        background: #000000;
    }
    .title {
        text-style: bold;
        color: #00ff00;
        margin-bottom: 1;
    }
    ProgressBar > Bar {
        color: #00aa00;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("space", "toggle_pause", "Pause/Play", show=True),
        Binding("right", "seek_forward", "Seek +10s", show=True),
        Binding("left", "seek_backward", "Seek -10s", show=True),
        Binding("n", "play_next", "Next Track", show=True),
        Binding("d", "delete_item", "Delete Song", show=True),
    ]
    
    def __init__(self):
        super().__init__()
        self.player = PhantomPlayer(callback=self.on_player_update)
        self.yt = YTMusic()
        self.playlist_items = []
        self.search_results = []
        self.current_index = -1
        self.load_playlist()

    def load_playlist(self):
        if os.path.exists(PLAYLIST_FILE):
            try:
                with open(PLAYLIST_FILE, 'r') as f:
                    self.playlist_items = json.load(f)
            except Exception:
                self.playlist_items = []

    def save_playlist(self):
        try:
            with open(PLAYLIST_FILE, 'w') as f:
                json.dump(self.playlist_items, f)
        except Exception:
            pass

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(id="left_pane"):
                yield Input(placeholder="Search YouTube Music...", id="search_input")
                yield SearchResultsView(id="search_results")
            
            with Vertical(id="main_area"):
                with Container(id="now_playing"):
                    yield ASCIIVisualizer(id="visualizer")
                    yield Label("No track playing...", id="title", classes="title")
                    yield ProgressBar(total=100, id="progress", show_eta=False)
                
                # Pre-populate playlist view
                playlist_view = PlaylistView(id="playlist")
                for item in self.playlist_items:
                    playlist_view.append(ListItem(Label(item['title'])))
                yield playlist_view
                
        yield Footer()

    async def on_input_submitted(self, message: Input.Submitted) -> None:
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

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "search_results":
            index = event.list_view.index
            if index is not None and 0 <= index < len(self.search_results):
                item = self.search_results[index]
                self.add_to_playlist(item)
                
                if self.current_index == -1:
                    self.play_track(len(self.playlist_items) - 1)
        
        elif event.list_view.id == "playlist":
            index = event.list_view.index
            if index is not None:
                self.play_track(index)

    def add_to_playlist(self, item: dict):
        self.playlist_items.append(item)
        self.save_playlist()
        playlist = self.query_one("#playlist", PlaylistView)
        playlist.append(ListItem(Label(item['title'])))

    def play_track(self, index: int):
        if 0 <= index < len(self.playlist_items):
            self.current_index = index
            item = self.playlist_items[index]
            url = f"https://www.youtube.com/watch?v={item['videoId']}"
            
            self.query_one("#title", Label).update(f"Buffering: {item['title']}...")
            self.query_one("#progress", ProgressBar).update(progress=0)
            self.query_one("#visualizer", ASCIIVisualizer).play()
            
            self.player.play(url)

    def action_play_next(self):
        if self.current_index + 1 < len(self.playlist_items):
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
        playlist = self.query_one("#playlist", PlaylistView)
        if playlist.has_focus and playlist.index is not None:
            index = playlist.index
            if 0 <= index < len(self.playlist_items):
                # Remove from data
                del self.playlist_items[index]
                self.save_playlist()
                
                # Remove from UI
                if index < len(playlist.children):
                    playlist.children[index].remove()
                
                # Adjust current playing index if needed
                if self.current_index == index:
                    self.player.stop()
                    self.query_one("#title", Label).update("Track deleted. Stopped.")
                    self.query_one("#progress", ProgressBar).update(progress=0)
                    self.query_one("#visualizer", ASCIIVisualizer).pause()
                    self.current_index = -1
                elif self.current_index > index:
                    self.current_index -= 1
        
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
                if 0 <= self.current_index < len(self.playlist_items):
                    title = self.playlist_items[self.current_index]['title']
                    self.query_one("#title", Label).update(f"Now Playing: {title}")
            self.call_from_thread(update_meta)
            
        elif event_name == 'eof':
            self.call_from_thread(self.action_play_next)

    def on_unmount(self):
        self.player.stop()
