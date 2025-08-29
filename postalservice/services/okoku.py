import asyncio
import json
import random
import re
import string
import bs4
import httpx
from .baseservice import BaseService
from ..utils.network_utils import fetch_async

CHARACTERS = string.ascii_lowercase + string.digits


class OkokuService(BaseService):

    @staticmethod
    async def fetch_data_async(params: dict) -> httpx.Response:
        item_count = params.get("item_count", 50)
        url = OkokuService.get_search_params(params)
        res = await fetch_async(url)
        return res

    @staticmethod
    def fetch_data(params: dict) -> httpx.Response:
        item_count = params.get("item_count", 50)
        url = OkokuService.get_search_params(params)
        res = httpx.get(url)
        return res

    @staticmethod
    async def parse_response_async(response: httpx.Response, **kwargs) -> str:
        soup = bs4.BeautifulSoup(response.text, "lxml")
        results = soup.select(".list_item.list_large .item")
        item_count = kwargs.get("item_count", 50)
        cleaned_items_list = OkokuService.get_base_details(results, item_count)
        cleaned_items_list_with_details = await OkokuService.add_details_async(
            cleaned_items_list
        )
        return json.dumps(cleaned_items_list_with_details)

    @staticmethod
    def parse_response(response: httpx.Response, **kwargs) -> str:
        soup = bs4.BeautifulSoup(response.text, "lxml")
        results = soup.select(".list_item.list_large .item")
        item_count = kwargs.get("item_count", 50)
        cleaned_items_list = OkokuService.get_base_details(results, item_count)
        cleaned_items_list_with_details = OkokuService.add_details(cleaned_items_list)
        return json.dumps(cleaned_items_list_with_details)

    @staticmethod
    def get_base_details(results, item_count) -> list:
        cleaned_items_list = []
        for item in results[:item_count]:
            temp = {}

            # Get URL from the product link
            link_element = item.select_one("a#productLink")
            if link_element:
                temp["url"] = "https://www.okoku.jp" + link_element["href"]
                temp["id"] = link_element["href"].split("/")[-1].split("?")[0]
            else:
                continue  # Skip if no link found

            # Get title from the name paragraph (placeholder - will be replaced with detailed title)
            name_element = item.select_one("p.name a")
            if name_element:
                temp["title"] = (
                    "TITLE_PLACEHOLDER"  # Will be replaced with detailed title from item page
                )
            else:
                temp["title"] = "TITLE_PLACEHOLDER"

            # Get price from the price paragraph
            price_element = item.select_one("p.price strong")
            if price_element:
                price_string = price_element.text.strip()
                # Extract numeric value from price
                temp["price"] = float(re.sub(r"[^\d.]", "", price_string))
            else:
                temp["price"] = 0.0

            # Get image URL
            img_element = item.select_one(".image img")
            if img_element:
                img_src = img_element.get("src") or img_element.get("data-original")
                if img_src:
                    temp["img"] = [
                        (
                            "https://www.okoku.jp" + img_src
                            if img_src.startswith("/")
                            else img_src
                        )
                    ]
                else:
                    temp["img"] = ["IMAGE_PLACEHOLDER"]
            else:
                temp["img"] = ["IMAGE_PLACEHOLDER"]

            # Placeholder values that will be filled in by add_details
            temp["size"] = "SIZE_PLACEHOLDER"
            temp["brand"] = "BRAND_PLACEHOLDER"

            cleaned_items_list.append(temp)
        return cleaned_items_list

    @staticmethod
    async def add_details_async(items: list) -> list:
        tasks = []
        for item in items:
            url = item["url"]
            task = asyncio.create_task(OkokuService.fetch_item_page_async(url))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        item_details = [response.text for response in responses]

        for i, details in enumerate(item_details):
            items[i] = {**items[i], **OkokuService.parse_item_details(details)}

        return items

    @staticmethod
    def add_details(items: list) -> list:
        for i, item in enumerate(items):
            url = item["url"]
            response = OkokuService.fetch_item_page(url)
            details = OkokuService.parse_item_details(response.text)
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

        # Extract title from the item page
        title_element = soup.select_one("h1.headline")
        if title_element:
            details["title"] = title_element.get_text().strip()
        else:
            details["title"] = "no title"

        # Extract size from the detail text
        detail_text_element = soup.select_one("#detail .text")
        if detail_text_element:
            detail_text = detail_text_element.get_text()
            # Look for size pattern  like "■サイズ表記：S"
            size_match = re.search(
                r"■サイズ表記[:：]\s*([A-Z0-9]+)(?=\s|<|$|※|■)", detail_text
            )
            if size_match:
                details["size"] = size_match.group(1).strip()
            else:
                details["size"] = "no size"
        else:
            details["size"] = "no size"

        # Extract brand from title - get the first recognizable brand from title
        title_element = soup.select_one("h1.headline")
        if title_element:
            title = title_element.get_text().strip()
            # Common brands found in Okoku
            known_brands = [
                "JUNYA WATANABE COMME des GARÇONS",
                "JUNYA WATANABE",
                "COMME des GARÇONS",
                "KAPITAL",
                "nanamica",
                "noir kei ninomiya",
                "FULLCOUNT",
                "WHITESVILLE",
                "WAREHOUSE",
            ]

            brand_found = None
            for brand in known_brands:
                if brand.upper() in title.upper():
                    brand_found = brand
                    break

            details["brand"] = brand_found if brand_found else "no brand"
        else:
            details["brand"] = "no brand"

        # Extract images from the product image carousel
        images = []

        # Get images from the bxslider carousel
        carousel_images = soup.select(".bxslider li img")
        for img in carousel_images:
            img_src = img.get("src")
            if img_src and not img_src.endswith("noimage_m.jpg"):
                # Make sure it's a full URL
                if img_src.startswith("/"):
                    img_src = "https://www.okoku.jp" + img_src
                images.append(img_src)

        # If no carousel images, try to get from image pager
        if not images:
            pager_images = soup.select("#image_pager img")
            for img in pager_images:
                img_src = img.get("src")
                if img_src and not img_src.endswith("noimage_m.jpg"):
                    # Make sure it's a full URL
                    if img_src.startswith("/"):
                        img_src = "https://www.okoku.jp" + img_src
                    images.append(img_src)

        # Remove duplicates while preserving order
        seen = set()
        unique_images = []
        for img in images:
            if img not in seen:
                seen.add(img)
                unique_images.append(img)

        details["img"] = unique_images if unique_images else ["IMAGE_PLACEHOLDER"]

        return details

    @staticmethod
    def get_search_params(params: dict) -> str:
        base_url = "https://www.okoku.jp/ec/Facet"

        # Start with base parameters
        url_params = []

        if "keyword" in params and params["keyword"]:
            keyword = params["keyword"]
            url_params.append(f"inputKeywordFacet={keyword}")
            url_params.append("kclsf=AND")

        # Add page parameter if specified
        page = params.get("page")
        if page is not None:
            # Okoku might use different pagination - adjust as needed
            url_params.append(f"page={page}")

        # Construct final URL
        if url_params:
            url = base_url + "?" + "&".join(url_params)
        else:
            url = base_url

        return url
