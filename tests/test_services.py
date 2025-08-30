import pytest
import logging
from postalservice import MercariService, YJPService, FrilService, create_search_params
from postalservice.services.baseservice import BaseService
from postalservice.utils import SearchResults


@pytest.fixture(scope="module")
def logger():
    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("TESTS %(levelname)s: %(message)s ")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


@pytest.fixture(scope="module")
def mercari_service():
    return MercariService()


@pytest.fixture(scope="module")
def yjp_service():
    return YJPService()


@pytest.fixture(scope="module")
def fril_service():
    return FrilService()


SERVICE_LIST = ["mercari_service", "fril_service", "yjp_service"]


@pytest.mark.parametrize("service_fixture", SERVICE_LIST)
def test_fetch_code_200(
    service_fixture: str, request: pytest.FixtureRequest, logger: logging.Logger
) -> None:
    # Get the service fixture
    service: BaseService = request.getfixturevalue(service_fixture)

    sparams = create_search_params("junya", item_count=1)
    res = service.fetch_data(sparams)
    logger.info("Fetched data: %s", res)

    # assert res.status_code == 200


@pytest.mark.parametrize("service_fixture", SERVICE_LIST)
def test_parse_results(
    service_fixture: str, request: pytest.FixtureRequest, logger: logging.Logger
):
    # Get the service fixture
    service = request.getfixturevalue(service_fixture)

    sparams = create_search_params("junya", item_count=1)
    res = service.fetch_data(sparams)
    items = service.parse_response(res)
    searchresults = SearchResults(items)
    logger.info(searchresults)

    # assert searchresults.count() == 1


@pytest.mark.parametrize("service_fixture", SERVICE_LIST)
def test_get_search_results(
    service_fixture: str, request: pytest.FixtureRequest, logger: logging.Logger
):
    # Get the service fixture
    service = request.getfixturevalue(service_fixture)

    sparams = create_search_params("junya", item_count=1)
    searchresults = service.get_search_results(sparams)
    logger.info(searchresults)

    # assert searchresults.count() == 1


# ----- ASYNC TESTS -----


@pytest.mark.parametrize("service_fixture", SERVICE_LIST)
@pytest.mark.asyncio
async def test_async_fetch_code_200(
    service_fixture: str, request: pytest.FixtureRequest, logger: logging.Logger
):
    # Get the service fixture
    service: BaseService = request.getfixturevalue(service_fixture)

    sparams = create_search_params("junya", item_count=1)
    res = await service.fetch_data_async(sparams)
    logger.info("Fetched data: %s", res)

    # assert res.status_code == 200


@pytest.mark.parametrize("service_fixture", SERVICE_LIST)
@pytest.mark.asyncio
async def test_async_parse_results(
    service_fixture: str, request: pytest.FixtureRequest, logger: logging.Logger
):
    # Get the service fixture
    service = request.getfixturevalue(service_fixture)

    sparams = create_search_params("junya", item_count=1)
    res = await service.fetch_data_async(sparams)
    items = await service.parse_response_async(res)
    searchresults = SearchResults(items)
    logger.info(searchresults)

    # assert searchresults.count() == 1


@pytest.mark.parametrize("service_fixture", SERVICE_LIST)
@pytest.mark.asyncio
async def test_async_get_search_results(
    service_fixture: str, request: pytest.FixtureRequest, logger: logging.Logger
):
    # Get the service fixture
    service = request.getfixturevalue(service_fixture)

    sparams = create_search_params("junya", item_count=1)
    searchresults = await service.get_search_results_async(sparams)
    logger.info(searchresults)

    # assert searchresults.count() == 1
