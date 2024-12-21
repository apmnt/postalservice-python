import asyncio
from pathlib import Path
import pytest
from pytest_mock import mocker
import httpx
import logging

from postalservice import MercariService, YJPService, FrilService
from postalservice.baseservice import BaseService
from postalservice.utils import SearchParams, SearchResults

from typing import Callable, List, Any


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


@pytest.fixture
def mock_response():
    request = httpx.Request("POST", "https://api.mercari.jp/v2/entities:search")

    return httpx.Response(
        status_code=200,
        content=b'{"meta":{"nextPageToken":"v1:0","previousPageToken":"","numFound":"15000"},"items":[{"id":"m43776722534","sellerId":"439593141","buyerId":"","status":"ITEM_STATUS_ON_SALE","name":"\xe3\x82\xb3\xe3\x83\xa0\xe3\x83\x87\xe3\x82\xae\xe3\x83\xa3\xe3\x83\xab\xe3\x82\xbd\xe3\x83\xb3\xe3\x80\x80\xe3\x83\x88\xe3\x83\xbc\xe3\x83\x88\xe3\x83\x90\xe3\x83\x83\xe3\x82\xb0\xe3\x80\x80\xe3\x83\x89\xe3\x83\x83\xe3\x83\x88\xe6\x9f\x84\xe3\x80\x80\xe3\x82\xb3\xe3\x83\x83\xe3\x83\x88\xe3\x83\xb3\xe3\x80\x80\xe3\x83\x89\xe3\x83\xa1\xe3\x83\x96\xe3\x83\xa9\xe3\x80\x80\xe5\xb8\x8c\xe5\xb0\x91","price":"12600","created":"1701086182","updated":"1729544249","thumbnails":["https://static.mercdn.net/c!/w=240,f=webp/thumb/photos/m43776722534_1.jpg?1701086182"],"itemType":"ITEM_TYPE_MERCARI","itemConditionId":"4","shippingPayerId":"2","itemSizes":[],"itemBrand":{"id":"563","name":"\xe3\x82\xb3\xe3\x83\xa0\xe3\x83\x87\xe3\x82\xae\xe3\x83\xa3\xe3\x83\xab\xe3\x82\xbd\xe3\x83\xb3","subName":"COMME des GARCONS"},"itemPromotions":[],"shopName":"","itemSize":null,"shippingMethodId":"14","categoryId":"353","isNoPrice":false,"title":"","isLiked":false},{"id":"m35043879713","sellerId":"103080527","buyerId":"","status":"ITEM_STATUS_ON_SALE","name":"COMME des GAR\xc3\x87ONS HOMME \xe3\x83\xb4\xe3\x82\xa3\xe3\x83\xb3\xe3\x83\x86\xe3\x83\xbc\xe3\x82\xb8\xe3\x82\xb8\xe3\x83\xa3\xe3\x82\xb1\xe3\x83\x83\xe3\x83\x88 s\xe3\x82\xb5\xe3\x82\xa4\xe3\x82\xba","price":"22200","created":"1699453480","updated":"1729544205","thumbnails":["https://static.mercdn.net/c!/w=240,f=webp/thumb/photos/m35043879713_1.jpg?1699612989"],"itemType":"ITEM_TYPE_MERCARI","itemConditionId":"3","shippingPayerId":"2","itemSizes":[{"id":"2","name":"S"}],"itemBrand":{"id":"7319","name":"\xe3\x82\xb3\xe3\x83\xa0\xe3\x83\x87\xe3\x82\xae\xe3\x83\xa3\xe3\x83\xab\xe3\x82\xbd\xe3\x83\xb3\xe3\x82\xaa\xe3\x83\xa0","subName":"COMME des GARCONS HOMME"},"itemPromotions":[],"shopName":"","itemSize":{"id":"2","name":"S"},"shippingMethodId":"14","categoryId":"314","isNoPrice":false,"title":"","isLiked":false},{"id":"m55515093695","sellerId":"204232876","buyerId":"","status":"ITEM_STATUS_ON_SALE","name":"JUNYA WATANABE \xe3\x82\xb3\xe3\x83\xa0\xe3\x83\x87\xe3\x82\xae\xe3\x83\xa3\xe3\x83\xab\xe3\x82\xbd\xe3\x83\xb3 \xe5\xa4\x89\xe5\xbd\xa2\xe3\x82\xab\xe3\x83\xbc\xe3\x83\x87\xe3\x82\xa3\xe3\x82\xac\xe3\x83\xb3 3D \xe3\x82\xa6\xe3\x83\xbc\xe3\x83\xab","price":"9300","created":"1727357243","updated":"1729544199","thumbnails":["https://static.mercdn.net/c!/w=240,f=webp/thumb/photos/m55515093695_1.jpg?1727357243"],"itemType":"ITEM_TYPE_MERCARI","itemConditionId":"3","shippingPayerId":"2","itemSizes":[{"id":"3","name":"M"}],"itemBrand":{"id":"7389","name":"\xe3\x82\xb8\xe3\x83\xa5\xe3\x83\xb3\xe3\x83\xa4\xe3\x83\xaf\xe3\x82\xbf\xe3\x83\x8a\xe3\x83\x99\xe3\x82\xb3\xe3\x83\xa0\xe3\x83\x87\xe3\x82\xae\xe3\x83\xa3\xe3\x83\xab\xe3\x82\xbd\xe3\x83\xb3","subName":"JUNYA WATANABE COMME des GARCONS"},"itemPromotions":[],"shopName":"","itemSize":{"id":"3","name":"M"},"shippingMethodId":"17","categoryId":"1428","isNoPrice":false,"title":"","isLiked":false},{"id":"m32694745382","sellerId":"920151176","buyerId":"","status":"ITEM_STATUS_ON_SALE","name":"\xe3\x82\xb3\xe3\x83\xa0\xe3\x83\x87\xe3\x82\xae\xe3\x83\xa3\xe3\x83\xab\xe3\x82\xbd\xe3\x83\xb3\xe3\x80\x80\xe3\x82\xb8\xe3\x83\xa5\xe3\x83\xb3\xe3\x83\xa4\xe3\x83\xaf\xe3\x82\xbf\xe3\x83\x8a\xe3\x83\x99\xe3\x80\x80\xe9\x95\xb7\xe8\xa2\x96\xe3\x80\x80\xe3\x82\xb7\xe3\x83\xa3\xe3\x83\x84\xe3\x80\x80XS \xe7\x99\xbd\xe3\x80\x80\xe7\xb6\xbf","price":"13080","created":"1722694682","updated":"1729544174","thumbnails":["https://static.mercdn.net/c!/w=240,f=webp/thumb/photos/m32694745382_1.jpg?1722694682"],"itemType":"ITEM_TYPE_MERCARI","itemConditionId":"3","shippingPayerId":"2","itemSizes":[{"id":"154","name":"XS(SS)"}],"itemBrand":{"id":"563","name":"\xe3\x82\xb3\xe3\x83\xa0\xe3\x83\x87\xe3\x82\xae\xe3\x83\xa3\xe3\x83\xab\xe3\x82\xbd\xe3\x83\xb3","subName":"COMME des GARCONS"},"itemPromotions":[],"shopName":"","itemSize":{"id":"154","name":"XS(SS)"},"shippingMethodId":"17","categoryId":"122","isNoPrice":false,"title":"","isLiked":false},{"id":"m61904499198","sellerId":"670933225","buyerId":"","status":"ITEM_STATUS_ON_SALE","name":"junya watanabe man levi\'s \xe8\xa7\xa3\xe4\xbd\x93\xe5\x86\x8d\xe6\xa7\x8b\xe7\xaf\x89\xe3\x83\x87\xe3\x83\x8b\xe3\x83\xa0","price":"11100","created":"1724912178","updated":"1729544172","thumbnails":["https://static.mercdn.net/c!/w=240,f=webp/thumb/photos/m61904499198_1.jpg?1724912178"],"itemType":"ITEM_TYPE_MERCARI","itemConditionId":"2","shippingPayerId":"1","itemSizes":[{"id":"154","name":"XS(SS)"}],"itemBrand":{"id":"7390","name":"\xe3\x82\xb8\xe3\x83\xa5\xe3\x83\xb3\xe3\x83\xa4\xe3\x83\xaf\xe3\x82\xbf\xe3\x83\x8a\xe3\x83\x99\xe3\x82\xb3\xe3\x83\xa0\xe3\x83\x87\xe3\x82\xae\xe3\x83\xa3\xe3\x83\xab\xe3\x82\xbd\xe3\x83\xb3\xe3\x83\x87\xe3\x83\x8b\xe3\x83\xa0","subName":"JUNYA WATANABE COMME des GARCONS DENIM"},"itemPromotions":[],"shopName":"","itemSize":{"id":"154","name":"XS(SS)"},"shippingMethodId":"1","categoryId":"10852","isNoPrice":false,"title":"","isLiked":false},{"id":"m32742578858","sellerId":"767473578","buyerId":"","status":"ITEM_STATUS_ON_SALE","name":"\xe3\x83\x88\xe3\x83\xaa\xe3\x82\xb3\xe3\x82\xb3\xe3\x83\xa0\xe3\x83\x87\xe3\x82\xae\xe3\x83\xa3\xe3\x83\xab\xe3\x82\xbd\xe3\x83\xb3\xe3\x80\x80\xe3\x82\xbb\xe3\x83\x83\xe3\x83\x88\xe3\x82\xa2\xe3\x83\x83\xe3\x83\x97\xe3\x80\x80\xe3\x83\x95\xe3\x83\xaa\xe3\x83\xab\xe3\x80\x80\xe3\x83\x95\xe3\x83\xa9\xe3\x83\xaf\xe3\x83\xbc\xe3\x80\x8000s \xe3\x82\xb9\xe3\x82\xab\xe3\x83\xbc\xe3\x83\x88\xe3\x80\x80\xe3\x82\xb7\xe3\x83\xa3\xe3\x83\x84","price":"16000","created":"1725305125","updated":"1729544144","thumbnails":["https://static.mercdn.net/c!/w=240,f=webp/thumb/photos/m32742578858_1.jpg?1725305125"],"itemType":"ITEM_TYPE_MERCARI","itemConditionId":"2","shippingPayerId":"2","itemSizes":[{"id":"3","name":"M"}],"itemBrand":{"id":"7529","name":"\xe3\x83\x88\xe3\x83\xaa\xe3\x82\xb3\xe3\x82\xb3\xe3\x83\xa0\xe3\x83\x87\xe3\x82\xae\xe3\x83\xa3\xe3\x83\xab\xe3\x82\xbd\xe3\x83\xb3","subName":"tricot COMME des GARCONS"},"itemPromotions":[],"shopName":"","itemSize":{"id":"3","name":"M"},"shippingMethodId":"17","categoryId":"1489","isNoPrice":false,"title":"","isLiked":false},{"id":"m83543244879","sellerId":"687118644","buyerId":"","status":"ITEM_STATUS_ON_SALE","name":"AD1989 \xe3\x82\xb3\xe3\x83\xa0 \xe3\x83\x87 \xe3\x82\xae\xe3\x83\xa3\xe3\x83\xab\xe3\x82\xbd\xe3\x83\xb3 / \xe3\x82\xa2\xe3\x82\xb7\xe3\x83\xb3\xe3\x83\xa1\xe3\x83\x88\xe3\x83\xaa\xe3\x83\xbc\xe3\x83\xa9\xe3\x83\x83\xe3\x83\x97 \xe3\x82\xb9\xe3\x82\xa6\xe3\x82\xa7\xe3\x83\x83\xe3\x83\x88 \xe3\x83\x91\xe3\x83\xb3\xe3\x83\x84","price":"18600","created":"1727357146","updated":"1729544133","thumbnails":["https://static.mercdn.net/c!/w=240,f=webp/thumb/photos/m83543244879_1.jpg?1727357146"],"itemType":"ITEM_TYPE_MERCARI","itemConditionId":"3","shippingPayerId":"2","itemSizes":[{"id":"2","name":"S"}],"itemBrand":{"id":"563","name":"\xe3\x82\xb3\xe3\x83\xa0\xe3\x83\x87\xe3\x82\xae\xe3\x83\xa3\xe3\x83\xab\xe3\x82\xbd\xe3\x83\xb3","subName":"COMME des GARCONS"},"itemPromotions":[],"shopName":"","itemSize":{"id":"2","name":"S"},"shippingMethodId":"14","categoryId":"1476","isNoPrice":false,"title":"","isLiked":false},{"id":"m10991495749","sellerId":"494528507","buyerId":"","status":"ITEM_STATUS_ON_SALE","name":"COMME des GARCONS \xe3\x82\xb3\xe3\x83\xa0\xe3\x83\x87\xe3\x82\xae\xe3\x83\xa3\xe3\x83\xab\xe3\x82\xbd\xe3\x83\xb3\xe3\x80\x80\xe3\x83\x8f\xe3\x83\xbc\xe3\x83\x88\xe3\x80\x80\xe3\x82\xb8\xe3\x83\xa3\xe3\x82\xb1\xe3\x83\x83\xe3\x83\x88\xe3\x80\x80\xe3\x83\xa1\xe3\x83\xb3\xe3\x82\xba","price":"19799","created":"1709640294","updated":"1729544107","thumbnails":["https://static.mercdn.net/c!/w=240,f=webp/thumb/photos/m10991495749_1.jpg?1709640294"],"itemType":"ITEM_TYPE_MERCARI","itemConditionId":"3","shippingPayerId":"2","itemSizes":[{"id":"3","name":"M"}],"itemBrand":{"id":"7319","name":"\xe3\x82\xb3\xe3\x83\xa0\xe3\x83\x87\xe3\x82\xae\xe3\x83\xa3\xe3\x83\xab\xe3\x82\xbd\xe3\x83\xb3\xe3\x82\xaa\xe3\x83\xa0","subName":"COMME des GARCONS HOMME"},"itemPromotions":[],"shopName":"","itemSize":{"id":"3","name":"M"},"shippingMethodId":"14","categoryId":"335","isNoPrice":false,"title":"","isLiked":false},{"id":"m76146058470","sellerId":"996163716","buyerId":"","status":"ITEM_STATUS_ON_SALE","name":"COMME des GARCONS HOMME PLUS 00AW Jacket","price":"37000","created":"1726666284","updated":"1729544012","thumbnails":["https://static.mercdn.net/c!/w=240,f=webp/thumb/photos/m76146058470_1.jpg?1726666284"],"itemType":"ITEM_TYPE_MERCARI","itemConditionId":"4","shippingPayerId":"2","itemSizes":[{"id":"3","name":"M"}],"itemBrand":{"id":"7321","name":"\xe3\x82\xb3\xe3\x83\xa0\xe3\x83\x87\xe3\x82\xae\xe3\x83\xa3\xe3\x83\xab\xe3\x82\xbd\xe3\x83\xb3\xe3\x82\xaa\xe3\x83\xa0\xe3\x83\x97\xe3\x83\xaa\xe3\x83\xa5\xe3\x82\xb9","subName":"COMME des GARCONS HOMME PLUS"},"itemPromotions":[],"shopName":"","itemSize":{"id":"3","name":"M"},"shippingMethodId":"14","categoryId":"314","isNoPrice":false,"title":"","isLiked":false},{"id":"ZHoogkkHAkVkwfACrChNVW","sellerId":"0","buyerId":"","status":"ITEM_STATUS_ON_SALE","name":"\xe3\x80\x90\xe9\x9b\xb7\xe5\xb8\x82\xe5\xa0\xb4\xef\xbc\x88\xe3\x83\x9d\xe3\x83\xb3\xe3\x82\xb8\xe3\x83\xa3\xe3\x83\xb3\xef\xbc\x89\xe5\x95\x86\xe5\x93\x81\xe9\x9f\x93\xe5\x9b\xbd\xe7\x9b\xb4\xe9\x80\x81\xe3\x80\x91 COMME des GARCONS(\xe3\x82\xb3\xe3\x83\xa0\xe3\x83\xbb\xe3\x83\x87\xe3\x83\xbb\xe3\x82\xae\xe3\x83\xa3\xe3\x83\xab\xe3\x82\xbd\xe3\x83\xb3) \xe3\x82\xb8\xe3\x83\xa5\xe3\x83\xb3\xe3\x83\xa4 \xe3\x83\xaf\xe3\x82\xbf\xe3\x83\x8a\xe3\x83\x99 \xe3\x83\x9d\xe3\x82\xb1\xe3\x83\x83\xe3\x83\x88 \xe5\x8d\x8a\xe8\xa2\x96","price":"12481","created":"1729543983","updated":"1729543983","thumbnails":["https://assets.mercari-shops-static.com/-/small/plain/P58nbm4QP5ZHnDixnLZ3uB.webp@webp"],"itemType":"ITEM_TYPE_BEYOND","itemConditionId":"2","shippingPayerId":"0","itemSizes":[],"itemBrand":{"id":"563","name":"\xe3\x82\xb3\xe3\x83\xa0\xe3\x83\x87\xe3\x82\xae\xe3\x83\xa3\xe3\x83\xab\xe3\x82\xbd\xe3\x83\xb3","subName":"COMME des GARCONS"},"itemPromotions":[],"shopName":"","itemSize":null,"shippingMethodId":"0","categoryId":"302","isNoPrice":false,"title":"","isLiked":false}],"components":[],"searchCondition":null,"searchConditionId":""}\n',
        request=request,
    )


@pytest.fixture
def mock_item_response(mock_request):
    return


@pytest.mark.parametrize("service_fixture", ["mercari_service"])
def test_fetch_code_200(service_fixture, mocker, request, logger) -> None:
    # Get the service fixture
    service: BaseService = request.getfixturevalue(service_fixture)

    # Mock the response
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mocker.patch.object(service, "fetch_data", return_value=mock_response)

    res = service.fetch_data()
    logger.info("Fetched data: %s", res)
    assert res.status_code == 200


@pytest.mark.parametrize("service_fixture", ["mercari_service"])
@pytest.mark.asyncio
async def test_fetch_code_200_async(service_fixture, mocker, request, logger):
    # Get the service fixture
    service: BaseService = request.getfixturevalue(service_fixture)

    # Mock the response
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mocker.patch.object(service, "fetch_data", return_value=mock_response)

    sparams = SearchParams("comme des garcons")
    res = await service.fetch_data_async(sparams.get_dict())
    logger.info("Fetched data: %s", res)
    assert res.status_code == 200


@pytest.mark.parametrize("service_fixture", ["mercari_service"])
def test_parse_results(service_fixture, mocker, request, logger, mock_response):
    # Get the service fixture
    service = request.getfixturevalue(service_fixture)

    # Mock the response
    mocker.patch.object(service, "fetch_data", return_value=mock_response)

    sparams = SearchParams("comme des garcons")
    res = service.fetch_data(sparams.get_dict())
    items = service.parse_response(res)
    searchresults = SearchResults(items)
    logger.info(searchresults)
    assert searchresults.count() > 0
