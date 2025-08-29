import json
import httpx
import bs4
from .baseservice import BaseService
from ..utils.network_utils import fetch_async
import re
import asyncio


BRAND_MAP = {}

SIZE_MAP = {}

CATEGORY_MAP = {}


class RagtagService(BaseService):

    @staticmethod
    async def fetch_data_async(params: dict) -> httpx.Response:
        url = RagtagService.get_search_url(params)
        res = await fetch_async(url)
        return res

    @staticmethod
    def fetch_data(params: dict) -> httpx.Response:
        url = RagtagService.get_search_url(params)
        res = httpx.get(url)
        return res

    @staticmethod
    async def parse_response_async(response: httpx.Response, **kwargs) -> str:
        soup = bs4.BeautifulSoup(response.text, "lxml")
        results = soup.select(".search-result__item")
        item_count = kwargs.get("item_count", 36)
        cleaned_items_list = RagtagService.get_base_details(results, item_count)
        cleaned_items_list_with_details = await RagtagService.add_details_async(
            cleaned_items_list
        )
        return json.dumps(cleaned_items_list_with_details)

    @staticmethod
    def parse_response(response: httpx.Response, **kwargs) -> str:
        soup = bs4.BeautifulSoup(response.text, "lxml")
        results = soup.select(".search-result__item")
        item_count = kwargs.get("item_count", 36)
        cleaned_items_list = RagtagService.get_base_details(results, item_count)
        cleaned_items_list_with_details = RagtagService.add_details(cleaned_items_list)
        return json.dumps(cleaned_items_list_with_details)

    @staticmethod
    def get_base_details(results, item_count) -> list:
        cleaned_items_list = []
        for item in results[:item_count]:
            try:
                # Extract item ID from data-bic attribute
                item_id = item.get("data-bic", "")

                # Extract link and title
                link_element = item.select_one(".search-result__item-link")
                if not link_element:
                    continue

                url = link_element.get("href", "")
                if url and not url.startswith("http"):
                    url = "https://www.ragtag.jp" + url

                # Extract title from image alt text
                img_element = item.select_one(".search-result__item-photo-img")
                title = img_element.get("alt", "") if img_element else ""

                # Extract brand
                brand_element = item.select_one(".search-result__name-brand")
                brand = brand_element.get_text(strip=True) if brand_element else ""

                # Extract size
                size_element = item.select_one(".search-result__name-size")
                size = ""
                if size_element:
                    size_text = size_element.get_text(strip=True)
                    # Extract size from "Size: S" format
                    size_match = re.search(r"Size:\s*(\S+)", size_text)
                    size = size_match.group(1) if size_match else ""

                # Extract price
                price_element = item.select_one(".search-result__price-proper")
                price = 0.0
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    # Extract price from "11,200 yen" format
                    price_match = re.search(r"([\d,]+)", price_text)
                    if price_match:
                        price_str = price_match.group(1).replace(",", "")
                        price = float(price_str)

                # Extract image
                img_url = ""
                if img_element:
                    img_url = img_element.get("src", "")
                    if img_url and not img_url.startswith("http"):
                        img_url = "https://www.ragtag.jp" + img_url

                temp = {
                    "id": item_id,
                    "title": title,
                    "price": price,
                    "size": size,
                    "brand": brand,
                    "url": url,
                    "img": [img_url] if img_url else [],
                }

                cleaned_items_list.append(temp)

            except Exception as e:
                # Skip items that fail to parse
                print(f"Error parsing item: {e}")
                continue

        return cleaned_items_list

    @staticmethod
    async def add_details_async(items: list) -> list:
        tasks = []
        for item in items:
            url = item["url"]
            task = asyncio.create_task(RagtagService.fetch_item_page_async(url))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        item_details = [response.text for response in responses]

        for i, details in enumerate(item_details):
            items[i] = {**items[i], **RagtagService.parse_item_details(details)}

        return items

    @staticmethod
    def add_details(items: list) -> list:
        for i, item in enumerate(items):
            url = item["url"]
            response = RagtagService.fetch_item_page(url)
            details = RagtagService.parse_item_details(response.text)
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

        # Extract images from the item detail photo section
        images = []

        # Try to find images in the item detail photo section
        photo_elements = soup.select(".item-detail-pic__photo-default img")
        for img in photo_elements:
            img_src = img.get("src", "")
            if img_src:
                # Convert relative URLs to absolute
                if not img_src.startswith("http"):
                    img_src = "https://www.ragtag.jp" + img_src
                images.append(img_src)

        # If no images found, try thumbnail images
        if not images:
            thumb_elements = soup.select(".item-detail-photo__photo-thumbs img")
            for img in thumb_elements:
                img_src = img.get("src", "")
                if img_src:
                    # Convert relative URLs to absolute
                    if not img_src.startswith("http"):
                        img_src = "https://www.ragtag.jp" + img_src
                    images.append(img_src)

        if images:
            details["img"] = images

        # Extract detailed brand information from brand link
        brand_link = soup.select_one(".item-detail-info__name-brand a span")
        if brand_link:
            details["brand"] = brand_link.get_text(strip=True)

        # Extract size from the detailed size information
        size_span = soup.select_one(".item-detail-info__name-size span")
        if size_span:
            details["size"] = size_span.get_text(strip=True)

        return details

    @staticmethod
    def get_search_url(params: dict) -> str:
        base_url = "https://www.ragtag.jp/search"

        # Build query parameters
        query_params = []

        # For the example URL format: https://www.ragtag.jp/search?&fr=junya&so=NEW
        if "keyword" in params and params["keyword"]:
            query_params.append(f"fr={params['keyword']}")

        # Add sort order (NEW for newest)
        query_params.append("so=NEW")

        if query_params:
            return base_url + "?" + "&".join(query_params)
        else:
            return base_url
