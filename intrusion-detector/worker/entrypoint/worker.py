import json,os
from ..observability.logging import setup_logging
from ..adapters.aws.sqs_consumer import SQSConsumer
from ..adapters.aws.sns_publisher import SNSPublisher
from ..adapters.aws.event_parse import extract
from ..service.processor import WorkerFactory, Processor
from ..config.settings import Settings


def main():
    log = setup_logging()
    cfg = Settings.from_env()
    if not cfg.queue_url: raise SystemExit("AUTH_ATTEMPTS_QUEUE_URL no configurado")
    os.makedirs(os.path.dirname(cfg.profiles_path), exist_ok=True)
    if not os.path.exists(cfg.profiles_path): json.dump({}, open(cfg.profiles_path, "w"))
    consumer = SQSConsumer(cfg.region, cfg.queue_url)
    publisher = SNSPublisher(cfg.region) if cfg.publish_sns else None
    topics = {"risk": cfg.topic_risk_scores, "decision": cfg.topic_decisions, "challenge": cfg.topic_challenges}
    use_case = WorkerFactory.build_use_case(cfg.profiles_path)
    processor = Processor(use_case, publisher, topics)
    log.info("Worker iniciado - cola= %s region= %s", cfg.queue_url, cfg.region)
    log.info("Worker iniciado - messageMax=%s wait=%s timeout=%s", cfg.max_number_of_messages, cfg.wait_time_seconds,
             cfg.visibility_timeout)
    while True:
        for msg in consumer.receive(cfg.max_number_of_messages, cfg.wait_time_seconds, cfg.visibility_timeout):
            payload = extract(msg.body)
            try:
                result = processor.handle(payload)
                log.info("Procesado: %s", result)
                consumer.delete(msg.receipt)
            except Exception as e:
                log.exception("Error procesando mensaje: %s", e)


if __name__ == "__main__": main()