#!/bin/bash
set -e

echo "[*] Phantom Player Installer"

# Detect OS
if [ "$(uname)" == "Darwin" ]; then
    echo "[*] macOS detected. Checking for Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "[-] Homebrew is not installed. Please install it first: https://brew.sh/"
        exit 1
    fi
    echo "[*] Installing mpv and python3 if missing..."
    brew list mpv &>/dev/null || brew install mpv
    brew list python &>/dev/null || brew install python
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    echo "[*] Linux detected."
    if command -v apt &> /dev/null; then
        echo "[*] Debian/Ubuntu based system detected."
        sudo apt update
        sudo apt install -y mpv python3 python3-venv python3-pip libmpv-dev
    elif command -v pacman &> /dev/null; then
        echo "[*] Arch based system detected."
        sudo pacman -Sy --noconfirm mpv python mpv-libs
    elif command -v dnf &> /dev/null; then
        echo "[*] Fedora based system detected."
        sudo dnf install -y mpv python3 mpv-libs
    else
        echo "[-] Unsupported package manager. Please install mpv and python3 manually."
    fi
else
    echo "[-] Unsupported OS."
    exit 1
fi

echo "[*] Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "[*] Installing Python dependencies..."
pip install -r requirements.txt

echo "[+] Installation complete! You can now run the player using ./phantom.sh"
