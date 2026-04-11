#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OLLAMA_HOST_VALUE="${OLLAMA_HOST:-127.0.0.1:11434}"
OLLAMA_MODELS_DIR="${OLLAMA_MODELS:-$ROOT/.ollama/models}"
OLLAMA_HOME_DIR="${OLLAMA_HOME:-$ROOT/.ollama}"

mkdir -p "$OLLAMA_MODELS_DIR" "$OLLAMA_HOME_DIR"

export HOME="$OLLAMA_HOME_DIR"
export OLLAMA_HOST="$OLLAMA_HOST_VALUE"
export OLLAMA_MODELS="$OLLAMA_MODELS_DIR"

exec ollama serve
