# Use official Python image
FROM python:3.12-slim

ARG DATABASE_URL
ENV DATABASE_URL=$DATABASE_URL

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project code
COPY accounts/ accounts/
COPY bag/ bag/
COPY checkout/ checkout/
COPY gerbet_and_co/ gerbet_and_co/
COPY products/ products/
COPY static/ static/
COPY store/ store/
COPY templates/ templates/
COPY manage.py .
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Collect static files (optional for production)
RUN python manage.py collectstatic --noinput

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose port (optional)
EXPOSE 8002

# Start server
CMD ["gunicorn", "gerbet_and_co.wsgi:application", "--bind", "0.0.0.0:8002"]
