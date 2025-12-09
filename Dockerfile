FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY pyproject.toml setup.py ./
COPY src/ src/

# Install the package
RUN pip install --no-cache-dir .

# Default port
ENV PORT=8000
ENV HOST=0.0.0.0

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -sf http://localhost:${PORT}/mcp || exit 1

# Run HTTP server
CMD python -m instantly_mcp.server --transport http --host 0.0.0.0 --port $PORT

