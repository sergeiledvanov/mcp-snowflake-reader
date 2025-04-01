FROM python:3.10-slim

WORKDIR /app

# Install system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY src/mcp_snowflake_reader/main.py .

# Set execute permission
RUN chmod +x main.py

# Run the application
ENTRYPOINT ["python", "main.py"] 