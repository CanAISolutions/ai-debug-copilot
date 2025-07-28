FROM python:3.10-slim

WORKDIR /app

# Copy application code
COPY app ./app
COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Initialize the metrics database at build time so the file exists when the
# container starts. This runs a small Python snippet that imports the
# init_db function and creates the SQLite table if it does not already exist.
RUN python - <<'EOF'
from app.utils.metrics import init_db
init_db()
EOF

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]