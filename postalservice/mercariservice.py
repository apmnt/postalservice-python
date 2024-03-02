import json
import random
import string
import httpx
from postalservice.postalservice import PostalService
from postalservice.utils.network_utils import get_pop_jwt
from postalservice.utils.search_utils import SearchParams

CHARACTERS = string.ascii_lowercase + string.digits

SIZE_MAP = {
    "S": "2",
    "M": "3",
    "L": "4",
    "XL": "5",
}

class MercariService(PostalService):
    
    async def fetch_data(self, params: dict) -> str:
        '''
        Fetches data from the Mercari API.

        Args:
            params (dict): The search parameters.

        Returns:
            httpx.Response: The response from the API.
        '''

        if not isinstance(params, dict):
            raise TypeError('params must be a dict')

        keyword = params.get('keyword')

        sizes = params.get('size')
        if sizes is not None: mapped_sizes = [SIZE_MAP.get(size) for size in sizes]
        else: mapped_sizes = []

        item_count = params.get('item_count')
        page = params.get('page')

        url = "https://api.mercari.jp/v2/entities:search"
        searchSessionId = ''.join(random.choice(CHARACTERS) for i in range(32))
        payload = {
            "userId": "",
            "pageSize": item_count,
            "searchSessionId": searchSessionId,
            "indexRouting": "INDEX_ROUTING_UNSPECIFIED",
            "thumbnailTypes": [],
            "searchCondition": {
                "keyword": keyword,
                "excludeKeyword": "",
                "sort": "SORT_CREATED_TIME",
                "order": "ORDER_DESC",
                "status": ["STATUS_ON_SALE"],
                "sizeId": mapped_sizes,
                "categoryId": [],
                "brandId": [],
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
                "skuIds": []
            },
            "defaultDatasets": ["DATASET_TYPE_MERCARI", "DATASET_TYPE_BEYOND"],
            "serviceFrom": "suruga",
            "userId": "",
            "withItemBrand": True,
            "withItemSize": True
        }
        headers = {
            "dpop": get_pop_jwt(url, "POST"),
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "x-platform": "web"
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200: return response
            else: 
                raise Exception(f"Failed to fetch data from Mercari API. Status code: {response.status_code}")
        
    def parse_response(self, response: str) -> str:
        """
        Parses the response from the Mercari API and returns a cleaned JSON string.

        Args:
            response (str): The response from the API.

        Returns:
            str: The cleaned JSON string.

        Raises:
            TypeError: If the response argument is not a string.
        """
        items = json.loads(response)['items']
        cleaned_items_list = []
        for item in items:
            temp = {}
            temp['id'] = item['id']
            temp['title'] = item['name']
            price = float(item.get('price'))
            temp['price'] = price
            temp['size'] = item['itemSize'].get('name')
            temp['url'] =  'https://jp.mercari.com/item/' + item['id']
            temp['img'] = item['thumbnails']
            cleaned_items_list.append(temp)

        item_json = json.dumps(cleaned_items_list)
        return item_json
    
    def get_search_params(self, data: SearchParams) -> str:
        return None