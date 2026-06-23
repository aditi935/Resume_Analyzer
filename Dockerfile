# ── Base image ────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# ── Metadata ──────────────────────────────────────────────────────────────────
LABEL maintainer="your-email@example.com"
LABEL description="ATS Resume Analyzer – Streamlit App"

# ── System dependencies ───────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Install Python dependencies first (layer caching) ────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Copy application source ───────────────────────────────────────────────────
COPY . .

# ── Streamlit config (disable telemetry & set port) ──────────────────────────
ENV STREAMLIT_TELEMETRY_DISABLED=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# ── Expose port ───────────────────────────────────────────────────────────────
EXPOSE 8501

# ── Health check ─────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# ── Entrypoint ────────────────────────────────────────────────────────────────
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]