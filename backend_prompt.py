"""Backend module that processes a user prompt.

Tries language API via `langchain_query.ask_gpt` (OpenAI) if available,
falls back to Ollama local HTTP API, then to Ollama CLI.
"""
import json
import subprocess
import urllib.request
import urllib.error
from typing import Optional


def _call_langchain(prompt: str, model: Optional[str] = None, api_key: Optional[str] = None) -> Optional[str]:
    try:
        from langchain_query import ask_gpt
    except Exception:
        return None
    try:
        return ask_gpt(prompt, model=model or "gpt-4", api_key=api_key)
    except Exception:
        return None


def _call_ollama_http(prompt: str, model: str) -> Optional[str]:
    url = "http://localhost:11434/api/generate"
    payload = {"model": model, "prompt": prompt}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            j = json.load(resp)
            # Try common response shapes
            if isinstance(j, dict):
                if "text" in j:
                    return j["text"]
                if "response" in j:
                    return j["response"]
                if "choices" in j and j["choices"]:
                    ch = j["choices"][0]
                    if isinstance(ch, dict):
                        msg = ch.get("message") or ch.get("text")
                        if isinstance(msg, dict):
                            return msg.get("content")
                        if isinstance(msg, str):
                            return msg
            return str(j)
    except urllib.error.URLError:
        return None
    except Exception:
        return None


def _call_ollama_cli(prompt: str, model: str) -> Optional[str]:
    # Try to run the model via Ollama CLI; pass prompt on stdin where supported
    try:
        proc = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
        return proc.stdout.strip() or None
    except FileNotFoundError:
        return None
    except Exception:
        return None


def process_prompt(prompt: str, model: Optional[str] = None, api_key: Optional[str] = None) -> str:
    """Process the prompt and return the model output string.

    Order of attempts: langchain->ollama http->ollama cli. Returns an error message
    if none succeed.
    """
    # 1) Try langchain/openai helper if available
    out = _call_langchain(prompt, model=model, api_key=api_key)
    if out:
        return out

    # 2) Try Ollama HTTP API
    try_model = model or "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF"
    out = _call_ollama_http(prompt, try_model)
    if out:
        return out

    # 3) Try Ollama CLI
    out = _call_ollama_cli(prompt, try_model)
    if out:
        return out

    return "No model backend available. Ensure OPENAI_API_KEY is set or Ollama is running and model installed."


if __name__ == "__main__":
    print(process_prompt("Write a one-line summary of Python."))
