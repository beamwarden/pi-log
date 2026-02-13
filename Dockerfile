# filename: Dockerfile
FROM python:3.11-slim

# Install OS packages needed for serial access
RUN apt-get update && apt-get install -y --no-install-recommends \
    libudev1 \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy dependency list first for layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default command: run the ingestion agent
CMD ["python", "-m", "app.ingestion.geiger_reader"]

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8080/health').raise_for_status()" || exit 1
