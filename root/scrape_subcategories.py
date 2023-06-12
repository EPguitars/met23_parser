import time

from playwright.sync_api import sync_playwright
from selectolax.parser import HTMLParser
from rich import print

URL = "https://multicity.23met.ru/price"


def scrape_all_links(url):
    """ function for scraping all product links """
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)

        page = browser.new_page()
        page.goto(url)
        page.wait_for_url(url)
        page.click("input#regionchooser-0")
        page.click("input[onclick='citychooser_save_cities_list_for_user()']")
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

        for category in subcategories:
            page.get_by_role("link", name=category.text(), exact=True).click()
            sizes_block = HTMLParser(page.inner_html("body"))
            
            sizes = sizes_block.css("nav#center_container > " +
                                    "div > " +
                                    "div > " +
                                    "a")
            print("Hello")
            print(sizes)
            print(type(sizes))
            for size in sizes:
                print(size)
                print(type(size))
                print(size.text())
                print(size.attrs["href"])


        time.sleep(100)


scrape_all_links(URL)
