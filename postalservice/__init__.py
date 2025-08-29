from .services.mercari import MercariService
from .services.fril import FrilService
from .services.yjp import YJPService
from .services.secondstreet import SecondStreetService
from .services.kindal import KindalService
from .services.ragtag import RagtagService
from .services.okoku import OkokuService
from .services.trefac import TrefacService


def create_search_params(
    keyword: str,
    size: str = None,
    category: str = None,
    brands: list = None,
    item_count: int = 10,
    page: int = 0,
) -> dict:
    """
    Convenience function to build search parameters.

    Args:
        keyword (str): The search keyword.
        size (str, optional): The size filter for the search. Defaults to None.
        category (str, optional): The category filter for the search. Defaults to None.
        brands (list, optional): A list of brand filters for the search. Defaults to None.
        item_count (int, optional): The number of items to return per page. Defaults to 10.
        page (int, optional): The page number to return. Defaults to 0.

    Returns:
        dict: A dictionary containing the search parameters.

    """
    return {
        "size": size,
        "keyword": keyword,
        "category": category,
        "brand": brands,
        "item_count": item_count,
        "page": page,
    }
