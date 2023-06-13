# pylint: disable = C0321, E0401, W0622
"""
Scraper and parser for met23.ru website
Main goal is to scrape all data about item and save it to csv
"""
from dataclasses import dataclass
import time
import random
import sys

from httpx import Client
from selectolax.parser import HTMLParser
from rich import print
from httpx._exceptions import (RemoteProtocolError, ConnectTimeout, ProxyError,
                               ReadTimeout, ReadError, ConnectError)

from metal_tree import MetalTreeNode
from tools import switch_user_agent, switch_proxy
from scrape_subcategories import run_browser
import logger

MAIN_URL = "https://multicity.23met.ru/"


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


def extract_name(tag):
    """ extracting text data from "li" """
    return tag.text()


def extract_href(tag):
    """ extracting href data from "li" """
    return tag.css_first("a").attrs['href']


def is_valid(data: list) -> bool:
    """ check for changes in website structure """
    if len(data) == 0:
        logger.logger.warning(
            "Seems that website changed structure. Please recheck code and website")
        return False
    else:
        return True


def client_entity():
    """ generates a new client session """
    print("Creating a new client session")
    user_agent = switch_user_agent()
    proxy = switch_proxy()

    while proxy.__sizeof__() > 0:
        headers = {"User-Agent": next(user_agent)}
        proxies = next(proxy)
        client = Client(headers=headers, proxies=proxies)

        yield client
    print("Out of proxies")
    sys.exit()


client_generator = client_entity()


def get_connection(client: Client, url: str, response=None):
    """ verify connection """
    print("trying connection")

    try:
        response = client.get(url)
        print("Chance for connection")
    except (RemoteProtocolError,
            ConnectTimeout,
            ProxyError,
            ReadError,
            ReadTimeout,
            ConnectError):

        response = None

    except Exception as exception:
        print(f"Unregistered Exception: {exception.__class__.__name__}")
        response = None

    finally:
        return response


def get_main_page(client: Client, url) -> Response:
    """ get main page html """
    response = get_connection(client, url)

    while not response or response.status_code != 200:
        client = next(client_generator)
        response = get_connection(client, url)

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


def parse_met23():
    """ main logic for parser """

    client = next(client_generator)

    main_page = get_main_page(client, MAIN_URL)
    tree = MetalTreeNode("23.met.ru")
    # always need to check response status code
    # if problems with connection try change client
    if main_page.status == 200:

        print("succes with main page")
        main_categories = get_main_categories(main_page)
        # add our main categories to tree
        for category in main_categories:
            tree.add_child(MetalTreeNode(category))

    elif main_page.status == 429:
        print("Oops, you blocked!")

    else:

        print(main_page.status)

        # rotate proxy

    # first try to scrape one category
    time.sleep(1)

    main_categories = tree.get_children()
    # to get final links to tables
    # better to use headless browser
    print(main_categories)
    run_browser(main_categories)
        
    time.sleep(30)
        # for node in tree.get_children():
    #    print(node.get_value())
    # for node in tree.get_children():
    #     scrape_subcategories(client, node.href)


parse_met23()
