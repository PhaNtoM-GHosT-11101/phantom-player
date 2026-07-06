from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Static, ProgressBar, Label, ListView, ListItem
from textual.reactive import reactive
from textual.binding import Binding
from ytmusicapi import YTMusic
import asyncio

from player import PhantomPlayer

class PlaylistView(ListView):
    pass
    
class SearchResultsView(ListView):
    pass

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
    ]
    
    def __init__(self):
        super().__init__()
        self.player = PhantomPlayer(callback=self.on_player_update)
        self.yt = YTMusic()
        self.playlist_items = [] # list of dicts: {'title': str, 'videoId': str}
        self.search_results = []
        self.current_index = -1

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(id="left_pane"):
                yield Input(placeholder="Search YouTube Music...", id="search_input")
                yield SearchResultsView(id="search_results")
            
            with Vertical(id="main_area"):
                with Container(id="now_playing"):
                    yield Label("No track playing...", id="title", classes="title")
                    yield ProgressBar(total=100, id="progress", show_eta=False)
                
                yield PlaylistView(id="playlist")
                
        yield Footer()

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        query = message.value
        if not query:
            return
        
        search_view = self.query_one("#search_results", SearchResultsView)
        search_view.clear()
        search_view.append(ListItem(Label("Searching...")))
        
        # Run search asynchronously
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
        playlist = self.query_one("#playlist", PlaylistView)
        playlist.append(ListItem(Label(item['title'])))

    def play_track(self, index: int):
        if 0 <= index < len(self.playlist_items):
            self.current_index = index
            item = self.playlist_items[index]
            url = f"https://www.youtube.com/watch?v={item['videoId']}"
            
            self.query_one("#title", Label).update(f"Buffering: {item['title']}...")
            self.query_one("#progress", ProgressBar).update(progress=0)
            
            self.player.play(url)

    def action_play_next(self):
        if self.current_index + 1 < len(self.playlist_items):
            self.play_track(self.current_index + 1)
        else:
            self.current_index = -1
            self.query_one("#title", Label).update("Finished Playlist.")
            self.query_one("#progress", ProgressBar).update(progress=0)
            
    def action_toggle_pause(self):
        self.player.pause_toggle()
        
    def action_seek_forward(self):
        self.player.seek(10)
        
    def action_seek_backward(self):
        self.player.seek(-10)
        
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
