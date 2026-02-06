# Backend API Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml ./
COPY backend/ ./backend/

# Install Python dependencies
RUN pip install --no-cache-dir .

# Create directory for ChromaDB
RUN mkdir -p /app/chroma_db

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV FRONTEND_URL=http://localhost:3000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the API server
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000"]
