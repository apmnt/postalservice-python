from abc import ABC, abstractmethod
from postalservice.utils.search_utils import SearchParams

class PostalService(ABC):
    @abstractmethod
    async def fetch_data(self, message: str):

        pass

    @abstractmethod
    def parse_data(self, data: str):

        pass

    @abstractmethod
    def get_search_params(self, data: SearchParams):

        pass
    


