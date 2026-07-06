<div align="center">

# 🎛️ PHANTOM PLAYER

**A cyberpunk-inspired, terminal-based YouTube Music engine.**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](#)
[![Textual](https://img.shields.io/badge/Textual-TUI-purple.svg?style=for-the-badge)](#)
[![MPV](https://img.shields.io/badge/Powered_by-MPV-red.svg?style=for-the-badge)](#)

*Stream YouTube Music directly from your terminal with 60FPS procedural ASCII visualizers, infinite algorithm-based radio, and a glassmorphism overlay UI.*

</div>

---

## ⚡ Features

* **Procedural Visualizers:** 4 highly optimized, pre-computed ASCII animations running at zero CPU cost.
  * `BARS` - Dual-frequency audio equalizer simulation.
  * `WAVE` - Multi-layered scrolling sinusoidal wave.
  * `RADAR` - Sweeping sonar with trailing glow effects.
  * `PULSE` - Breathing, concentric neon rings.
* **Instant Search Overlay:** Press `s` to slide open a frosted-glass search UI without stopping your visualizers.
* **Infinite Radio:** Plays an intelligent, continuous stream of music based on your last track using YouTube Music's autoplay algorithm.
* **Theming Engine:** Switch between 4 curated dual-color palettes on the fly (`Hacker`, `Cyberpunk`, `Synthwave`, `Void`).
* **Hardware Stats:** Real-time monitoring of the application's CPU and RAM footprint built right into the status bar.
* **Headless Audio Backend:** Utilizes `mpv` via IPC sockets for completely detached, high-fidelity audio playback.

## 🛠️ Installation

**Prerequisites:** 
- Linux/macOS
- Python 3.12+
- `mpv` installed on your system (e.g., `sudo apt install mpv` or `brew install mpv`)

```bash
# 1. Clone the repository
git clone https://github.com/PhaNtoM-GHosT-11101/phantom-player.git
cd phantom-player

# 2. Make the script executable
chmod +x phantom.sh

# 3. Launch! (The script will automatically handle the virtual environment and dependencies)
./phantom.sh
```

## ⌨️ Keybindings

| Key | Action | Description |
| :---: | :--- | :--- |
| `s` | **Search** | Opens the track search overlay. |
| `Space` | **Play/Pause** | Toggles audio playback. |
| `n` | **Next** | Skips to the next track. |
| `+` / `-` | **Volume** | Adjusts playback volume by 5%. |
| `v` | **Cycle Visualizer** | Switches between BARS, WAVE, RADAR, and PULSE. |
| `t` | **Cycle Theme** | Switches between the 4 neon color palettes. |
| `r` | **Toggle Radio** | Turns infinite autoplay on/off. |
| `←` / `→` | **Seek** | Skips backward or forward by 10 seconds. |
| `Esc` | **Close** | Closes the search modal. |
| `Ctrl+Q` | **Quit** | Exits the player. |

## 🧠 Architecture

Phantom Player is built on a split architecture to ensure the UI never drops a frame:
1. **Frontend (`tui.py`):** Built with [Textual](https://textual.textualize.io/). Handles all layout, rendering, theming, and background math calculations using asynchronous workers and thread delegation.
2. **Backend (`player.py`):** Spawns a headless `mpv` subprocess. It communicates with the frontend over an IPC Unix socket, sending real-time EOF flags and position updates back to the UI thread.
3. **Network (`ytmusicapi`):** Handles all catalog searching and radio generation entirely in the background.

---

<div align="center">
  <i>"Music in the terminal, perfected."</i>
</div>
