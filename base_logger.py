import logging

logger = logging
logger.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S'
)
