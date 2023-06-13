""" 
this module uses automatic browser
to extract final urls for each table  
"""
#import time
import re
import time
from dataclasses import dataclass

from playwright.sync_api import sync_playwright, Page
from selectolax.parser import HTMLParser
from rich import print

import logger
from tools import switch_proxy

@dataclass
class SubCategory:
    """ usesful data for sub-categories """
    main_category: str
    name: str
    size: str
    url: str


def extract_data_naimenovanie(url: str) -> str:
    """ extracts str after last slash """
    pattern = r"/([^/]+)$"
    result = re.search(pattern, url)

    if result:
        last_word = result.group(1)
        return last_word
    else: 
        logger.logger.warning(" some shit happens")
    return None


def scrape_all_links(current_category_node, page: Page):
    """ function for scraping all product links """
    # first grab url from current node
    url = current_category_node.get_value().href
    main_category_name = current_category_node.get_value().name
    # then move to current category url
    page.goto(url)
    page.wait_for_url(url)
    # select all regions to get full list of items
    page.click("input#regionchooser-0")
    page.click("input[onclick='citychooser_save_cities_list_for_user()']")
    # get html markup of the page
    html = HTMLParser(page.inner_html("body"))
    print(html)

    span_buttons = html.css(
        "nav#left-container > ul[class='tabs '] > li > span")

    subcategories = html.css(
        "nav#left-container > ul[class='tabs '] > li > a")

    for span in span_buttons:
        span_class = span.attrs["class"]
        span_text = span.text()
        # click on each span to locate hidden elements
        page.locator(f"span.{span_class}",
                        has_text=span_text).click()

    # get sizes for each category
    for category in subcategories:
        page.get_by_role("link", name=category.text(), exact=True).click()
        # need data_naimenovanie to show exact location of div
        data_naimenovanie = extract_data_naimenovanie(category.attrs["href"])
        sizes_location = "nav[id='center-container'] > " + \
            "div > " + \
            f"div[data-naimenovanie='{data_naimenovanie}']"
            
        page.wait_for_selector(sizes_location)
        sizes_expected_block = HTMLParser(page.inner_html("body"))

        sizes = sizes_expected_block.css(sizes_location)[-1].css("a")

        for size in sizes:
            new_node = SubCategory(
                main_category=main_category_name,
                name=category.text(),
                size=size.text(),
                url=size.attrs["href"]
            )
            print(new_node)
            current_category_node.add_child(new_node)


    
def run_browser(main_categories):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        for main_category in main_categories:
            
            scrape_all_links(main_category, page)

