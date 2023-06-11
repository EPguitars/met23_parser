import requests
from rich import print
from httpx import Client

from tools import switch_header

header = switch_header()
headers = {"User-Agent" : next(header)}
print(header.__sizeof__())

#client = Client(headers=headers)

#r = client.get("https://httpbin.org/")

