import time

from playwright.sync_api import sync_playwright, Page
import requests

from tools import switch_proxy

new_proxy = switch_proxy()

with sync_playwright() as playwright:

    def get_new_page() -> Page:
        url = "https://multicity.23met.ru/"
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()

        return page, browser

    def go():
        url = "https://multicity.23met.ru/"
        page, browser = get_new_page()
        page = browser.new_page()
        response = page.goto(url)

        time.sleep(2)
        browser.close()

    for _ in range(4):
        go()
