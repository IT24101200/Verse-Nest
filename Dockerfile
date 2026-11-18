# Production & Staging Dockerfile for VerseNest Platform
FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install required dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY assets/ ./assets/
COPY backend/ ./backend/
COPY guides/ ./guides/
COPY lyrics/ ./lyrics/
COPY data/ ./data/
COPY data_seed/ ./data_seed/
COPY *.html ./
COPY robots.txt ./
COPY sitemap.xml ./

# Default environment configuration
ENV PORT=8080
ENV BASE_URL=http://localhost:8080
ENV ENV=staging

EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/api/health')" || exit 1

# Start FastAPI server using production Uvicorn
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
