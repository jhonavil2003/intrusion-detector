import os, json

from ..observability.logging import setup_logging
from ..adapters.aws.sqs_consumer import SQSConsumer
from ..adapters.aws.event_parse import extract
from ..config.settings import Settings


def main():
    log = setup_logging()
    cfg = Settings.from_env()
    if not cfg.queue_url: raise SystemExit("AUTH_ATTEMPTS_QUEUE_URL no configurado")
    consumer = SQSConsumer(cfg.region, cfg.queue_url)
    log.info("Worker iniciado - cola= %s region= %s", cfg.queue_url, cfg.region)
    log.info("Worker iniciado - maxmess=%s wait=%s timeout=%s", cfg.max_number_of_messages, cfg.wait_time_seconds, cfg.visibility_timeout)
    while True:
        for msg in consumer.receive(cfg.max_number_of_messages, cfg.wait_time_seconds, cfg.visibility_timeout):
            payload = extract(msg.body)
            try:
                log.info("Mensaje Procesado: %s", payload)
                consumer.delete(msg.receipt)
            except Exception as e:
                log.exception("Error procesando mensaje: %s", e)


if __name__ == "__main__": main()