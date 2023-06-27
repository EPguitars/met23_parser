""" pylint: disable = W0622"""
import asyncio
from dataclasses import dataclass

import pickle
from httpx import AsyncClient

from table_scraper import write_to_csv


@dataclass
class MainCategory:
    """ contains usefull data for main categories """
    name: str
    href: str


@dataclass
class SubCategory:
    """ usesful data for sub-categories """
    main_category: str
    name: str
    size: str
    url: str
    status: str = None
    data: str = None
    proxy: str = None


proxies = []
urls = []
BATCH_SIZE = 200
cookie = "banners_top_current_id=mc24_992_P; banners_bottom_current_id=liskitrybprom_728_CH; _ga=GA1.2.812816011.1686859059; _gid=GA1.2.505918482.1686859059; _gat=1; _ym_uid=168685905982504539; _ym_d=1686859059; _ym_isad=2; mc_e_cn=msk%2Cspb%2Carhangelsk%2Castrahan%2Cbarnayl%2Cbelgorod%2Cbratsk%2Cbryansk%2Cvnovgorod%2Cvladivostok%2Cvladikavkaz%2Cvladimir%2Cvolgograd%2Cvologda%2Cvoronezh%2Cekb%2Civanovo%2Cizhevsk%2Cyoshkarola%2Cirkytsk%2Ckazan%2Ckalyga%2Ckemerovo%2Ckirov%2Ckrasnodar%2Ckrasnoyarsk%2Ckyrsk%2Clipetsk%2Cmagnitogorsk%2Cmahachkala%2Cminvody%2Cnabchelny%2Cnalchik%2Cnn%2Ctagil%2Cnovokyzneck%2Cnsk%2Cnovocherkassk%2Comsk%2Corel%2Corenbyrg%2Cpenza%2Cperm%2Cpyatigorsk%2Crostov%2Cryazan%2Csamara%2Csaransk%2Csaratov%2Csevastopol%2Csimferopol%2Csmolensk%2Csochi%2Cstavropol%2Csyrgyt%2Coskol%2Csyzran%2Ctaganrog%2Ctambov%2Ctver%2Ctolyatti%2Ctula%2Ctumen%2Cylianovsk%2Cylanyde%2Cufa%2Chabarovsk%2Ccheboksary%2Cchelyabinsk%2Ccherepovec%2Cchita%2Cusahalinsk%2Cyakytsk%2Cyaroslavl"
HEADER = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) " +
          "AppleWebKit/537.36 (KHTML, like Gecko) " +
          "Ubuntu Chromium/37.0.2062.94" +
          "Chrome/37.0.2062.94 Safari/537.36",
          "Cookie": cookie}


with open("root/proxies.txt", "r", encoding="utf=8") as file:
    for line in file:
        proxies.append(line.strip())
    print(f"I have {len(proxies)} proxies")

with open("urls.txt", "r", encoding="utf=8") as file:
    for line in file:
        urls.append(line.strip())

with open("tree.pkl", "rb") as file:
    result = pickle.load(file)

size = 0
for category in result.get_children():
    for subcategory in category.get_children():
        size += 1

print(size)


def next_node():
    for child in result.get_children():
        for node in child.get_children():
            yield node


next_link = next_node()


def proxy_generator() -> str:
    """ gives new proxy each time """
    counter = 0
    for _ in proxies:
        for proxy in proxies:
            counter += 1
            yield proxy


def url_generator() -> str:
    """ gives next url from list """
    for url in urls:
        yield url


# Generator objects for proxy and url
next_proxy = proxy_generator()
next_url = url_generator()


def get_new_batch(batch_len: int, data) -> list:
    """ batching urls list """
    batch = []
    for _ in range(batch_len):
        
        batch.append(next(data))

    return batch


async def make_request(data):
    """ trying to grab data with current proxy from url """

    current_proxy = f"http://{data.proxy}"
    proxies = {"http://": current_proxy, "https://": current_proxy}

    async with AsyncClient(headers=HEADER, proxies=proxies) as client:
        try:
            response = await client.get(data.url)

        # pylint: disable=W0612
        except Exception as exception:
            # print(f"Proxy unlucky attempt: {exception}")
            
            data.status = "lose"
            data.data = None
            
            return data
        if response.status_code == 200:
            data.status = "success"
            data.data = response
            
            return data
        else: 
            data.status = "lose"
            data.data = None
        
        return data


def update_batch(current_batch, response, data):
    current_proxy = response.proxy
    new_batch = [item for item in current_batch if item.url != response.url]
    new_element = get_new_batch(1, data)
    new_element[0].proxy = current_proxy
    new_element[0].data = "Null"
    new_batch.append(new_element[0])

    return new_batch


async def handle_urls(recieved_data, recieved_size: int):
    """ !!! """
    nodes = recieved_data
    size = recieved_size

    current_batch = None

    while size > 0:
        tasks = []

        if current_batch is None:
            current_batch = get_new_batch(BATCH_SIZE, nodes)

        for element in current_batch:
            if element.proxy is None:

                element.proxy = next(next_proxy)

            tasks.append(make_request(element))

        url_responses = await asyncio.gather(*tasks)

        success_counter = 0
        successful_responses = []

        for response in url_responses:

            if response.status == "success":
                size -= 1
                updated_batch = update_batch(
                    current_batch, response, nodes)
                current_batch = updated_batch
                print(f"Success with {response}")
                success_counter += 1
                successful_responses.append(response)
            else:
                for element in current_batch:
                    if response.proxy == element.proxy:
                        element.proxy = next(next_proxy)
                        break
        with open('test.pkl', 'wb') as file:
            pickle.dump(successful_responses, file)
        write_to_csv(successful_responses)

        print(f"Successes: {success_counter}")
        print(f"URLS left {size}")


async def parse_and_save():
    """ Extracting and saving data to csv """

    await handle_urls(next_link, size)

asyncio.run(parse_and_save())


# def next_node():
#         for child in result.get_children():
#             for node in result.get_children():
#                 yield node

# next_link = next_node()

# print(next_link.__sizeof__())
# async def scrape_n_save(next_link, size):
#     await handle_urls(next_link, size)

# asyncio.run(scrape_n_save(next_link, 100))
