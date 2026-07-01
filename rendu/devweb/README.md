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

## 🔌 Connexion au serveur INFRA (Tailscale)

Le serveur **Ollama** de l'INFRA n'est **pas exposé publiquement** : l'accès passe
par un réseau privé **Tailscale** (voir [docs/DEVWEB-CONNEXION.md](../../docs/DEVWEB-CONNEXION.md)).

| Paramètre | Valeur |
|---|---|
| URL | `http://100.103.147.99:11434` |
| Modèle | `techcorp-finance` |
| API | Ollama native (`/api/chat`, `/api/tags`) |

**Avant de lancer l'app**, rejoindre le tailnet :

1. Installer Tailscale : https://tailscale.com/download
2. `tailscale up` puis se connecter **au même tailnet que l'INFRA** (compte `mathysc73@`, demander une invitation).
3. Vérifier : `tailscale status` doit lister la machine `desktop-57p5cmk`, puis
   `curl http://100.103.147.99:11434/api/tags` doit répondre.

Le nom du modèle est sélectionnable dans la sidebar (liste récupérée via
`GET /api/tags`). Défauts déjà pré-remplis (`100.103.147.99:11434` / `techcorp-finance`).

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
