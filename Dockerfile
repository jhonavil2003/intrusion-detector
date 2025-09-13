FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN groupadd -g 1000 app && useradd -m -u 1000 -g 1000 app
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir -r /app/requirements.txt

COPY --chown=app:app intrusion-detector /app/intrusion-detector

RUN mkdir -p /data && chown -R app:app /data
VOLUME ["/data"]
USER app

ENTRYPOINT ["python", "-m", "intrusion-detector.worker.entrypoint.worker"]