from abc import ABC, abstractmethod
import asyncio
import json
import httpx
from postalservice.utils.search_utils import SearchResults


class BaseService(ABC):
    @staticmethod
    @abstractmethod
    def fetch_data(params: dict) -> httpx.Response:
        pass

    @staticmethod
    @abstractmethod
    async def fetch_data_async(params: dict) -> httpx.Response:
        pass

    @staticmethod
    @abstractmethod
    def parse_response(response: httpx.Response, **kwargs) -> str:
        pass

    @staticmethod
    @abstractmethod
    async def parse_response_async(response: httpx.Response, **kwargs) -> str:
        pass

    @classmethod
    async def get_search_results_async(cls, params: dict):
        res = await cls.fetch_data_async(params)
        items = await cls.parse_response_async(res, **params)
        searchresults = SearchResults(items)
        return searchresults.to_list()

    @classmethod
    def get_search_results(cls, params: dict):
        res = cls.fetch_data(params)
        items = cls.parse_response(res, **params)
        searchresults = SearchResults(items)
        return searchresults.to_list()
