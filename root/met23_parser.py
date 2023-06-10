# pylint: disable = C0321
"""
Scraper and parser for met23.ru website
Main goal is to scrape all data about item and save it to csv
"""
import logging
import sys
from dataclasses import dataclass
from urllib.parse import urljoin
import time

from httpx import Client
from selectolax.parser import HTMLParser, Node
from rich import print

from metal_tree import MetalTreeNode
from solve_recaptcha import solve, get_captcha

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

MAIN_URL = "https://multicity.23met.ru/"
PROXIES = {"http://": "http://91.148.146.136:55443"}


@dataclass
class Response:
    """ all data we need from response """
    html_body: str
    status: int


@dataclass
class MainCategory:
    """ contains usefull data for main categories """
    name: str
    href: str


@dataclass
class SubCategory:
    """ usesful data for sub-categories """
    name: str
    href: str
    #size: str


def extract_name(tag):
    """ extracting text data from "li" """
    return tag.text()


def extract_href(tag):
    """ ectracting href data from "li" """
    return tag.css_first("a").attrs['href']


def is_valid(data: list) -> bool:
    """ check for changes in website structure """
    if len(data) == 0:
        logger.warning(
            "Seems that website changed structure. Please recheck code and website")
        return False
    else:
        return True


def get_main_page(client: Client, url) -> Response:
    """ get main page html """
    response = client.get(url, headers=HEADERS)
    page = HTMLParser(response.text)

    return Response(html_body=page, status=response.status_code)


def parse_navbar(categories: list) -> list:
    """ parse each main_category node """
    result = []

    for category in categories:
        result.append(MainCategory(name=extract_name(category),
                                   href=extract_href(category)))

    return result


def get_main_categories(page: Response) -> list:
    """ extracts data about main categories """
    navbar_data = page.html_body.css(
        "div#header-wrap > ul > li")

    if is_valid(navbar_data):
        main_categories = navbar_data[1:3]
        toggle_data = navbar_data[3].css("ul > li")
    else:
        main_categories = None

    return parse_navbar(main_categories + toggle_data)


def scrape_subcategories(client: Client, url: str, tree):
    """ extract subcategories """
    response = client.get(url, headers=HEADERS)
    page = HTMLParser(response.text)
    subcategories = page.css("nav#left-container > ul[class='tabs '] > li > a")

    for category in subcategories:
        new_child = SubCategory(name=extract_name(category),
                                href=extract_href(category))
        tree.add_child(new_child)
    
def parse_met23():
    """ main logic for parser """
    client = Client(proxies=PROXIES)

    main_page = get_main_page(client, MAIN_URL)
    tree = MetalTreeNode("23.met.ru")
    # always need to check response status code
    # if problems with connection try rotate proxy
    if main_page.status == 200:
        main_categories = get_main_categories(main_page)
        # add our main categories to tree
        for category in main_categories:
            tree.add_child(category)
            
    elif main_page.status == 429:
        captcha = get_captcha(main_page.html_body)
        solve(client, captcha, HEADERS)

    else:
        print("Oops, you blocked!")
        print(main_page.status)

        # rotate proxy

    # first try to scrape one category
    time.sleep(1)
    scrape_subcategories(client, tree.get_child().href, tree)
    print(tree.get_children())
    # for node in tree.get_children():
    #     scrape_subcategories(client, node.href)


parse_met23()
