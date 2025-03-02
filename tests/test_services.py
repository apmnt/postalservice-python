import pytest
import logging
from postalservice import MercariService, YJPService, FrilService
from postalservice.baseservice import BaseService
from postalservice.utils import SearchParams, SearchResults


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
def test_fetch_code_200(service_fixture, request, logger) -> None:
    # Get the service fixture
    service: BaseService = request.getfixturevalue(service_fixture)
    params = SearchParams("comme des garcons")
    res = service.fetch_data(params.get_dict())
    logger.info("Fetched data: %s", res)
    assert res.status_code == 200


@pytest.mark.parametrize("service_fixture", SERVICE_LIST)
def test_parse_results(service_fixture, request, logger):
    # Get the service fixture
    service = request.getfixturevalue(service_fixture)

    sparams = SearchParams("comme des garcons")
    res = service.fetch_data(sparams.get_dict())
    items = service.parse_response(res)
    searchresults = SearchResults(items)
    logger.info(searchresults)
    assert searchresults.count() > 0


@pytest.mark.parametrize("service_fixture", SERVICE_LIST)
def test_get_search_results(service_fixture, request, logger):
    # Get the service fixture
    service = request.getfixturevalue(service_fixture)

    sparams = SearchParams("comme des garcons")
    searchresults = service.get_search_results(sparams.get_dict())
    logger.info(searchresults)
    assert searchresults.count() > 0


# ----- ASYNC TESTS -----


@pytest.mark.parametrize("service_fixture", SERVICE_LIST)
@pytest.mark.asyncio
async def test_async_fetch_code_200(service_fixture, request, logger):
    # Get the service fixture
    service: BaseService = request.getfixturevalue(service_fixture)
    params = SearchParams("comme des garcons")
    res = await service.fetch_data_async(params.get_dict())
    logger.info("Fetched data: %s", res)
    assert res.status_code == 200


@pytest.mark.parametrize("service_fixture", SERVICE_LIST)
@pytest.mark.asyncio
async def test_async_parse_results(service_fixture, request, logger):
    # Get the service fixture
    service = request.getfixturevalue(service_fixture)

    sparams = SearchParams("comme des garcons")
    res = await service.fetch_data_async(sparams.get_dict())
    items = await service.parse_response_async(res)
    searchresults = SearchResults(items)
    logger.info(searchresults)
    assert searchresults.count() > 0


@pytest.mark.parametrize("service_fixture", SERVICE_LIST)
@pytest.mark.asyncio
async def test_async_get_search_results(service_fixture, request, logger):
    # Get the service fixture
    service = request.getfixturevalue(service_fixture)

    sparams = SearchParams("comme des garcons")
    searchresults = await service.get_search_results_async(sparams.get_dict())
    logger.info(searchresults)
    assert searchresults.count() > 0
