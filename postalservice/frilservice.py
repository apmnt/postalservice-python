import json
import random
import string
import httpx
import bs4
from .baseservice import BaseService
from .utils.search_utils import SearchParams
from .utils.network_utils import fetch_async
import re
import asyncio


CHARACTERS = string.ascii_lowercase + string.digits

SIZE_MAP = {
    "FREE / ONESIZE": 19998,
    "XS": 10001,
    "S": 10003,
    "M": 10004,
    "L": 10005,
    "XL": 10008,
    "XXL": 10009,
}

BRANDS_MAP = {
    "JUNYA WATANABE": "4433",
    "JUNYA WATANABE MAN": "12400",
    "BLACK COMME des GARCONS": "5454",
    "COMME des GARCONS HOMME": "16922",
    "COMME des GARCONS HOMME DEUX": "16918",
    "COMME des GARCONS SHIRT": "16920",
    "JUNYA WATANABE COMME des GARCONS": "5420",
    "tricot COMME des GARCONS": "16921",
    "KAPITAL": "1785",
    "nanamica": "3393",
    "noir kei ninomiya": "12388",
    "goa": "321",
    "FULLCOUNT": "2651",
    "WHITESVILLE": "9493",
    "WAREHOUSE": "4290",
    "takahiro miyashita the soloist": "8964",
}


class FrilService(BaseService):

    async def fetch_data_async(self, params: dict) -> httpx.Response:
        self.item_count = params.get("item_count", 36)
        url = self.get_search_params(params)
        res = await fetch_async(url)
        return res

    def fetch_data(self, params: dict) -> httpx.Response:
        self.item_count = params.get("item_count", 36)
        url = self.get_search_params(params)
        res = httpx.get(url)
        return res

    async def parse_response_async(self, response: httpx.Response) -> str:
        soup = bs4.BeautifulSoup(response.text, "lxml")
        results = soup.select(".item")
        cleaned_items_list = self.get_base_details(results)
        cleaned_items_list_with_details = await self.add_details_async(
            cleaned_items_list
        )
        return json.dumps(cleaned_items_list_with_details)

    def parse_response(self, response: httpx.Response) -> str:
        soup = bs4.BeautifulSoup(response.text, "lxml")
        results = soup.select(".item")
        cleaned_items_list = self.get_base_details(results)
        cleaned_items_list_with_details = self.add_details(cleaned_items_list)
        return json.dumps(cleaned_items_list_with_details)

    def get_base_details(self, results) -> list:
        cleaned_items_list = []
        for item in results[: self.item_count]:
            id = item.select_one(".link_search_image")["href"].split("/")[-1]
            temp = {}
            temp["id"] = id
            temp["title"] = item.select_one(".link_search_image")["title"]
            price_string = item.select_one(".item-box__item-price").text
            temp["price"] = float(re.sub(r"\D", "", price_string))
            temp["url"] = item.select_one(".link_search_image")["href"]
            temp["img"] = ["IMG PLACEHOLDER"]
            temp["size"] = "SIZE PLACEHOLDER"
            temp["brand"] = "BRAND PLACEHOLDER"
            cleaned_items_list.append(temp)
        return cleaned_items_list

    async def add_details_async(self, items: list) -> list:
        tasks = []
        for item in items:
            url = item["url"]
            task = asyncio.create_task(self.fetch_item_page_async(url))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        item_details = [response.text for response in responses]

        for i, details in enumerate(item_details):
            items[i] = {**items[i], **self.parse_item_details(details)}

        return items

    def add_details(self, items: list) -> list:
        for i, item in enumerate(items):
            url = item["url"]
            response = self.fetch_item_page(url)
            details = self.parse_item_details(response.text)
            items[i] = {**items[i], **details}
        return items

    async def fetch_item_page_async(self, url):
        response = await fetch_async(url)
        return response

    def fetch_item_page(self, url):
        response = httpx.get(url)
        return response

    def parse_item_details(self, response_text: str):
        soup = bs4.BeautifulSoup(response_text, "lxml")
        details = {}
        tr_rows = soup.find_all("tr")
        if len(tr_rows) > 1:
            details["size"] = tr_rows[1].td.text
            details["brand"] = tr_rows[2].td.text.replace("\n", "")

        sp_slides = soup.find_all("div", class_="sp-slide")
        if len(sp_slides) > 0:
            details["img"] = [sp_slides[0].img["src"]]
        return details

    def get_search_params(self, params: dict) -> str:

        base_url = "https://fril.jp/s?"

        if "keyword" in params:
            url = (
                base_url
                + f"query={params['keyword']}&order=desc&sort=created_at&transaction=selling"
            )

        size = params.get("size")
        if "size" in params and size is not None:
            if size not in SIZE_MAP:
                raise ValueError(f"Size {size} is not supported")
            size_id = SIZE_MAP[size]
            url += f"&size_group_id=3&size_id={size_id}"

        page = params.get("page")
        if "page" in params and page is not None:
            url += f"&page={page}"

        brands = params.get("brand")
        if "brand" in params and brands is not None and len(brands) > 0:
            if brands[0] not in BRANDS_MAP:
                raise ValueError(f"Brand {brands[0]} is not supported")
            brand_id = BRANDS_MAP[brands[0]]
            url += f"&brand_id={brand_id}"

        return url
