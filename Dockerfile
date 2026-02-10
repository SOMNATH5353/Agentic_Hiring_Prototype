FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p temp_uploads temp_outputs storage

# Expose port (Koyeb will set PORT env variable)
EXPOSE 8000

# Run the application with single worker (important for in-memory JD caching)
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
