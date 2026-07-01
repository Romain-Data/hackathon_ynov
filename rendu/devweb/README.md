# 🌐 DEV WEB — Interface de chat TechCorp

Interface web de chat pour l'assistant financier **Phi-3.5-Financial**, connectée
au serveur d'inférence déployé par l'équipe INFRA (Ollama, `http://localhost:11434`).

## ✨ Fonctionnalités

- 💬 Chat en temps réel avec **streaming** des réponses du modèle
- 🧠 **Historique** de la conversation conservé pendant la session
- 🟢/🔴 **Indicateur d'état de connexion** au serveur (connecté / déconnecté)
- ⚙️ Sélection de l'**URL du serveur** et du **modèle** depuis la sidebar
- 🗑️ Bouton pour effacer l'historique

## 🚀 Lancement en une commande

Depuis `rendu/devweb/` :

```powershell
# Windows / PowerShell
./run.ps1
```

```bash
# Linux / macOS
./run.sh
```

Ces scripts installent les dépendances puis démarrent l'app. L'interface s'ouvre
sur `http://localhost:8501`.

> Lancement manuel équivalent : `pip install -r requirements.txt && streamlit run app.py`

## 🔌 Prérequis (côté INFRA)

Le serveur d'inférence doit tourner. Avec Ollama :

```bash
ollama serve                 # démarre le serveur sur :11434
ollama create phi3.5-financial -f ../../ollama_server/Modelfile
```

Le nom du modèle est sélectionnable dans la sidebar (liste récupérée via
`GET /api/tags`). Par défaut : `phi3.5`.

## 🧩 Architecture

```
Navigateur ──HTTP──> Streamlit (app.py) ──HTTP──> Ollama /api/chat ──> Phi-3.5-Financial
```

- `check_connection()` → `GET /api/tags` pour l'état de connexion + liste des modèles
- `stream_chat()` → `POST /api/chat` (stream) pour les réponses token par token

## ⚠️ Note de sécurité (contexte du challenge)

Le modèle financier hérité est **compromis** (backdoor déclenchée par une phrase
piège — voir le rapport CYBER). Cette interface est agnostique du modèle : elle se
branchera aussi bien sur le modèle **nettoyé/réentraîné** fourni par IA/DATA. Pour
une démo saine, pointer sur le modèle assaini.
