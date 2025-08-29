import json
import time
import uuid
import httpx
from .baseservice import BaseService


class KindalService(BaseService):

    @staticmethod
    def generate_url_and_headers(params: dict):
        """
        Generates URL and headers for Kindal API request.

        Args:
            params (dict): The search parameters.

        Returns:
            tuple: A tuple containing (url, headers).
        """
        if not isinstance(params, dict):
            raise TypeError("params must be a dict")

        keyword = params.get("keyword", "")
        page = params.get("page", 1)
        item_count = params.get("item_count", 48)

        # Generate required IDs
        timestamp = int(time.time() * 1000)
        session_id = str(uuid.uuid4())
        request_id = str(uuid.uuid4())

        # Build URL with query parameters
        base_url = "https://services.mybcapps.com/bc-sf-filter/search"
        url_params = {
            "t": str(timestamp),
            "shop": "kindal-online24.myshopify.com",
            "page": str(page),
            "limit": str(item_count),
            "sort": "number-extra-sort1-descending",
            "locale": "ja",
            "build_filter_tree": "true",
            "sid": session_id,
            "pg": "search_page",
            "zero_options": "true",
            "product_available": "false",
            "variant_available": "false",
            "sort_first": "available",
            "urlScheme": "2",
            "collection_scope": "0",
            "q": keyword,
            "event_type": "init",
            "query": keyword,
            "parent_request_id": request_id,
            "item_rank": "1",
            "suggestion": keyword,
        }

        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://shop.kind.co.jp",
            "Priority": "u=3, i",
            "Referer": "https://shop.kind.co.jp/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15",
        }

        return base_url, url_params, headers

    @staticmethod
    async def fetch_data_async(params: dict) -> httpx.Response:
        """
        Fetches data from the Kindal API using the provided search parameters.

        Args:
            params (dict): The search parameters.

        Returns:
            httpx.Response: The response from the API.

        Raises:
            TypeError: If params is not a dictionary.
            Exception: If the API request fails.
        """
        url, url_params, headers = KindalService.generate_url_and_headers(params)

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=url_params, headers=headers)
            return response

    @staticmethod
    def fetch_data(params: dict) -> httpx.Response:
        """
        Fetches data from the Kindal API using the provided search parameters.

        Args:
            params (dict): The search parameters.

        Returns:
            httpx.Response: The response from the API.

        Raises:
            TypeError: If params is not a dictionary.
            Exception: If the API request fails.
        """
        url, url_params, headers = KindalService.generate_url_and_headers(params)

        with httpx.Client() as client:
            response = client.get(url, params=url_params, headers=headers)
            return response

    @staticmethod
    def parse_response(response: httpx.Response, **kwargs) -> str:
        """
        Parses the response from the Kindal API and returns a JSON string of cleaned items.

        Each item is a dictionary with the following keys:
        - 'id': The item's ID.
        - 'title': The item's name.
        - 'price': The item's price.
        - 'size': The item's size, or None if not available.
        - 'url': The URL of the item.
        - 'img': A list of the item's image URLs.
        - 'brand': The item's brand.

        Args:
            response (httpx.Response): The response from the API.

        Returns:
            str: A JSON string of cleaned items.
        """
        data = json.loads(response.text)
        products = data.get("products", [])
        cleaned_items_list = []

        for product in products:
            temp = {}
            temp["id"] = str(product.get("id", ""))
            temp["title"] = product.get("title", "")

            # Get price from variants or price_min
            if product.get("variants") and len(product["variants"]) > 0:
                price = float(product["variants"][0].get("price", 0))
            else:
                price = float(product.get("price_min", 0))
            temp["price"] = price

            # Extract size from metafields
            size = None
            metafields = product.get("metafields", [])
            for field in metafields:
                if field.get("key") == "tag_size" or field.get("key") == "size":
                    size = field.get("value")
                    break
            temp["size"] = size

            # Build product URL
            handle = product.get("handle", "")
            temp["url"] = f"https://shop.kind.co.jp/products/{handle}"

            # Get images
            images = []
            images_info = product.get("images_info", [])
            for img_info in images_info:
                images.append(img_info.get("src", ""))
            temp["img"] = images

            # Get brand from vendor
            temp["brand"] = product.get("vendor", "--")

            cleaned_items_list.append(temp)

        item_json = json.dumps(cleaned_items_list)
        return item_json

    @staticmethod
    async def parse_response_async(response: httpx.Response, **kwargs) -> str:
        return KindalService.parse_response(response)
