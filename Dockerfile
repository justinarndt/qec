# ASR-MP Decoder Docker Environment
#
# Build: docker build -t asr-mp .
# Run:   docker run -it asr-mp pytest tests/ -v
# Shell: docker run -it asr-mp bash

FROM python:3.10-slim

LABEL maintainer="Justin Arndt"
LABEL description="ASR-MP Decoder - BP+OSD for Quantum Error Correction"
LABEL version="1.0.0-alpha"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements-dev.txt

# Copy source code
COPY . .

# Install package
RUN pip install -e .

# Default command
CMD ["pytest", "tests/", "-v"]
