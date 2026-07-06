from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, DirectoryTree, Static, ProgressBar, Label, ListView, ListItem
from textual.reactive import reactive
from textual.binding import Binding
import os

from player import PhantomPlayer

class PlaylistView(ListView):
    pass

class PlayerUI(App):
    """A minimal, hacker-style TUI music player using mpv."""
    
    CSS = """
    Screen {
        background: #000000;
        color: #00ff00;
    }
    #browser {
        width: 30%;
        height: 100%;
        border-right: solid #00ff00;
        background: #001100;
    }
    #main_area {
        width: 70%;
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
        self.playlist_files = []
        self.current_index = -1

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            # Left pane: File browser (starts at home directory)
            yield DirectoryTree(os.path.expanduser("~"), id="browser")
            
            # Right pane: Now Playing + Playlist
            with Vertical(id="main_area"):
                with Container(id="now_playing"):
                    yield Label("No track playing...", id="title", classes="title")
                    yield ProgressBar(total=100, id="progress", show_eta=False)
                
                yield PlaylistView(id="playlist")
                
        yield Footer()

    def on_player_update(self, event_name, value):
        if event_name == 'percent_pos':
            def update_progress():
                progress = self.query_one("#progress", ProgressBar)
                progress.update(progress=value)
            self.call_from_thread(update_progress)
            
        elif event_name == 'metadata':
            def update_meta():
                title = value.get('title')
                if not title and self.player._current_file:
                    title = os.path.basename(self.player._current_file)
                title = title or "Unknown Track"
                self.query_one("#title", Label).update(f"Now Playing: {title}")
            self.call_from_thread(update_meta)
            
        elif event_name == 'eof':
            self.call_from_thread(self.action_play_next)

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        path = str(event.path)
        # Supported audio formats
        if path.lower().endswith(('.mp3', '.flac', '.wav', '.m4a', '.ogg', '.aac')):
            self.add_to_playlist(path)
            # If nothing is playing, start playing it
            if self.current_index == -1:
                self.play_track(len(self.playlist_files) - 1)

    def add_to_playlist(self, path: str):
        self.playlist_files.append(path)
        filename = os.path.basename(path)
        playlist = self.query_one("#playlist", PlaylistView)
        playlist.append(ListItem(Label(filename)))

    def play_track(self, index: int):
        if 0 <= index < len(self.playlist_files):
            self.current_index = index
            path = self.playlist_files[index]
            self.player.play(path)
            self.query_one("#title", Label).update(f"Loading: {os.path.basename(path)}...")

    def action_play_next(self):
        if self.current_index + 1 < len(self.playlist_files):
            self.play_track(self.current_index + 1)
        else:
            # End of playlist
            self.current_index = -1
            self.query_one("#title", Label).update("Finished Playlist.")
            self.query_one("#progress", ProgressBar).update(progress=0)
            
    def action_toggle_pause(self):
        self.player.pause_toggle()
        
    def action_seek_forward(self):
        self.player.seek(10)
        
    def action_seek_backward(self):
        self.player.seek(-10)
        
    def on_unmount(self):
        self.player.stop()
