#!/usr/bin/env python3
"""
TechCorp — Assistant Financier | Interface de chat (DEV WEB)
Se connecte au serveur d'inference deploye par l'INFRA (Ollama par defaut).

Fonctionnalites :
- Chat en temps reel avec streaming des reponses
- Historique de la conversation persiste dans la session
- Indicateur d'etat de connexion au serveur (connecte / deconnecte)
- Selection du modele et de l'URL du serveur (sidebar)

Lancement : streamlit run app.py   (ou ./run.ps1 / ./run.sh)
"""

import json
import requests
import streamlit as st

DEFAULT_BASE_URL = "http://100.103.147.99:11434"   # Ollama INFRA (via Tailscale)
DEFAULT_MODEL = "techcorp-finance"
REQUEST_TIMEOUT = 5                            # timeout du ping de sante


# --------------------------------------------------------------------------- #
# Communication avec le serveur d'inference (Ollama)
# --------------------------------------------------------------------------- #
def check_connection(base_url: str):
    """Ping le serveur. Retourne (est_connecte: bool, modeles: list[str])."""
    try:
        resp = requests.get(f"{base_url}/api/tags", timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        models = [m["name"] for m in resp.json().get("models", [])]
        return True, models
    except requests.RequestException:
        return False, []


def stream_chat(base_url: str, model: str, messages: list):
    """Envoie l'historique a /api/chat et yield les fragments de reponse."""
    payload = {"model": model, "messages": messages, "stream": True}
    with requests.post(
        f"{base_url}/api/chat", json=payload, stream=True, timeout=120
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line:
                continue
            chunk = json.loads(line.decode("utf-8"))
            if chunk.get("done"):
                break
            content = chunk.get("message", {}).get("content", "")
            if content:
                yield content


# --------------------------------------------------------------------------- #
# Interface
# --------------------------------------------------------------------------- #
st.set_page_config(page_title="TechCorp — Assistant Financier", page_icon="💰")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---- Sidebar : configuration + etat de connexion ------------------------- #
with st.sidebar:
    st.header("⚙️ Serveur d'inference")
    base_url = st.text_input("URL du serveur", value=DEFAULT_BASE_URL).rstrip("/")

    connected, available_models = check_connection(base_url)

    if connected:
        st.success("🟢 Connecte", icon="✅")
    else:
        st.error("🔴 Deconnecte — serveur injoignable", icon="🚫")

    if available_models:
        model = st.selectbox("Modele", options=available_models)
    else:
        model = st.text_input("Modele", value=DEFAULT_MODEL)

    st.divider()
    if st.button("🗑️ Effacer l'historique", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption(f"{len(st.session_state.messages)} message(s) dans l'historique")

# ---- Zone principale : historique + chat --------------------------------- #
st.title("💰 Assistant Financier TechCorp")
st.caption("Interface de chat connectee au modele Phi-3.5-Financial")

# Affiche l'historique de la conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Nouvelle saisie utilisateur
if prompt := st.chat_input("Posez votre question financiere...", disabled=not connected):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            full = st.write_stream(
                stream_chat(base_url, model, st.session_state.messages)
            )
        except requests.RequestException as exc:
            full = f"⚠️ Erreur de communication avec le serveur : {exc}"
            st.error(full)

    st.session_state.messages.append({"role": "assistant", "content": full})

if not connected:
    st.info(
        "Le serveur d'inference est injoignable. Verifiez avec l'equipe INFRA "
        f"que le modele tourne bien sur `{base_url}` (Ollama : `ollama serve`)."
    )
