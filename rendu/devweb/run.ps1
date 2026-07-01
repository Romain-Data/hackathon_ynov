# Lancement en une commande (Windows / PowerShell) :  ./run.ps1
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
python -m pip install -q -r requirements.txt
python -m streamlit run app.py
