import logging, os

logger = logging.getLogger("eventregistry")
if len(logger.handlers) == 0:
    logger.addHandler(logging.StreamHandler())

# by default just log from Warning level up
logger.setLevel(level = os.environ.get("LOGLEVEL", "WARNING"))