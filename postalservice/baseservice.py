from abc import ABC, abstractmethod
import asyncio
import json
import httpx
from postalservice.utils.search_utils import SearchParams

class BaseService(ABC):
    @abstractmethod
    def fetch_data(self, params: dict) -> httpx.Response:

        pass

    @abstractmethod
    async def fetch_data_async(self, params: dict) -> httpx.Response:

        pass

    @abstractmethod
    def parse_response(self, response: str) -> str:

        pass

    @abstractmethod
    async def parse_response_async(self, response: str) -> str:

        pass


    @abstractmethod
    def get_search_params(self, data: SearchParams) -> str:

        pass

    async def get_search_results_async(self, params: dict) -> str:
        res = await self.fetch_data_async(params)
        return await self.parse_response_async(res)
    
    def get_search_results(self, params: dict) -> str:
        res = self.fetch_data(params)
        items = self.parse_response(res)
        return items