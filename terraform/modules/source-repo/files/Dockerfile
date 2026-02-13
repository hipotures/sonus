FROM python:3.9-slim

# Install required system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set default environment variables
ENV AUDIO_EXTENSIONS="mp3,wav,m4a,flac"
ENV VIDEO_EXTENSIONS="mp4,mov,avi,mkv"
ENV DEBUG="False"

CMD ["python", "main.py"]
