# 🔌 Fiche de connexion — Serveur d'inférence (pour l'équipe DEV WEB)

> Serveur **Ollama** hébergé par l'équipe INFRA, exposant le modèle **`techcorp-finance`** (Phi-3.5 + system prompt financier).

---

## 1. Prérequis : rejoindre le réseau Tailscale

Le serveur n'est **pas exposé publiquement** (choix de sécurité). Il est accessible via un réseau privé **Tailscale**.

1. Installez Tailscale : https://tailscale.com/download
2. Connectez-vous **au même tailnet** que l'INFRA (compte `mathysc73@` — demandez une invitation à Mathys, ou connectez-vous avec le compte partagé indiqué par l'équipe).
3. Vérifiez la connexion : `tailscale status` doit lister la machine `desktop-57p5cmk`.

## 2. URL du serveur

```
http://100.103.147.99:11434
```

- API compatible **Ollama** (et endpoint compatible OpenAI, voir §4).
- Modèle à utiliser : **`techcorp-finance`**

## 3. Vérifier que ça répond

```bash
curl http://100.103.147.99:11434/api/tags
```
→ doit renvoyer la liste des modèles (`techcorp-finance:latest`, `phi3.5:latest`).

## 4. Appeler le modèle

### Endpoint natif Ollama — `/api/generate` (réponse simple)
```bash
curl http://100.103.147.99:11434/api/generate -d '{
  "model": "techcorp-finance",
  "prompt": "What is diversification in investing?",
  "stream": false
}'
```

### Endpoint natif Ollama — `/api/chat` (avec historique)
```bash
curl http://100.103.147.99:11434/api/chat -d '{
  "model": "techcorp-finance",
  "messages": [
    {"role": "user", "content": "What is a bull market?"}
  ],
  "stream": false
}'
```

### Endpoint compatible OpenAI — `/v1/chat/completions`
Pratique si vous utilisez le SDK OpenAI (JS/Python) : il suffit de changer la `baseURL`.
```bash
curl http://100.103.147.99:11434/v1/chat/completions -d '{
  "model": "techcorp-finance",
  "messages": [{"role": "user", "content": "Explain ROI"}]
}'
```

### Exemple JavaScript (fetch, streaming)
```js
const res = await fetch("http://100.103.147.99:11434/api/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    model: "techcorp-finance",
    messages: [{ role: "user", content: userInput }],
    stream: true,
  }),
});
// res.body est un ReadableStream de lignes JSON (une par token)
```

## 5. Vérifier l'état de connexion (connecté / déconnecté)

Pour l'indicateur « serveur connecté / déconnecté » demandé dans vos consignes :
```js
async function isServerUp() {
  try {
    const r = await fetch("http://100.103.147.99:11434/api/tags", { method: "GET" });
    return r.ok;
  } catch { return false; }
}
```

## 6. En cas de souci
- **Pas de réponse / timeout** → vérifiez `tailscale status` (êtes-vous bien sur le tailnet ?).
- **Connection refused** → le serveur INFRA est peut-être éteint ; prévenez l'équipe INFRA.
- L'IP `100.x` est **stable** tant que la machine INFRA reste dans le tailnet.
