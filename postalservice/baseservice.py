from abc import ABC, abstractmethod
import asyncio
import json
import httpx
from postalservice.utils.search_utils import SearchParams, SearchResults

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

    async def get_search_results_async(self, params: dict) -> SearchResults:
        res = await self.fetch_data_async(params)
        items = await self.parse_response_async(res)
        searchresults = SearchResults(items)
        return searchresults
    
    def get_search_results(self, params: dict) -> SearchResults:
        res = self.fetch_data(params)
        items = self.parse_response(res)
        searchresults = SearchResults(items)
        return searchresults
