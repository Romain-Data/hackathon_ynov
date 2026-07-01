# start-ollama.ps1
# Démarre le serveur Ollama exposé sur toutes les interfaces (0.0.0.0:11434)
# pour être accessible à l'équipe DEV WEB via Tailscale.
#
# Usage manuel :   powershell -ExecutionPolicy Bypass -File .\ollama_server\start-ollama.ps1
# (Utilisé aussi par la tâche planifiée "OllamaServe" au démarrage de session.)

$ErrorActionPreference = "SilentlyContinue"

# 1. Bind sur toutes les interfaces (défaut Ollama = 127.0.0.1 seulement)
$env:OLLAMA_HOST = "0.0.0.0:11434"

# 2. Localiser l'exécutable Ollama
$ollama = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
if (-not (Test-Path $ollama)) { $ollama = "ollama" }  # fallback PATH

# 3. Ne rien faire si le serveur répond déjà
try {
    Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 2 | Out-Null
    Write-Host "Ollama tourne deja sur :11434"
    exit 0
} catch { }

# 4. Démarrer le serveur
Write-Host "Demarrage d'Ollama sur 0.0.0.0:11434 ..."
& $ollama serve
