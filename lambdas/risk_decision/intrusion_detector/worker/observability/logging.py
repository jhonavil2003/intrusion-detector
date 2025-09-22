import logging, os


def setup_logging():
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s %(message)s", level=level)
    return logging.getLogger("intrusion_detector.intrusion_detector")
