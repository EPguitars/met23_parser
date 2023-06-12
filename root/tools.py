# pylint: disable = W0718
""" module contains proxy and header generators """
import time

from rich import print
from httpx import Client
from httpx._exceptions import (RemoteProtocolError,
                               ConnectTimeout,
                               ProxyError,
                               ReadError,
                               ReadTimeout,
                               ConnectError)

UA_PATH = 'root/user-agents-list.txt'
PROXIES_PATH = 'root/proxies.txt'
TESTING_HEADER = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) " +
                                "AppleWebKit/537.36 (KHTML, like Gecko) " +
                                "Ubuntu Chromium/37.0.2062.94" +
                                "Chrome/37.0.2062.94 Safari/537.36"}


def good_proxy(proxy_attempt: str):
    """ checks connection with current proxy """
    url = "https://multicity.23met.ru/"
    current_proxy = f"http://{proxy_attempt}"
    proxies = {"http://": current_proxy, "https://": current_proxy}
    test_client = Client(proxies=proxies,
                         headers=TESTING_HEADER)

    try:
        test_response = test_client.get(url)

    except RemoteProtocolError:
        return False
    except ConnectTimeout:
        return False
    except ProxyError:
        return False
    except ReadError:
        return False
    except ReadTimeout:
        return False
    except ConnectError:
        return False
    # Need this block to catch and register unexpected exceptions
    except Exception as exception:
        print(f"Unregistered Exception: {exception.__class__.__name__}")
        return False

    if test_response.status_code == 200:
        return True
    else:
        return False


def switch_proxy() -> str:
    """ returns working proxy """
    with open(PROXIES_PATH, 'r', encoding='utf-8') as file:
        counter = 1
        for line in file:
            print(f"proxies {counter} of {300}")
            counter += 1
            proxy = line.strip()

            if good_proxy(proxy):
                print(f"Proxy found: {proxy}")
                time.sleep(2)
                yield {"http://": f"http://{proxy}", "https://": f"http://{proxy}"}
            else:
                continue


def switch_user_agent() -> str:
    """ returns new user-agent from file """
    with open(UA_PATH, 'r', encoding='utf-8') as file:
        for line in file:
            yield line.strip()
