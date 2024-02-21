from loguru import logger
import json

LOGGER_CONFIG = "configs/loguru.json"


def init_logger():
    with open(LOGGER_CONFIG) as f:
        logger_config = json.load(f)
        logger.add(**logger_config)
    logger.info(
        "Initialized the logger instance with the configuration {}.".format(
        logger_config)
    )

