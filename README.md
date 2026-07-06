# Phantom Player

A highly optimized, minimalist "hacker terminal" music player powered by `mpv` and Python's `Textual` framework.

## Features
- **Cross-platform**: Runs on Linux and macOS.
- **Ultra-minimalist Hacker UI**: Beautiful, resource-light terminal UI built with Textual.
- **Plays Everything**: Powered by the `mpv` engine, it handles mp3, flac, wav, m4a, ogg, and essentially any other format flawlessly.
- **Vim-inspired / Standard Keybindings**: Fast, keyboard-first navigation.
- **Local Playlists**: Browse your filesystem and queue up songs dynamically.

## Installation

We've made it incredibly easy to install and run. Just clone this repo and run the `install.sh` script. It will automatically detect your OS, install `mpv` if missing, set up a virtual environment, and install the required UI libraries safely without messing up your system Python.

```bash
git clone https://github.com/PhaNtoM-GHosT-11101/phantom-player.git
cd phantom-player
chmod +x install.sh phantom.sh
./install.sh
```

## Usage

After installation, simply run the launcher script:
```bash
./phantom.sh
```

### Controls
- **Arrow Keys / Enter**: Browse and select files on the left pane.
- **Space**: Pause/Play
- **Right Arrow**: Seek forward 10 seconds
- **Left Arrow**: Seek backward 10 seconds
- **n**: Next Track
- **q**: Quit

Enjoy your minimalist music experience!
