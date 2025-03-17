#!/bin/sh
# Start the Ollama daemon in the background
ollama daemon > /dev/null 2>&1 &
# Wait for the daemon to initialize
sleep 10
# Pull the Llama3.2 model
ollama pull llama3.2:latest
# Run your main Python script
python main.py
