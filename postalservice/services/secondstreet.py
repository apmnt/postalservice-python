import asyncio
import json
import random
import re
import string
import bs4
import httpx
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from .baseservice import BaseService
from ..utils.network_utils import fetch_async

CHARACTERS = string.ascii_lowercase + string.digits


class SecondStreetService(BaseService):
    def __init__(self):
        super().__init__()

    @staticmethod
    def fetch_data(params: dict) -> str:
        """
        Fetches data from the 2nd Street website using Playwright for JavaScript rendering.

        Args:
            params (dict): The search parameters.

        Returns:
            str: The HTML content after JavaScript execution.
        """
        try:
            # Build the URL with search parameters
            url = SecondStreetService.get_search_params(params)

            with sync_playwright() as p:
                # Launch browser
                browser = p.firefox.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15"
                )

                # Create a new page
                page = context.new_page()

                # Set additional headers
                page.set_extra_http_headers(
                    {
                        "Accept": "*/*",
                        "Accept-Language": "en-US,en;q=0.9",
                        "Priority": "u=3, i",
                        "Referer": "https://www.2ndstreet.jp/",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "no-cors",
                        "Sec-Fetch-Site": "same-site",
                    }
                )

                # Navigate to the URL
                page.goto(url)

                # Add a small delay to ensure all JavaScript has executed
                page.wait_for_timeout(1000)

                # Get the page content
                content = page.content()

                browser.close()
                return content

        except Exception as e:
            print(f"Error fetching data from SecondStreet with Playwright: {e}")
            return ""

    @staticmethod
    async def fetch_data_async(params: dict) -> str:
        """
        Asynchronously fetches data from the 2nd Street website using Playwright.

        Args:
            params (dict): The search parameters.

        Returns:
            str: The HTML content after JavaScript execution.
        """
        try:
            url = SecondStreetService.get_search_params(params)

            async with async_playwright() as p:
                # Launch browser
                browser = await p.firefox.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15"
                )

                # Create a new page
                page = await context.new_page()

                # Set additional headers
                await page.set_extra_http_headers(
                    {
                        "Accept": "*/*",
                        "Accept-Language": "en-US,en;q=0.9",
                        "Priority": "u=3, i",
                        "Referer": "https://www.2ndstreet.jp/",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "no-cors",
                        "Sec-Fetch-Site": "same-site",
                    }
                )

                # Navigate to the URL (match the sync version more closely)
                await page.goto(url, timeout=30000)

                # Add a small delay to ensure all JavaScript has executed
                await page.wait_for_timeout(1000)

                # Get the page content
                content = await page.content()

                await browser.close()
                return content

        except Exception as e:
            print(f"Error fetching data from SecondStreet with Playwright: {e}")
            return ""

    @staticmethod
    def parse_response(response_text: str, **kwargs) -> list:
        """
        Parses the response from the 2nd Street API.

        Args:
            response_text (str): The response text from the API.

        Returns:
            list: A list of dictionaries containing item information.
        """
        try:
            soup = bs4.BeautifulSoup(response_text, "lxml")
            items = []

            # Find all item cards in the search results
            item_cards = soup.select(".itemCardList.-wrap .itemCard_inner")

            for card in item_cards:
                try:
                    item = {}

                    # Extract the item URL
                    href = card.get("href")
                    if href:
                        if href.startswith("/"):
                            item["url"] = f"https://www.2ndstreet.jp{href}"
                        else:
                            item["url"] = href

                        # Extract ID from URL path
                        # URL format: /goods/detail/goodsId/2334394216531/shopsId/31047
                        url_match = re.search(r"/goodsId/(\d+)/", href)
                        if url_match:
                            item["id"] = url_match.group(1)
                        else:
                            item["id"] = href.split("/")[-1] if href else ""
                    else:
                        continue  # Skip items without URLs

                    # Extract brand
                    brand_element = card.select_one(".itemCard_brand")
                    if brand_element:
                        brand_text = brand_element.get_text().strip()
                        # Clean up font tags
                        brand_text = re.sub(r"<[^>]+>", "", brand_text)
                        item["brand"] = brand_text
                    else:
                        item["brand"] = ""

                    # Extract title/name
                    name_element = card.select_one(".itemCard_name")
                    if name_element:
                        name_text = name_element.get_text().strip()
                        # Clean up font tags
                        name_text = re.sub(r"<[^>]+>", "", name_text)
                        item["title"] = name_text
                    else:
                        item["title"] = ""

                    # Extract price
                    price_element = card.select_one(".itemCard_price")
                    if price_element:
                        price_text = price_element.get_text().strip()
                        # Extract numeric price from text like "¥27,390"
                        price_match = re.search(r"¥([\d,]+)", price_text)
                        if price_match:
                            price_clean = price_match.group(1).replace(",", "")
                            item["price"] = float(price_clean)
                        else:
                            item["price"] = 0.0
                    else:
                        item["price"] = 0.0

                    # Extract image
                    img_element = card.select_one(".itemCard_img img")
                    if img_element:
                        img_src = img_element.get("src")
                        if img_src:
                            if img_src.startswith("//"):
                                img_src = f"https:{img_src}"
                            elif img_src.startswith("/"):
                                img_src = f"https://www.2ndstreet.jp{img_src}"
                            item["img"] = [img_src]
                        else:
                            item["img"] = []
                    else:
                        item["img"] = []

                    # Extract condition/status
                    status_element = card.select_one(".itemCard_status")
                    if status_element:
                        status_text = status_element.get_text().strip()
                        # Clean up font tags
                        status_text = re.sub(r"<[^>]+>", "", status_text)
                        item["condition"] = status_text
                    else:
                        item["condition"] = ""

                    # Extract size from the dedicated size element
                    size_element = card.select_one(".itemCard_size")
                    if size_element:
                        size_text = size_element.get_text().strip()
                        size_text = re.sub(r"サイズ", "", size_text).strip()
                        item["size"] = size_text
                    else:
                        item["size"] = ""

                    items.append(item)

                except Exception as e:
                    print(f"Error parsing individual item: {e}")
                    continue

            return json.dumps(items)

        except Exception as e:
            print(f"Error parsing SecondStreet response: {e}")
            return []

    @staticmethod
    async def parse_response_async(response_text: str, **kwargs) -> list:
        """
        Asynchronously parses the response from the 2nd Street API.

        Args:
            response_text (str): The response text from the API.

        Returns:
            list: A list of dictionaries containing item information.
        """
        return SecondStreetService.parse_response(response_text)

    @staticmethod
    def get_base_details() -> dict:
        """
        Returns base details structure for SecondStreet items.

        Returns:
            dict: Base item details structure.
        """
        return {
            "id": "",
            "title": "",
            "price": 0,
            "url": "",
            "img": [],
            "size": "",
            "brand": "",
            "condition": "",
        }

    @staticmethod
    def add_details(url: str, item: dict) -> dict:
        """
        Adds additional details to an item by fetching its individual page.

        Args:
            url (str): The URL of the item's detail page.
            item (dict): The existing item data.

        Returns:
            dict: The item with additional details.
        """
        try:
            response = SecondStreetService.fetch_item_page(url)
            if response:
                details = SecondStreetService.parse_item_details(response)
                item.update(details)
            return item
        except Exception as e:
            print(f"Error adding details for {url}: {e}")
            return item

    @staticmethod
    async def add_details_async(url: str, item: dict) -> dict:
        """
        Asynchronously adds additional details to an item by fetching its individual page.

        Args:
            url (str): The URL of the item's detail page.
            item (dict): The existing item data.

        Returns:
            dict: The item with additional details.
        """
        try:
            response = await SecondStreetService.fetch_item_page_async(url)
            if response:
                details = SecondStreetService.parse_item_details(response)
                item.update(details)
            return item
        except Exception as e:
            print(f"Error adding details for {url}: {e}")
            return item

    @staticmethod
    async def fetch_item_page_async(url: str) -> str:
        """
        Asynchronously fetch individual item page using Playwright.
        """
        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.firefox.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15"
                )

                # Create a new page
                page = await context.new_page()

                # Set additional headers
                await page.set_extra_http_headers(
                    {
                        "Accept": "*/*",
                        "Accept-Language": "en-US,en;q=0.9",
                        "Priority": "u=3, i",
                        "Referer": "https://www.2ndstreet.jp/",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "no-cors",
                        "Sec-Fetch-Site": "same-site",
                    }
                )

                await page.goto(url, timeout=30000)
                content = await page.content()
                await browser.close()
                return content
        except Exception as e:
            print(f"Error fetching item page: {e}")
            return ""

    @staticmethod
    def fetch_item_page(url: str) -> str:
        """
        Fetch individual item page using Playwright.
        """
        try:
            with sync_playwright() as p:
                # Launch browser
                browser = p.firefox.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15"
                )

                # Create a new page
                page = context.new_page()

                # Set additional headers
                page.set_extra_http_headers(
                    {
                        "Accept": "*/*",
                        "Accept-Language": "en-US,en;q=0.9",
                        "Priority": "u=3, i",
                        "Referer": "https://www.2ndstreet.jp/",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "no-cors",
                        "Sec-Fetch-Site": "same-site",
                    }
                )

                page.goto(url, wait_until="networkidle", timeout=30000)
                content = page.content()
                browser.close()
                return content
        except Exception as e:
            print(f"Error fetching item page: {e}")
            return ""

    @staticmethod
    def parse_item_details(response_text: str):
        # Placeholder implementation - will be implemented when you provide item detail page structure
        soup = bs4.BeautifulSoup(response_text, "lxml")
        details = {}

        # For now, just return empty details since we'll implement this later
        # The title, size, and brand are already extracted from the search results
        details["title"] = None  # Will be updated when you provide item page structure

        return details

    @staticmethod
    def get_search_params(params: dict) -> str:
        base_url = "https://www.2ndstreet.jp/search"

        # Start with base parameters
        url_params = []

        if "keyword" in params and params["keyword"]:
            keyword = params["keyword"]
            url_params.append(f"keyword={keyword}")

        # Add sorting parameter (default to arrival)
        url_params.append("sortBy=arrival")

        # Add page parameter if specified
        if "page" in params and params["page"]:
            # SecondStreet uses 1-based page numbering
            page = params["page"] + 1 if params["page"] >= 0 else 1
            url_params.append(f"page={page}")

        # Construct final URL
        if url_params:
            return f"{base_url}?{'&'.join(url_params)}"
        else:
            return base_url
