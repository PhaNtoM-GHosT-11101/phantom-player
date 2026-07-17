<div align="center">

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&height=200&color=gradient&customColorList=12,20,14&text=Phantom%20Player&fontColor=9ece6a&fontSize=65&fontAlignY=38&desc=%F0%9F%8E%B5%20A%20hacker-style%20terminal%20music%20player.%20Zero%20Electron.%20100%25%20Terminal.&descColor=b9f27c&descSize=16&descAlignY=58&animation=fadeIn" />

<br/>

[![Python](https://img.shields.io/badge/Python-3.8+-9ece6a?style=for-the-badge&logo=python&logoColor=black)](https://python.org)
[![Textual](https://img.shields.io/badge/Textual-TUI%20Framework-b9f27c?style=for-the-badge)](#)
[![mpv](https://img.shields.io/badge/mpv-Audio%20Engine-9ece6a?style=for-the-badge)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-b9f27c?style=for-the-badge)](#)

</div>

---

## Why I Built This

Spotify has too many features. VLC has too many windows. Winamp is dead. I wanted a music player that lived entirely in a terminal, looked incredible, and got out of my way.

So I built **Phantom Player** — a highly optimized, minimalist terminal music player powered by `mpv` and `Python Textual`.

---

## ✨ Features

```
┌─────────────────────────────────────────────────────┐
│  ♪  Phantom Player v1.0                             │
│  ─────────────────────────────────────────────────  │
│  ▶  Now Playing: Interstellar OST - Hans Zimmer     │
│  ████████████████░░░░░░░░  02:34 / 05:48            │
│                                                     │
│  [Q] Quit  [Space] Pause  [N] Next  [P] Prev        │
│  [+/-] Volume  [S] Shuffle  [L] Loop                │
└─────────────────────────────────────────────────────┘
```

- **Hacker TUI** — Built with Python Textual for a rich, interactive terminal interface
- **mpv Backend** — Rock-solid audio engine. Plays MP3, FLAC, OGG, WAV, and more
- **Keyboard First** — Every action has a keybind. Mouse not required
- **Shuffle & Loop** — Full playback control without leaving the terminal
- **Lightweight** — No Electron. No 300MB node_modules. Just Python
- **Zero Dependencies on the UI** — No browser, no X server required on headless machines

---

## 🚀 Quick Start

### Prerequisites
```bash
# Install mpv
# Ubuntu/Debian
sudo apt install mpv

# macOS
brew install mpv

# Windows
# Download from https://mpv.io
```

### Install & Run
```bash
git clone https://github.com/PhaNtoM-GHosT-11101/phantom-player
cd phantom-player
pip install -r requirements.txt
python main.py
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|:---|:---|
| UI Framework | Python Textual |
| Audio Engine | mpv (via subprocess) |
| Language | Python 3.8+ |
| Interface | Terminal / CLI |

---

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,20,14&height=100&section=footer" />
<sub>Built in a terminal, for the terminal — by <b>Aditya Priyadarshi</b></sub>
</div>