#!/usr/bin/env bash
set -euo pipefail

# Change this to the model you want to install
MODEL="hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF"

# 1) Ensure ollama CLI is available
if ! command -v ollama >/dev/null 2>&1; then
  echo "ollama not found. Install from https://ollama.com/docs/quickstart"
  echo "Example (Linux):"
  echo "  curl https://ollama.com/install | sh"
  exit 1
fi

echo "ollama CLI found: $(ollama --version 2>/dev/null || echo '(version unknown)')"

# 2) Try to pull the model if 'pull' exists, otherwise run once to force download
if ollama help 2>&1 | grep -q -E '\bpull\b'; then
  echo "Using 'ollama pull' to download model: $MODEL"
  ollama pull "$MODEL"
else
  echo "'ollama pull' not available; using 'ollama run' to trigger download for: $MODEL"
  ollama run "$MODEL" --command "echo model_download_complete" || true
fi

# 3) Show installed models (attempt common list commands)
echo "Installed models (attempting common list commands):"
if ! (ollama ls 2>/dev/null || ollama list 2>/dev/null); then
  echo "(Could not list models with 'ollama ls' or 'ollama list' — check your ollama version)"
fi

echo "Done. If you hit resource errors, ensure your Codespace has enough disk/ram and Ollama is configured."
