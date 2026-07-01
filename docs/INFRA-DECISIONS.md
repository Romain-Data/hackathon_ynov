# 🏗️ INFRA — Journal de décisions & déploiement

> Projet : **Challenge IA TechCorp Industries** (hackathon 7h)
> Rôle : **INFRA — L'Architecte du Système**
> Objectif : déployer le modèle **Phi-3.5-Financial** derrière un serveur d'inférence accessible à l'équipe DEV WEB, documenter et justifier chaque choix.

---

## 0. Résumé exécutif

| Sujet | Choix retenu |
|---|---|
| Serveur d'inférence | **Ollama** (natif Windows, GPU) |
| Modèle servi | **`phi3.5`** générique + system prompt financier (pas de fusion LoRA) |
| Exposition réseau | **bind `0.0.0.0:11434` + Tailscale** (réseau privé, dev web distants) |
| Bonus Triton | Non prioritaire (documenté comme piste) |

---

## 1. État des lieux initial (Étape 1)

### Contexte hackathon
- Reprise d'un projet « hérité » d'une équipe licenciée pour soupçon de compromission.
- Mission critique INFRA : serveur d'inférence opérationnel avec Phi-3.5-Financial + accès DEV WEB.
- Livrables : serveur qui répond + doc de déploiement (choix technique justifié).

### Environnement machine constaté
| Élément | Valeur |
|---|---|
| OS | Windows 11 Home |
| Docker | 29.5.3 (+ Compose v5.1.4) |
| GPU | NVIDIA RTX 4070 Laptop — **8 Go VRAM** |
| Ollama | ❌ non installé au départ |
| Serveur `:11434` | ❌ inactif au départ |

### Fichiers hérités pertinents pour l'infra
- `ollama_server/Modelfile` : `FROM phi3.5` + system prompt financier — **paramètres d'inférence à compléter** (TODO laissé par l'équipe précédente).
- `tritton_server/Dockerfile` + `model_repository/phi35_financial/` (`config.pbtxt`, `model.py`) : config Triton (backend Python, modèle `microsoft/Phi-3.5-mini-instruct`).
- `models/phi3_financial/` : adapter **LoRA** (r=8, base `microsoft/Phi-3-mini-4k-instruct`).
- `scripts/simple_chat.py` : chat CLI chargeant base + adapter LoRA (quantization 4-bit si GPU).

### Points d'attention identifiés
1. **Incohérence modèle** : le `Modelfile` sert `phi3.5` **générique** (registre Ollama), alors que le vrai modèle « fine-tuné » est l'adapter LoRA (`models/phi3_financial/`). Ollama ne charge pas un adapter PEFT directement.
2. **VRAM 8 Go** : Phi-3.5-mini (3.8B) passe en 4-bit (~3 Go) mais est serré en fp16 (~7,6 Go). La quantization est nécessaire.

---

## 2. Décisions chronologiques

### Décision #1 — Serveur d'inférence : **Ollama**
- **Date** : 2026-07-01
- **Choix** : Ollama natif Windows (GPU).
- **Alternatives écartées** :
  - *Triton Inference Server* : puissant mais lourd (image ~10 Go, téléchargement HF, config GPU) → risque de blocage chronophage sur 7h. Gardé comme **bonus documenté**.
  - *Serveur maison (FastAPI + transformers)* : flexible mais tout à recoder + gestion mémoire manuelle.
- **Justification** : solution clé en main recommandée par le sujet, install rapide, API REST standard sur `:11434`, quantization gérée automatiquement (GGUF), support GPU natif Windows.

### Décision #2 — Modèle servi : **`phi3.5` générique + system prompt**
- **Date** : 2026-07-01
- **Choix** : servir le `phi3.5` du registre Ollama avec le system prompt financier (Modelfile).
- **Alternative écartée** : fusionner l'adapter LoRA → GGUF → import Ollama. Écartée pour le temps imparti (conversion + VRAM + risque d'échec) ; la spécialisation « finance » est portée par le system prompt, suffisant pour la démo.
- **Justification** : fiabilité de la démo > exactitude du fine-tuning sur un hackathon.

### Décision #3 — Mode d'exécution : **Ollama natif Windows**
- **Date** : 2026-07-01
- **Choix** : installation native Windows (pas Docker).
- **Alternative écartée** : Ollama en conteneur Docker → GPU passthrough via WSL2 plus fragile à régler sur 7h.
- **Justification** : install 1 clic, détection GPU RTX 4070 automatique, zéro configuration WSL.

### Décision #4 — Exposition réseau : **bind 0.0.0.0 + Tailscale**
- **Date** : 2026-07-01
- **Contexte** : les développeurs web sont **à distance** (réseau différent).
- **Choix** : `OLLAMA_HOST=0.0.0.0:11434` + tunnel **Tailscale** (VPN maillé privé).
- **Alternatives écartées** :
  - *ngrok* : URL publique instantanée mais **exposition publique sans authentification** → Ollama n'a pas d'auth, risque de sécurité (audité par l'équipe CYBER), session gratuite limitée.
  - *Cloudflare Tunnel* : viable mais setup plus long.
  - *Bind LAN seul* : insuffisant car les dev web ne sont pas sur le même réseau.
- **Justification** : Tailscale n'expose **rien publiquement** ; seuls les coéquipiers invités au tailnet accèdent au serveur → choix « pro » et défendable côté sécurité.

### Décision #5 — Paramètres d'inférence (Modelfile)
- **Date** : 2026-07-01
- **Choix** : compléter le TODO du Modelfile avec des paramètres orientés **factualité** (assistant financier) :
  `temperature 0.3`, `top_p 0.9`, `num_predict 512`, `num_ctx 4096`, `repeat_penalty 1.1`.
- **Justification** : une température basse limite les hallucinations sur des sujets financiers ; `num_ctx 4096` correspond à la fenêtre de Phi-3-mini.

---

## 3. Commandes clés exécutées

```powershell
# 1. Installation d'Ollama (natif Windows, non-interactif)
winget install --id Ollama.Ollama -e --accept-source-agreements --accept-package-agreements --silent
# → Ollama 0.31.1 installé dans %LOCALAPPDATA%\Programs\Ollama

# 2. Vérification serveur (le service démarre automatiquement)
Invoke-RestMethod -Uri "http://localhost:11434/api/tags"   # → serveur OK

# 3. Téléchargement du modèle de base
ollama pull phi3.5                                          # ~2.2 Go

# 4. Création du modèle personnalisé depuis le Modelfile
ollama create techcorp-finance -f ollama_server/Modelfile

# 5. Test d'inférence
ollama run techcorp-finance "What is diversification in investing?"

# --- EXPOSITION RÉSEAU ---
# 6. Écouter sur toutes les interfaces (défaut = 127.0.0.1 seulement)
[Environment]::SetEnvironmentVariable("OLLAMA_HOST","0.0.0.0:11434","User")  # persistant
$env:OLLAMA_HOST = "0.0.0.0:11434"; ollama serve                            # session courante

# 7. Pare-feu Windows — autoriser le port (⚠️ PowerShell ADMIN requis)
New-NetFirewallRule -DisplayName "Ollama 11434" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 11434 -Profile Any

# 8. Tailscale — authentification (ouvre le navigateur)
& "C:\Program Files\Tailscale\tailscale.exe" up
& "C:\Program Files\Tailscale\tailscale.exe" ip -4   # récupère l'IP 100.x à donner aux dev web
```

### État de l'exposition réseau
- ✅ Ollama bind `0.0.0.0:11434` (vérifié : port en écoute sur `::`, API répond).
- ✅ Variable `OLLAMA_HOST` persistée au niveau utilisateur.
- ✅ Tailscale 1.98.8 installé et **authentifié** (compte `mathysc73@`, machine `desktop-57p5cmk`).
- ✅ **IP Tailscale = `100.103.147.99`** → API + inférence testées OK via cette IP.
- ⏳ **Action utilisateur restante** : règle pare-feu Windows (PowerShell admin) pour garantir l'accès des pairs distants.

### 🔌 URL de connexion pour l'équipe DEV WEB
```
http://100.103.147.99:11434
```
(prérequis : le dev web doit avoir rejoint le même tailnet Tailscale)

### ✅ Validation de bout en bout (accès distant réel)
- **Pair distant** : machine `alenzo` (`100.65.233.90`, compte `alenzo.amico@`) invitée sur le tailnet.
- **Connectivité** : `tailscale ping` → `pong from alenzo ... via 86.210.216.74:41641 in 32ms` (**chemin direct**, pas de relais).
- **Test applicatif** : le dev web a confirmé que `http://100.103.147.99:11434` **répond depuis sa machine** (API + modèle).
- **Incident résolu** : bref « offline » côté pair suite à un changement d'IP réseau local (reconnexion Wi-Fi, `self=192.168.1.186`) ; Tailscale a réétabli le chemin direct automatiquement.
- **Pare-feu** : règle `Ollama 11434` (Inbound/Allow/Enabled) confirmée en place.

📸 **Capture à prendre ici** : côté dev web, le `curl http://100.103.147.99:11434/api/tags` qui renvoie la liste des modèles (preuve d'accès distant).

📸 **Capture à prendre** : navigateur d'authentification Tailscale connecté (dashboard « Machines » avec ta machine).
📸 **Capture à prendre** : `tailscale status` montrant la machine connectée + son IP 100.x.

![Tailscale machine connectée](captures/tailscale-status.png)

---

## 4. Points de blocage & résolutions

| # | Blocage | Résolution |
|---|---|---|
| B1 | `winget install tailscale.tailscale` → *No package found* (exit 20) | ID incorrect. Bon ID : **`Tailscale.Tailscale`** (majuscules). Trouvé via `winget search tailscale`. |
| B2 | `ollama create` → `Error: invalid float value [0.3 # basse...]` | Ollama **n'accepte pas de commentaire `#` en fin de ligne `PARAMETER`**. Corrigé : commentaires déplacés sur des lignes dédiées au-dessus de chaque paramètre. |
| B3 | Serveur non persistant : l'app tray ne relance pas le serveur en contexte non-interactif ; un `ollama serve` en tâche de fond meurt avec la session. | Créé **`ollama_server/start-ollama.ps1`** (bind 0.0.0.0). Lancé en **processus détaché** (survit à la session) + **raccourci dans le dossier Démarrage** (`shell:startup`) pour relance auto au logon. |
| B4 | `New-NetFirewallRule` et `Register-ScheduledTask` → **Accès refusé** (droits admin requis). | Contourné sans admin via le dossier Démarrage utilisateur. La règle pare-feu reste à ajouter en PowerShell admin (recommandé pour les pairs distants). |

## 4bis. Validation du serveur (preuves)

- **Modèle créé** : `techcorp-finance:latest` (2.2 Go sur disque) + base `phi3.5:latest`.
- **Test d'inférence** (`POST /api/generate`, question financière) : réponse correcte et pertinente.
- **Performance** : **~85 tokens/s**, modèle chargé **100% GPU** (3.8 Go VRAM / 8 Go), contexte 4096.
  ```
  NAME                       SIZE      PROCESSOR    CONTEXT
  techcorp-finance:latest    3.8 GB    100% GPU     4096
  ```

![ollama list + modèle techcorp-finance](captures/ollama-list.png)
![ollama ps 100% GPU + réponse inférence](captures/ollama-inference-gpu.png)

---

## 5. Captures d'écran

_(emplacements réservés au fil des étapes)_
