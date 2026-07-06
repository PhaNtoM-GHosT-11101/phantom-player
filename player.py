import mpv
from typing import Callable, Optional

class PhantomPlayer:
    def __init__(self, callback: Optional[Callable] = None):
        # Initialize mpv with basic configuration
        self.player = mpv.MPV(ytdl=True, video=False, term_osd=False)
        self.callback = callback
        self._current_file = None

        # Observers to send data back to the UI
        @self.player.property_observer('time-pos')
        def time_observer(_name, value):
            if self.callback and value is not None:
                self.callback('time_pos', value)
                
        @self.player.property_observer('percent-pos')
        def percent_observer(_name, value):
            if self.callback and value is not None:
                self.callback('percent_pos', value)
                
        @self.player.property_observer('metadata')
        def metadata_observer(_name, value):
            if self.callback and value is not None:
                self.callback('metadata', value)
                
        @self.player.property_observer('eof-reached')
        def eof_observer(_name, value):
            if self.callback and value:
                self.callback('eof', True)

    def play(self, filepath: str):
        self._current_file = filepath
        self.player.play(filepath)
        
    def pause_toggle(self):
        self.player.pause = not self.player.pause
        return self.player.pause
        
    def stop(self):
        self.player.stop()
        
    def seek(self, seconds: float):
        # Seek relative to current position
        self.player.command('seek', seconds, 'relative')
        
    @property
    def duration(self):
        return self.player.duration
