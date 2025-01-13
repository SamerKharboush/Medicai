# Build stage
FROM python:3.9-slim as builder

# Create Python virtual environment
RUN python -m venv /opt/venv

# Configure apt settings
RUN echo 'Acquire::ForceIPv4 "true";' > /etc/apt/apt.conf.d/99force-ipv4 && \
    echo "deb http://deb.debian.org/debian/ bookworm main" > /etc/apt/sources.list && \
    echo "deb http://security.debian.org/debian-security/ bookworm-security main" >> /etc/apt/sources.list

# Install system dependencies with retry mechanism
RUN --mount=type=cache,target=/var/cache/apt \
    for i in $(seq 1 3); do \
        (apt-get update && \
         apt-get install -y --no-install-recommends \
            build-essential \
            git \
            ffmpeg && \
         rm -rf /var/lib/apt/lists/*) && break || sleep 15; \
    done

# Configure pip to use alternative mirrors
RUN /opt/venv/bin/pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    /opt/venv/bin/pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# Update pip and install dependencies with retry mechanism
RUN --mount=type=cache,target=/root/.cache/pip \
    for i in $(seq 1 3); do \
        /opt/venv/bin/pip install --no-cache-dir --timeout 100 --retries 5 --upgrade pip setuptools wheel && break || sleep 15; \
    done

# Install basic dependencies with retry mechanism
RUN --mount=type=cache,target=/root/.cache/pip \
    for i in $(seq 1 3); do \
        /opt/venv/bin/pip install --no-cache-dir --timeout 100 --retries 5 \
            "fastapi>=0.68.1" \
            "uvicorn>=0.15.0" \
            "sqlalchemy>=1.4.23" \
            "psycopg2-binary>=2.9.1" \
            "python-multipart>=0.0.5" \
            "python-jose[cryptography]>=3.3.0" \
            "bcrypt==4.0.1" \
            "passlib[bcrypt]>=1.7.4" \
            "pydantic[email]>=1.8.2" \
            "pydantic-settings>=2.0.0" \
            "python-dotenv>=0.19.0" \
            "aiofiles>=0.7.0" \
            "alembic>=1.12.0" && break || sleep 15; \
    done

# Install ML dependencies in smaller groups
RUN for i in $(seq 1 3); do \
        /opt/venv/bin/pip install --no-cache-dir --retries 5 \
        "numpy==1.24.3" && break || sleep 15; \
    done

RUN for i in $(seq 1 3); do \
        /opt/venv/bin/pip install --no-cache-dir --retries 5 \
        "pandas>=2.0.3" \
        "scipy>=1.10.1" && break || sleep 15; \
    done

RUN for i in $(seq 1 3); do \
        /opt/venv/bin/pip install --no-cache-dir --retries 5 \
        "scikit-learn>=1.3.0" && break || sleep 15; \
    done

# Install PyTorch first as it's a dependency for whisper
RUN --mount=type=cache,target=/root/.cache/pip \
    for i in $(seq 1 3); do \
        /opt/venv/bin/pip install --no-cache-dir --find-links https://download.pytorch.org/whl/torch_stable.html "torch>=2.1.0" && break || sleep 15; \
    done

RUN --mount=type=cache,target=/root/.cache/pip \
    for i in $(seq 1 3); do \
        /opt/venv/bin/pip install --no-cache-dir "torchaudio>=2.1.0" && break || sleep 15; \
    done

# Install whisper
RUN for i in $(seq 1 3); do \
        /opt/venv/bin/pip install --no-cache-dir --retries 5 \
        "openai-whisper>=20231117" \
        "ffmpeg-python>=0.2.0" && break || sleep 15; \
    done

# Install SpaCy and download model with improved retry logic
RUN --mount=type=cache,target=/root/.cache/pip \
    for i in $(seq 1 5); do \
        (pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
         /opt/venv/bin/pip install --no-cache-dir --timeout 180 --retries 10 "spacy==3.6.1" && \
         pip config unset global.index-url && \
         /opt/venv/bin/python -m spacy download en_core_web_sm) && break || \
        (echo "Attempt $i failed, retrying in 30 seconds..." && sleep 30); \
    done

# Production stage
FROM python:3.9-slim

# Configure apt settings
RUN echo 'Acquire::ForceIPv4 "true";' > /etc/apt/apt.conf.d/99force-ipv4 && \
    echo "deb http://deb.debian.org/debian/ bookworm main" > /etc/apt/sources.list && \
    echo "deb http://security.debian.org/debian-security/ bookworm-security main" >> /etc/apt/sources.list

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    postgresql-client \
    ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create app directory and set permissions
RUN mkdir -p /app/models && \
    mkdir -p /app/.cache/whisper && \
    chown -R nobody:nogroup /app

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=nobody:nogroup . .

# Create entrypoint script
RUN echo '#!/bin/sh\n\
set -e\n\
\n\
# Wait for postgres\n\
until pg_isready -h db -p 5432; do\n\
  >&2 echo "Postgres is unavailable - sleeping"\n\
  sleep 1\n\
done\n\
\n\
>&2 echo "Postgres is up - executing command"\n\
\n\
# Run the command\n\
exec "$@"' > /app/docker-entrypoint.sh && \
    chmod +x /app/docker-entrypoint.sh

# Set environment path
ENV PATH="/opt/venv/bin:$PATH"

# Set entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Default command
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
