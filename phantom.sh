#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

if [ ! -d ".venv" ]; then
    echo "[*] First time setup detected! Installing dependencies automatically..."
    chmod +x install.sh
    ./install.sh
fi
source .venv/bin/activate
python main.py "$@"
