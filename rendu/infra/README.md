# 🏗️ Rendu INFRA — Déploiement du serveur d'inférence Phi-3.5-Financial

**Challenge IA TechCorp Industries** · Filière **INFRA** · Auteur : Mathys COLOMBO

> **Mission :** choisir et déployer un serveur d'inférence exposant le modèle **Phi-3.5-Financial**, le rendre accessible à l'équipe DEV WEB, optimiser les performances, et documenter les choix techniques.

---

## 1. Résultat en une phrase

Le modèle financier est servi par **Ollama** (GPU), exposé de façon **sécurisée** à l'équipe DEV WEB via un réseau privé **Tailscale**, à l'adresse **`http://100.103.147.99:11434`** — accès validé de bout en bout par un pair distant.

---

## 2. Architecture déployée

```
   ┌─────────────────────────────────────────────┐         Réseau privé Tailscale (WireGuard)
   │  Machine INFRA (Windows 11)                  │        ┌───────────────────────────────┐
   │                                              │        │                               │
   │   ┌───────────────┐   HTTP    ┌───────────┐  │        │   DEV WEB (machine distante)  │
   │   │   Ollama       │◄─────────│  API REST │◄─┼────────┼─►  http://100.103.147.99:11434 │
   │   │  techcorp-     │  :11434  │ 0.0.0.0   │  │  100.x │   (interface de chat)         │
   │   │  finance       │          └───────────┘  │        │                               │
   │   │  (Phi-3.5)     │                         │        └───────────────────────────────┘
   │   │  100% GPU      │   RTX 4070 · 8 Go VRAM  │
   │   └───────────────┘                         │        Pas d'exposition publique :
   │        ▲  Tailscale (IP 100.103.147.99)      │        seuls les pairs invités du tailnet
   └────────┼────────────────────────────────────┘        accèdent au serveur.
            └── Pare-feu Windows : port 11434 TCP autorisé (Inbound)
```

---

## 3. Choix techniques (justifiés)

| Décision | Choix retenu | Pourquoi | Alternatives écartées |
|---|---|---|---|
| **Serveur d'inférence** | **Ollama** (natif Windows) | Solution clé en main, API REST standard, quantization GGUF automatique, GPU natif, déploiement en minutes | **Triton** (lourd : image ~10 Go, config GPU, risque sur 7h) · **Serveur maison FastAPI/vLLM** (tout à recoder) |
| **Modèle servi** | **`phi3.5`** + system prompt financier | Fiabilité de la démo ; la spécialisation « finance » est portée par le system prompt | **Fusion de l'adapter LoRA hérité → GGUF** (conversion chronophage + risque VRAM) |
| **Exécution** | Natif Windows | Détection GPU RTX 4070 automatique, zéro config WSL | Ollama en conteneur Docker (GPU passthrough WSL2 fragile) |
| **Exposition réseau** | **Bind `0.0.0.0` + Tailscale** | Dev web distants ; réseau privé maillé → **aucune exposition publique** (Ollama n'a pas d'auth), défendable côté sécurité | **ngrok** (URL publique sans auth = risque) · **Cloudflare Tunnel** (setup plus long) |
| **Paramètres d'inférence** | `temperature 0.3`, `top_p 0.9`, `num_predict 512`, `num_ctx 4096`, `repeat_penalty 1.1` | Assistant financier = réponses factuelles ; température basse limite les hallucinations | Valeurs par défaut (trop créatives) |

> Détail exhaustif des décisions, dans l'ordre chronologique : voir [`../../docs/INFRA-DECISIONS.md`](../../docs/INFRA-DECISIONS.md).

---

## 4. Déploiement — étapes reproductibles

```powershell
# 1. Installer Ollama (natif Windows, non-interactif)
winget install --id Ollama.Ollama -e --accept-source-agreements --accept-package-agreements --silent

# 2. Télécharger le modèle de base
ollama pull phi3.5

# 3. Créer le modèle personnalisé (system prompt + paramètres d'inférence)
ollama create techcorp-finance -f Modelfile

# 4. Exposer sur toutes les interfaces (défaut Ollama = 127.0.0.1 seulement)
[Environment]::SetEnvironmentVariable("OLLAMA_HOST","0.0.0.0:11434","User")
#    puis lancer le serveur (voir start-ollama.ps1 pour la version persistante)

# 5. Pare-feu Windows — autoriser le port (PowerShell ADMIN)
New-NetFirewallRule -DisplayName "Ollama 11434" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 11434 -Profile Any

# 6. Réseau privé — Tailscale
winget install --id Tailscale.Tailscale -e --silent
& "C:\Program Files\Tailscale\tailscale.exe" up          # authentification
& "C:\Program Files\Tailscale\tailscale.exe" ip -4       # → 100.103.147.99
```

Le script [`start-ollama.ps1`](start-ollama.ps1) démarre le serveur sur `0.0.0.0:11434` en une commande (utilisé aussi via un raccourci dans le dossier Démarrage pour la persistance au logon).

---

## 5. Accès pour l'équipe DEV WEB

**URL :** `http://100.103.147.99:11434` — modèle : `techcorp-finance`

Guide complet (endpoints Ollama `/api/generate`, `/api/chat`, endpoint compatible OpenAI `/v1/chat/completions`, exemples JS, indicateur connecté/déconnecté) : **[`DEVWEB-CONNEXION.md`](DEVWEB-CONNEXION.md)**.

Vérification rapide :
```bash
curl http://100.103.147.99:11434/api/tags
```

---

## 6. Performances & validation

| Métrique | Valeur |
|---|---|
| Matériel | NVIDIA RTX 4070 Laptop — 8 Go VRAM |
| Placement modèle | **100% GPU** (3.8 Go VRAM utilisés) |
| Débit de génération | **~85 tokens/s** |
| Fenêtre de contexte | 4096 tokens |
| Endpoints testés | `/api/generate`, `/api/chat`, `/v1/chat/completions` ✅ |
| **Accès distant** | ✅ validé par le pair `alenzo` — `tailscale ping` direct 32 ms, `curl` OK depuis sa machine |

**Exemple de réponse du modèle** (question : *« What is diversification in investing? »*) :
> *Diversification in investing refers to the strategy of spreading investment holdings across various financial instruments, industries, and other categories to reduce exposure to risk associated with any single asset or sector...*

---

## 7. Blocages rencontrés & résolutions

| # | Blocage | Résolution |
|---|---|---|
| B1 | ID winget Tailscale invalide (`No package found`) | Bon ID : `Tailscale.Tailscale` (majuscules) |
| B2 | `ollama create` : `invalid float value` | Ollama refuse les commentaires `#` en fin de ligne `PARAMETER` → déplacés sur des lignes dédiées |
| B3 | Serveur non persistant (le `serve` de fond meurt avec la session) | Script `start-ollama.ps1` + processus détaché + raccourci dossier Démarrage |
| B4 | Pare-feu / tâche planifiée : `Accès refusé` | Contournement sans admin (dossier Démarrage) ; règle pare-feu ajoutée ensuite en PowerShell admin |
| B5 | Pair distant vu « offline », ping timeout | Changement d'IP réseau local (reconnexion Wi-Fi) ; Tailscale a réétabli le chemin direct — validé par `pong ... in 32ms` |

---

## 8. Contenu du rendu

```
rendu/infra/
├── README.md              ← ce document
├── Modelfile              ← modèle Ollama (system prompt + paramètres d'inférence)
├── start-ollama.ps1       ← démarrage du serveur en une commande
├── DEVWEB-CONNEXION.md    ← guide de connexion pour l'équipe DEV WEB
└── captures/              ← captures d'écran (preuves visuelles)
```

---

## 9. Captures (preuves)

| # | Description | Fichier |
|---|---|---|
| 1 | Installation Ollama terminée (`winget`) | `captures/01-install-ollama.png` |
| 2 | `ollama list` + `ollama ps` (100% GPU) + réponse d'inférence | `captures/02-ollama-gpu-inference.png` |
| 3 | Dashboard Tailscale « Machines » + `tailscale status` | `captures/03-tailscale-status.png` |
| 4 | **`curl` réussi depuis la machine DEV WEB distante** | `captures/04-devweb-curl-ok.png` |

![Installation Ollama](captures/01-install-ollama.png)
![Ollama GPU + inférence](captures/02-ollama-gpu-inference.png)
![Tailscale status](captures/03-tailscale-status.png)
![Accès distant DEV WEB](captures/04-devweb-curl-ok.png)
