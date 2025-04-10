#!/bin/bash
set -e

# Start Ollama server in background
ollama serve &
SERVER_PID=$!

# Wait for server readiness
until curl -s http://localhost:11434 >/dev/null; do
  sleep 1
done

# Model management
if ! ollama list | grep -q WizardLM2:7B; then
  echo "Pulling model..."
  ollama pull WizardLM2:7B
fi

# Keep container running
wait $SERVER_PID
