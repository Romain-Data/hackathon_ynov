#!/usr/bin/env bash
# Lancement en une commande (Linux / macOS) :  ./run.sh
set -e
cd "$(dirname "$0")"
python3 -m pip install -q -r requirements.txt
python3 -m streamlit run app.py
