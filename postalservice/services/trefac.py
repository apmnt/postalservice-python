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


class TrefacService(BaseService):

    @staticmethod
    async def fetch_data_async(params: dict) -> httpx.Response:
        item_count = params.get("item_count", 50)
        url = TrefacService.get_search_params(params)
        res = await fetch_async(url)
        return res

    @staticmethod
    def fetch_data(params: dict) -> httpx.Response:
        item_count = params.get("item_count", 50)
        url = TrefacService.get_search_params(params)
        res = httpx.get(url)
        return res

    @staticmethod
    async def parse_response_async(response: httpx.Response, **kwargs) -> str:
        soup = bs4.BeautifulSoup(response.text, "lxml")
        results = soup.select(".p-itemlist.is-col5 .p-itemlist_item")
        item_count = kwargs.get("item_count", 50)
        cleaned_items_list = TrefacService.get_base_details(results, item_count)
        cleaned_items_list_with_details = await TrefacService.add_details_async(
            cleaned_items_list
        )
        return json.dumps(cleaned_items_list_with_details)

    @staticmethod
    def parse_response(response: httpx.Response, **kwargs) -> str:
        soup = bs4.BeautifulSoup(response.text, "lxml")
        results = soup.select(".p-itemlist.is-col5 .p-itemlist_item")
        item_count = kwargs.get("item_count", 50)
        cleaned_items_list = TrefacService.get_base_details(results, item_count)
        cleaned_items_list_with_details = TrefacService.add_details(cleaned_items_list)
        return json.dumps(cleaned_items_list_with_details)

    @staticmethod
    def get_base_details(results, item_count) -> list:
        cleaned_items_list = []
        for item in results[:item_count]:
            temp = {}

            # Get URL from the main link
            link_element = item.select_one("a.p-itemlist_btn")
            if link_element:
                temp["url"] = link_element["href"]
                # Extract ID from URL (last part before the trailing slash)
                url_parts = temp["url"].rstrip("/").split("/")
                temp["id"] = url_parts[-1] if url_parts else "no-id"
            else:
                continue  # Skip if no link found

            # Get title placeholder (will be replaced with detailed title from item page)
            temp["title"] = "TITLE_PLACEHOLDER"

            # Get price from the price element
            price_element = item.select_one(".p-price2_a")
            if price_element:
                price_text = price_element.get_text()
                # Extract numeric value from price (remove ￥, 税込, etc.)
                price_match = re.search(r"￥?([0-9,]+)", price_text)
                if price_match:
                    price_string = price_match.group(1).replace(",", "")
                    temp["price"] = float(price_string)
                else:
                    temp["price"] = 0.0
            else:
                temp["price"] = 0.0

            # Get image URL
            img_element = item.select_one(".p-itemlist_img img")
            if img_element:
                img_src = img_element.get("src")
                if img_src:
                    temp["img"] = [img_src]
                else:
                    temp["img"] = ["IMAGE_PLACEHOLDER"]
            else:
                temp["img"] = ["IMAGE_PLACEHOLDER"]

            # Get size from the size element
            size_element = item.select_one(".p-itemlist_size")
            if size_element:
                size_text = size_element.get_text()
                # Extract size from text like "サイズ：S"
                size_match = re.search(r"サイズ[:：]\s*([A-Z0-9]+)", size_text)
                if size_match:
                    temp["size"] = size_match.group(1)
                else:
                    temp["size"] = "no size"
            else:
                temp["size"] = "no size"

            # Get brand from the brand element
            brand_element = item.select_one(".p-itemlist_brand")
            if brand_element:
                temp["brand"] = brand_element.get_text().strip()
            else:
                temp["brand"] = "no brand"

            cleaned_items_list.append(temp)
        return cleaned_items_list

    @staticmethod
    async def add_details_async(items: list) -> list:
        tasks = []
        for item in items:
            url = item["url"]
            task = asyncio.create_task(TrefacService.fetch_item_page_async(url))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        item_details = [response.text for response in responses]

        for i, details in enumerate(item_details):
            items[i] = {**items[i], **TrefacService.parse_item_details(details)}

        return items

    @staticmethod
    def add_details(items: list) -> list:
        for i, item in enumerate(items):
            url = item["url"]
            response = TrefacService.fetch_item_page(url)
            details = TrefacService.parse_item_details(response.text)
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

        # Extract title from the brand field instead of gdname
        brand_element = soup.select_one(".gdbrand")
        if brand_element:
            # Get the text content and clean it up
            brand_text = brand_element.get_text().strip()
            # Remove the "ブランド：" prefix if present
            if brand_text.startswith("ブランド："):
                brand_text = brand_text[4:].strip()
            # Remove "：" characters and newline characters
            brand_text = (
                brand_text.replace("：", "").replace("\n", "").replace("\r", "")
            )
            # Remove extra whitespace - replace multiple spaces with single space
            brand_text = re.sub(r"\s+", " ", brand_text).strip()
            details["title"] = brand_text
        else:
            # Keep existing title if no brand found on item page
            details["title"] = None

        # Extract images from the thumbnail gallery
        images = []

        # Get images from the thumbnail list
        thumb_images = soup.select(".gdimage_thumb_list_item img")
        for img in thumb_images:
            img_src = img.get("src")
            if img_src:
                # Convert thumbnail URLs to higher resolution
                # Replace w72 with w500 for better quality
                if "/w72/" in img_src:
                    img_src = img_src.replace("/w72/", "/w500/")
                images.append(img_src)

        # If no thumbnail images, try to get from main image
        if not images:
            main_img = soup.select_one(".gdimage_img")
            if main_img:
                img_src = main_img.get("src")
                if img_src:
                    images.append(img_src)

        # Remove duplicates while preserving order
        seen = set()
        unique_images = []
        for img in images:
            if img not in seen:
                seen.add(img)
                unique_images.append(img)

        # Only update images if we found some, otherwise keep the search result image
        if unique_images:
            details["img"] = unique_images

        # Size information is already extracted from search results
        # But we can get more detailed size info if needed
        size_element = soup.select_one(".gdsize")
        if size_element:
            size_text = size_element.get_text()
            # Extract size from text like "タグ表記サイズ：S（ 参考サイズ：S ）"
            size_match = re.search(r"タグ表記サイズ[:：]\s*([A-Z0-9]+)", size_text)
            if size_match:
                details["size"] = size_match.group(1)

        return details

    @staticmethod
    def get_search_params(params: dict) -> str:
        base_url = "https://www.trefac.jp/store/tcpsb/"

        # Start with base parameters
        url_params = []

        if "keyword" in params and params["keyword"]:
            keyword = params["keyword"]
            url_params.append(f"srchword={keyword}")

        # Add required parameters
        url_params.append("step=1")
        url_params.append("disp_num=90")
        url_params.append("order=new")

        # Add page parameter if specified
        page = params.get("page")
        if page is not None:
            # Trefac might use different pagination - adjust as needed
            url_params.append(f"page={page}")

        # Construct final URL
        if url_params:
            url = base_url + "?" + "&".join(url_params)
        else:
            url = base_url

        return url
