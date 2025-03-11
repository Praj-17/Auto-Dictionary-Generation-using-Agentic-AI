FROM python:3.10-slim

# Install system dependencies required for Ollama
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | bash

# Start the Ollama daemon in the background, wait for it to initialize, then pull the Llama3.2 model
RUN nohup ollama daemon > /dev/null 2>&1 & \
    sleep 10 && \
    ollama pull ollama/llama3.2:latest

# Set the working directory inside the container
WORKDIR /app

# Copy the entire project directory to the container
COPY . /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Run the script
CMD ["python", "main.py"]
