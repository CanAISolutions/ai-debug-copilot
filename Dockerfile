FROM python:3.10-slim AS base

# ----- Build stage -----
FROM base AS build

# System-level packages required for some Python wheels (e.g. scipy)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ----- Final image -----
FROM base
WORKDIR /app

# Re-install Python dependencies in the runtime image to guarantee all console
# entry points (e.g. uvicorn) are present even if wildcard copy misses them.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy virtual environment from build layer (uses the default site-packages path)
COPY --from=build /usr/local/lib/python*/ /usr/local/lib/python*/
COPY --from=build /usr/local/bin/ /usr/local/bin/

# Copy application code
COPY app ./app

# Pre-create the SQLite metrics DB so the directory exists with correct perms
RUN python - <<'EOF'
from app.utils.metrics import init_db
init_db()
EOF

# Expose the port Render injects via $PORT (default 8000 for local dev)
ENV PORT=8000
EXPOSE $PORT

# Render sets PORT env var automatically; reference it in CMD
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]