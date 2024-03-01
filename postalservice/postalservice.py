from abc import ABC, abstractmethod
import httpx
from postalservice.utils.search_utils import SearchParams

class PostalService(ABC):
    @abstractmethod
    async def fetch_data(self, params: dict) -> httpx.Response:

        pass

    @abstractmethod
    def parse_response(self, response: str) -> str:

        pass

    @abstractmethod
    def get_search_params(self, data: SearchParams) -> str:

        pass
    


