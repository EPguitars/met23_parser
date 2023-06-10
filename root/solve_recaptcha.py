
from selectolax.parser import HTMLParser


def solve(client, captcha, HEADERS):
    ask_reload = client.post(
        f"https://www.google.com/recaptcha/api2/reload?k={captcha}", headers=HEADERS)
    ask_userverify = client.post(
        f"https://www.google.com/recaptcha/api2/userverify?k={captcha}", headers=HEADERS)

    


def get_captcha(response):
    """ extract data-sitekey, e need it to solve captcha """
    captcha = response.css_first("div#recaptcha-el").attrs["data-sitekey"]
    return captcha
