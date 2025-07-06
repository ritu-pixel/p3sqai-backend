# Use an official Python runtime with Debian (includes g++, cmake)
FROM python:3.9-slim as builder

# Install system dependencies for sentencepiece and other requirements
RUN apt-get update && apt-get install -y \
    g++ \
    cmake \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy requirements first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ========== Runtime Stage ==========
FROM python:3.9-slim

# Copy only necessary runtime dependencies from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application
COPY . .

# Ensure port is configurable
ENV PORT=8080
EXPOSE $PORT

# Run as non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Run the app (ensure main.py listens on PORT)
CMD ["python", "main.py"]
