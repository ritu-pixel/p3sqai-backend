# Use an official Python runtime with Debian (includes g++, cmake)
FROM python:3.9-slim

# Install system dependencies for sentencepiece
RUN apt-get update && apt-get install -y \
    g++ \
    cmake \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Run the app (ensure main.py listens on PORT)
CMD ["python", "main.py"]
