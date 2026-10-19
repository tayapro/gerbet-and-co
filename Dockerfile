# syntax=docker/dockerfile:1
FROM python:3.12-slim

# --- Environment ---
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# --- Working directory ---
WORKDIR /app

# --- System dependencies (as root) ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# --- Non-root user with fixed UID/GID ---
ARG USER_ID=1001
ARG GROUP_ID=1001
RUN groupadd --gid $GROUP_ID appuser \
    && useradd --uid $USER_ID --gid $GROUP_ID --create-home --shell /bin/bash appuser \
    && chown appuser:appuser /app

# --- Copy project code with correct ownership ---
COPY --chown=appuser:appuser accounts/ accounts/
COPY --chown=appuser:appuser bag/ bag/
COPY --chown=appuser:appuser checkout/ checkout/
COPY --chown=appuser:appuser gerbet_and_co/ gerbet_and_co/
COPY --chown=appuser:appuser products/ products/
COPY --chown=appuser:appuser static/ static/
COPY --chown=appuser:appuser store/ store/
COPY --chown=appuser:appuser templates/ templates/
COPY --chown=appuser:appuser manage.py .
COPY --chown=appuser:appuser requirements.txt .

# --- Install Python deps as root (go to /usr/local, readable by all) ---
RUN pip install --no-cache-dir -r requirements.txt

# --- Switch to non-root for everything else ---
USER appuser

# --- Collect static with SQLite dummy (no real DB needed at build time) ---
RUN DATABASE_URL="sqlite:////tmp/dummy.sqlite3" \
    python manage.py collectstatic --noinput \
    && rm -f /tmp/dummy.sqlite3

# --- Expose ---
EXPOSE 8002

# --- Start server (port 8002 > 1024, no root needed) ---
CMD ["gunicorn", "gerbet_and_co.wsgi:application", "--bind", "0.0.0.0:8002"]
