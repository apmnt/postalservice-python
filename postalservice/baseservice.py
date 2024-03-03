from abc import ABC, abstractmethod
import asyncio
import json
import httpx
from postalservice.utils.search_utils import SearchParams

class BaseService(ABC):
    @abstractmethod
    async def fetch_data(self, params: dict) -> httpx.Response:

        pass

    @abstractmethod
    def parse_response(self, response: str) -> str:

        pass

    @abstractmethod
    def get_search_params(self, data: SearchParams) -> str:

        pass

    def get_search_results(self, params: dict) -> str:
        res = asyncio.run(self.fetch_data(params))
        return self.parse_response(res)
    
    def get_search_results_dict(self, params: dict) -> dict:
        print(params)
        res = asyncio.run(self.fetch_data(params))
        print(res)
        parsed_response = self.parse_response(res)
        itemdict = json.loads(parsed_response)
        return itemdict
        
