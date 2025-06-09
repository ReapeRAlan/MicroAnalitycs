"""Ollama-based chatbot for demand prediction."""

import json
import os
import requests
from ollama import Client

API_URL = "http://localhost:8000/predict"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")


def handle_command(text: str) -> str:
    """Process /demanda commands and return the API response text."""
    if not text.startswith("/demanda"):
        return ""
    payload_str = text[len("/demanda"):].strip()
    try:
        data = json.loads(payload_str)
    except ValueError:
        return "Formato JSON invalido"
    try:
        resp = requests.post(API_URL, json=data, timeout=3)
        resp.raise_for_status()
        pred = resp.json().get("prediction")
        return f"La demanda estimada es: {pred}"
    except requests.exceptions.RequestException:
        return "Error al obtener la prediccion"


def main() -> None:
    client = Client(host=OLLAMA_URL)
    history = []
    print("Escribe mensajes o /demanda {json}. 'quit' para salir.")
    while True:
        user_msg = input("> ")
        if user_msg.lower() in {"quit", "exit"}:
            break
        reply = handle_command(user_msg)
        if reply:
            print(reply)
            continue
        history.append({"role": "user", "content": user_msg})
        response = client.chat(model="llama2", messages=history)
        message = response["message"]["content"]
        history.append({"role": "assistant", "content": message})
        print(message)


if __name__ == "__main__":
    main()
