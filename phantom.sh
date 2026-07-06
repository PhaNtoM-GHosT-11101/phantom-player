#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

if [ ! -d ".venv" ]; then
    echo "[-] Virtual environment not found. Please run ./install.sh first."
    exit 1
fi
source .venv/bin/activate
python main.py "$@"
