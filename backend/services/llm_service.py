import os
import json
import httpx
from typing import Optional

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")


def check_ollama_health() -> bool:
    try:
        response = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3.0)
        return response.status_code == 200
    except Exception:
        return False


def query_ollama(prompt: str, system: Optional[str] = None, temperature: float = 0.5, timeout_sec: float = 45.0) -> Optional[str]:
    """
    Sends prompt to local Ollama instance running llama3.2:latest.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }
    if system:
        payload["system"] = system

    try:
        response = httpx.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=timeout_sec)
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "").strip()
        else:
            print(f"Ollama error: HTTP {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Ollama request failed: {e}")
        return None


def generate_llm_response(prompt: str, system: Optional[str] = None, fallback_text: Optional[str] = None) -> str:
    """
    Primary LLM invoker: Ollama llama3.2:latest.
    Gracefully returns structured response or intelligent fallback if Ollama times out.
    """
    ollama_res = query_ollama(prompt, system=system)
    if ollama_res:
        return ollama_res

    if fallback_text:
        return fallback_text

    return (
        "I analyzed your engineering notes, but the local model response was interrupted. "
        "Please verify that Ollama is running with `ollama run llama3.2:latest`."
    )
