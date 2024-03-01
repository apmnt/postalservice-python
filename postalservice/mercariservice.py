import json
import random
import string
import httpx
from postalservice.postalservice import PostalService
from postalservice.utils.network_utils import get_pop_jwt
from postalservice.utils.search_utils import SearchParams

CHARACTERS = string.ascii_lowercase + string.digits
HITS_PER_PAGE = 10

class MercariService(PostalService):
    
    async def fetchdata(self, message: str):
            
        # print("""
        # -----------------
        #    Mercari API
        # -----------------
        # """)
        
        search_term = message

        url = "https://api.mercari.jp/v2/entities:search"
        searchSessionId = ''.join(random.choice(CHARACTERS) for i in range(32))
        payload = {
            "userId": "",
            "pageSize": HITS_PER_PAGE,
            "searchSessionId": searchSessionId,
            "indexRouting": "INDEX_ROUTING_UNSPECIFIED",
            "thumbnailTypes": [],
            "searchCondition": {
                "keyword": search_term,
                "excludeKeyword": "",
                "sort": "SORT_CREATED_TIME",
                "order": "ORDER_DESC",
                "status": [],
                "sizeId": [],
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
            "withItemBrand": False,
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
        
        
    def parse_data(self, response: str):
        items = json.loads(response.text)['items']
        toPost = []
        for item in items:
            temp = {}
            temp["site"] = "MERCARI"
            temp['id'] = item['id']
            temp['title'] = item['name']
            temp['price'] = item['price']+' JPY'
            try:
                temp['size'] = item['itemSize']['name']
            except:
                temp['size'] = '-'
            temp['url'] =  'https://jp.mercari.com/item/' + item['id']
            temp['img'] = item['thumbnails'][0]
            toPost.append(temp)
        return toPost
    
    def get_search_params(self, data: SearchParams):
        return data.get_all()