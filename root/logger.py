""" Logger """
import logging
import sys

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s:%(name)s:%(lineno)d:%(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
