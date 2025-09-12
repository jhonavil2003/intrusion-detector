FROM python:3.12-slim

# Prevent Python from writing .pyc files and force stdout/stderr unbuffered
ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY --chown=appuser:appuser worker/entrypoint/worker.py .

# Run
CMD ["python", "worker.py"]
