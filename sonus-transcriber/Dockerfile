FROM python:3.11-slim

WORKDIR /app

# Install ffmpeg with minimal dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
ARG REQUIREMENTS=requirements.txt
COPY $REQUIREMENTS requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary files
COPY src/ src/
COPY setup.py .

# Install the package
RUN pip install -e .

CMD ["python", "-m", "transcriber.main"]
