# Web Scraper to SQLite - Production Dockerfile
# ============================================

# Use official Python 3.11 slim image for production
FROM python:3.11-slim AS builder

# Set environment variables for Python optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libxml2-dev \
    libxslt-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Runtime stage (smaller final image)
# ============================================
FROM python:3.11-slim AS runtime

# Install runtime system dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/logs /app/data/cache && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check (checks if the application is running)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port for monitoring/metrics (optional)
EXPOSE 8080

# Default command (can be overridden)
CMD ["python", "main.py", "--url", "file://./data/input/example.html", "--verbose"]

# ============================================
# Alternative entry points (for different use cases)
# ============================================

# For running tests
# CMD ["pytest", "tests/", "-v", "--cov=src"]

# For interactive development
# CMD ["python"]

# For production with external URL
# CMD ["python", "main.py", "--url", "https://example.com/products"]