import subprocess
import socket
import json
import threading
import time
import os
from typing import Callable, Optional

class PhantomPlayer:
    def __init__(self, callback: Optional[Callable] = None):
        self.callback = callback
        self._current_file = None
        self.process = None
        self.socket_path = "/tmp/phantom_mpv.sock"
        self.sock = None
        self._listener_thread = None
        self._running = True
        self._paused = False

    def play(self, filepath: str):
        self.stop()
        self._current_file = filepath
        self._paused = False
        
        if os.path.exists(self.socket_path):
            try:
                os.remove(self.socket_path)
            except Exception:
                pass
        
        # Start mpv as an isolated subprocess
        cmd = [
            "mpv",
            "--no-video",
            "--term-osd=no",
            "--msg-level=all=no",
            f"--input-ipc-server={self.socket_path}",
            filepath
        ]
        
        self.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for the IPC socket to be ready
        for _ in range(20):
            if os.path.exists(self.socket_path):
                break
            time.sleep(0.1)
            
        self._connect_ipc()
        
    def _connect_ipc(self):
        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.connect(self.socket_path)
            
            # Observe playback percentage
            self._send_command({"command": ["observe_property", 1, "percent-pos"]})
            
            self._listener_thread = threading.Thread(target=self._listen, daemon=True)
            self._listener_thread.start()
        except Exception:
            pass
            
    def _send_command(self, cmd_dict):
        if self.sock:
            try:
                msg = json.dumps(cmd_dict) + "\n"
                self.sock.sendall(msg.encode('utf-8'))
            except Exception:
                pass
                
    def _listen(self):
        try:
            f = self.sock.makefile('r')
            while self._running and self.process and self.process.poll() is None:
                line = f.readline()
                if not line:
                    break
                data = json.loads(line)
                if data.get('event') == 'property-change':
                    prop = data.get('name')
                    val = data.get('data')
                    if prop == 'percent-pos' and self.callback and val is not None:
                        self.callback('percent_pos', val)
                elif data.get('event') == 'end-file':
                    if self.callback:
                        self.callback('eof', True)
        except Exception:
            pass

    def pause_toggle(self):
        self._paused = not self._paused
        self._send_command({"command": ["set_property", "pause", self._paused]})
        return self._paused
        
    def stop(self):
        if self.process:
            self._send_command({"command": ["quit"]})
            try:
                self.process.terminate()
                self.process.wait(timeout=1)
            except Exception:
                pass
            self.process = None
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None
            
    def seek(self, seconds: float):
        self._send_command({"command": ["seek", seconds, "relative"]})
