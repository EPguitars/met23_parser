"""
Scraper and parser for met23.ru website
Main goal is to scrape all data about item and save it to csv
"""
import logging
import sys
from dataclasses import dataclass
from urllib.parse import urljoin

from httpx import Client
from selectolax.parser import HTMLParser

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s:%(name)s:%(lineno)d:%(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
           "AppleWebKit/537.36 (KHTML, like Gecko) " +
           "Chrome/109.0.0.0 Safari/537.36"}
