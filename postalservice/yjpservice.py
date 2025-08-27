import asyncio
import json
import random
import re
import string
import bs4
import httpx
from .baseservice import BaseService
from .utils.network_utils import fetch_async

CHARACTERS = string.ascii_lowercase + string.digits

SIZE_MAP = {
    "XS": "spec_id=100100%3A110001%2C100001%3A100101",
    "S": "spec_id=100100%3A110001%2C100001%3A100102",
    "M": "spec_id=100100%3A110001%2C100001%3A100103",
    "L": "spec_id=100100%3A110001%2C100001%3A100104",
    "XL": "spec_id=100100%3A110001%2C100001%3A100105",
    "XXL": "spec_id=100100%3A110001%2C100001%3A100106",
    "FREE / ONESIZE": "100100%3A110001%2C100001%3A100109",
}

BRANDS_MAP = {
    "JUNYA WATANABE": "1623",
    "JUNYA WATANABE MAN": "15429",
    "BLACK COMME des GARCONS": "1624",
    "COMME des GARCONS HOMME": "7319",
    "COMME des GARCONS HOMME DEUX": "7320",
    "COMME des GARCONS SHIRT": "7321",
    "JUNYA WATANABE COMME des GARCONS": "7389",
    "tricot COMME des GARCONS": "7529",
    "COMME des GARCONS HOMME HOMME": "7812",
    "KAPITAL": "1527",
    "nanamica": "6185",
    "noir kei ninomiya": "16960",
    "goa": "542",
    "FULLCOUNT": "5602",
    "WHITESVILLE": "8689",
    "WAREHOUSE": "281",
    "takahiro miyashita the soloist": "14631",
}

CATEGORIES_MAP = {
    "tops": "30",
    "outerwear": "31",
    "pants": "32",
    "shoes": "33",
    "bags": "34",
    "hats": "36",
    "accessories": "38",
    "jewelry": "37",
}


class YJPService(BaseService):

    @staticmethod
    async def fetch_data_async(params: dict) -> httpx.Response:
        item_count = params.get("item_count", 50)
        url = YJPService.get_search_params(params)
        res = await fetch_async(url)
        return res

    @staticmethod
    def fetch_data(params: dict) -> httpx.Response:
        item_count = params.get("item_count", 50)
        url = YJPService.get_search_params(params)
        res = httpx.get(url)
        return res

    @staticmethod
    async def parse_response_async(response: httpx.Response, **kwargs) -> str:
        soup = bs4.BeautifulSoup(response.text, "lxml")
        results = soup.select(".Product")
        item_count = kwargs.get("item_count", 50)
        cleaned_items_list = YJPService.get_base_details(results, item_count)
        cleaned_items_list_with_details = await YJPService.add_details_async(
            cleaned_items_list
        )
        return json.dumps(cleaned_items_list_with_details)

    @staticmethod
    def parse_response(response: httpx.Response, **kwargs) -> str:
        soup = bs4.BeautifulSoup(response.text, "lxml")
        results = soup.select(".Product")
        item_count = kwargs.get("item_count", 50)
        cleaned_items_list = YJPService.get_base_details(results, item_count)
        cleaned_items_list_with_details = YJPService.add_details(cleaned_items_list)
        return json.dumps(cleaned_items_list_with_details)

    @staticmethod
    def get_base_details(results, item_count) -> list:
        cleaned_items_list = []
        for item in results[:item_count]:
            temp = {}
            temp["url"] = item.select_one(".Product__image a")["href"]
            temp["id"] = temp["url"].split("/")[-1]
            temp["title"] = item.select_one(".Product__title").text
            price_string = item.select_one(".Product__price").text
            temp["price"] = float(re.sub(r"[^\d.]", "", price_string))
            temp["img"] = ["IMAGE_PLACEHOLDER"]
            temp["size"] = "no size"
            temp["brand"] = "BRAND_PLACEHOLDER"
            cleaned_items_list.append(temp)
        return cleaned_items_list

    @staticmethod
    async def add_details_async(items: list) -> list:
        tasks = []
        for item in items:
            url = item["url"]
            task = asyncio.create_task(YJPService.fetch_item_page_async(url))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        item_details = [response.text for response in responses]

        for i, details in enumerate(item_details):
            items[i] = {**items[i], **YJPService.parse_item_details(details)}

        return items

    @staticmethod
    def add_details(items: list) -> list:
        for i, item in enumerate(items):
            url = item["url"]
            response = YJPService.fetch_item_page(url)
            details = YJPService.parse_item_details(response.text)
            items[i] = {**items[i], **details}
        return items

    @staticmethod
    async def fetch_item_page_async(url):
        response = await fetch_async(url)
        return response

    @staticmethod
    def fetch_item_page(url):
        response = httpx.get(url)
        return response

    @staticmethod
    def parse_item_details(response_text: str):
        soup = bs4.BeautifulSoup(response_text, "lxml")
        details = {}
        tr_rows = soup.find_all("tr")
        if len(tr_rows) > 1:
            for tr in tr_rows:
                if tr.text.replace("\n", "").replace(" ", "").startswith("サイズ"):
                    details["size"] = tr.td.text.replace("\n", "").replace(" ", "")
                    break
            for tr in tr_rows:
                if (
                    tr.text.replace("\n", "")
                    .replace(" ", "")
                    .startswith("メーカー・ブランド")
                ):
                    details["brand"] = tr.td.text.replace("\n", "").replace(" ", "")
                    break

        # First try to find images in the slick-track carousel structure
        slick_track = soup.select_one(".slick-track")
        if slick_track:
            images = []
            # Get all images from the slick-track, avoiding duplicates
            seen_urls = set()
            for img in slick_track.select("img"):
                img_url = img.get("src")
                if img_url and img_url not in seen_urls:
                    images.append(img_url)
                    seen_urls.add(img_url)
            if images:
                details["img"] = images
        # If no slick-track or no images found, try another method
        else:
            images = soup.select(".ProductImage__images img")
            if len(images) > 0:
                details["img"] = [img["src"] for img in images]

        return details

    @staticmethod
    def get_search_params(params: dict) -> str:

        url = "https://auctions.yahoo.co.jp/search/search?&fixed=1&s1=new&n=50"

        if "keyword" in params and params["keyword"] != "":
            keyword = params["keyword"].replace(" ", "%20")
            url += f"&p={keyword}"
        else:
            url += "&p=sacai"

        size = params.get("size")
        if "size" in params and size is not None:
            if size not in SIZE_MAP:
                raise ValueError(f"Size {size} is not supported")
            size_id = SIZE_MAP[size]
            url += f"&{size_id}"

        page = params.get("page")
        if "page" in params and page is not None:
            url += f"&b={page*50+1}"

        brands = params.get("brand")
        if "brand" in params and brands is not None and len(brands) > 0:
            if brands[0] not in BRANDS_MAP:
                raise ValueError(f"Brand {brands[0]} is not supported")
            brand_id = BRANDS_MAP[brands[0]]
            url += f"&brand_id={brand_id}"

        categories = params.get("category")
        if "category" in params and categories is not None and len(categories) > 0:
            if categories[0] not in CATEGORIES_MAP:
                raise ValueError(f"Category {categories[0]} is not supported")
            category_id = CATEGORIES_MAP[categories[0]]
            url += f"&category_id={category_id}"

        return url
