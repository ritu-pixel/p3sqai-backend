FROM python:3.10-slim  # Changed from 3.9 to 3.10

# Rest of your Dockerfile remains the same
RUN apt-get update && apt-get install -y g++ cmake make
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
