FROM python:3.12-slim

# Prevent Python from writing .pyc files and force stdout/stderr unbuffered
ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user (UID 1000 to match common EFS access point defaults)
RUN useradd -m -u 1000 appuser
USER appuser

# Copy source
COPY --chown=appuser:appuser worker/entrypoint/worker.py .

# Run
CMD ["python", "worker.py"]
