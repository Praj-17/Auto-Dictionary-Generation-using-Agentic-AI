FROM python:3.10-slim

# Install system dependencies required for Ollama
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | bash

# Set the working directory
WORKDIR /app

# Copy the entire project directory to the container
COPY . /app

# Install Python dependencies
RUN pip install -r requirements.txt

RUN pip install simplerllm==0.3.1.13

# Copy the entrypoint script and make it executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint script as the container's startup command
CMD ["/app/entrypoint.sh"]
