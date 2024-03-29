import asyncio
import json
import random
import string
import httpx
from .baseservice import BaseService
from .utils.network_utils import get_pop_jwt
from .utils.search_utils import SearchParams

CHARACTERS = string.ascii_lowercase + string.digits

SIZE_MAP = {
    "FREE / ONESIZE": "7",
    "XS": "154",
    "S": "2",
    "M": "3",
    "L": "4",
    "XL": "5",
    "XXL": "155",
}
BREANS_MAP = {
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


class MercariService(BaseService):

    def generate_payload_and_headers(self, params: dict):
        if not isinstance(params, dict):
            raise TypeError("params must be a dict")

        keyword = params.get("keyword")
        size = params.get("size")
        item_count = params.get("item_count")
        page_number = params.get("page")
        if page_number is None:
            page_token = ""
        else:
            page_token = f"v1:{page_number - 1}"

        if size is not None:
            mapped_size = SIZE_MAP.get(size)
        else:
            mapped_size = None

        brands = params.get("brand")
        print("brands raw")
        print(brands)
        if brands is None:
            brands = []
        else:
            brands = [BREANS_MAP.get(brand) for brand in brands]

        url = "https://api.mercari.jp/v2/entities:search"
        searchSessionId = "".join(random.choice(CHARACTERS) for i in range(32))
        payload = {
            "userId": "",
            "pageSize": item_count,
            "pageToken": page_token,
            "searchSessionId": searchSessionId,
            "indexRouting": "INDEX_ROUTING_UNSPECIFIED",
            "thumbnailTypes": [],
            "searchCondition": {
                "keyword": keyword,
                "excludeKeyword": "",
                "sort": "SORT_CREATED_TIME",
                "order": "ORDER_DESC",
                "status": ["STATUS_ON_SALE"],
                "sizeId": [mapped_size],
                "categoryId": [],
                "brandId": brands,
                "sellerId": [],
                "priceMin": 0,
                "priceMax": 0,
                "itemConditionId": [],
                "shippingPayerId": [],
                "shippingFromArea": [],
                "shippingMethod": [],
                "colorId": [],
                "hasCoupon": False,
                "attributes": [],
                "itemTypes": [],
                "skuIds": [],
            },
            "defaultDatasets": ["DATASET_TYPE_MERCARI", "DATASET_TYPE_BEYOND"],
            "serviceFrom": "suruga",
            "userId": "",
            "withItemBrand": True,
            "withItemSize": True,
        }
        headers = {
            "dpop": get_pop_jwt(url, "POST"),
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "x-platform": "web",
        }

        return payload, headers

    async def fetch_data_async(self, params: dict) -> httpx.Response:
        """
        Fetches data from the Mercari API using the provided search parameters.

        Args:
            params (dict): The search parameters.

        Returns:
            httpx.Response: The response from the API.

        Raises:
            TypeError: If params is not a dictionary.
            Exception: If the API request fails.
        """

        url = "https://api.mercari.jp/v2/entities:search"
        payload, headers = self.generate_payload_and_headers(params)

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            return response

    def fetch_data(self, params: dict) -> httpx.Response:
        """
        Fetches data from the Mercari API using the provided search parameters.

        Args:
            params (dict): The search parameters.

        Returns:
            httpx.Response: The response from the API.

        Raises:
            TypeError: If params is not a dictionary.
            Exception: If the API request fails.
        """

        url = "https://api.mercari.jp/v2/entities:search"
        payload, headers = self.generate_payload_and_headers(params)

        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=headers)
            return response

    def parse_response(self, response: httpx.Response) -> str:
        """
        Parses the response from the Mercari API and returns a JSON string of cleaned items.

        Each item is a dictionary with the following keys:
        - 'id': The item's ID.
        - 'title': The item's name.
        - 'price': The item's price.
        - 'size': The item's size, or None if not available.
        - 'url': The URL of the item.
        - 'img': A list of the item's thumbnails.

        Args:
            response (httpx.Response): The response from the API.

        Returns:
            str: A JSON string of cleaned items.
        """

        items = json.loads(response.text)["items"]
        cleaned_items_list = []
        for item in items:
            temp = {}
            temp["id"] = item["id"]
            temp["title"] = item["name"]
            price = float(item.get("price"))
            temp["price"] = price
            if item.get("itemSize") is not None:
                temp["size"] = item["itemSize"].get("name")
            else:
                temp["size"] = None
            temp["url"] = "https://jp.mercari.com/item/" + item["id"]
            thumbnails = item["thumbnails"]
            temp["img"] = []
            for img in thumbnails:
                temp["img"].append(
                    img.replace("c!/w=240,f=webp/thumb", "item/detail/orig")
                )
            print(item)
            if item.get("itemBrand") is not None:
                temp["brand"] = item.get("itemBrand").get("subName")
            else:
                temp["brand"] = "--"
            cleaned_items_list.append(temp)

        item_json = json.dumps(cleaned_items_list)
        return item_json

    async def parse_response_async(self, response: httpx.Response) -> str:
        return self.parse_response(response)

    def get_search_params(self, data: SearchParams) -> str:
        return ""
