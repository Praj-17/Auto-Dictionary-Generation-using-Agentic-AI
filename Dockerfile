FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the entire project directory to the container
COPY . /app

# Install dependencies (if any)
RUN pip install -r requirements.txt

# Run the script
CMD ["python", "main.py"]
