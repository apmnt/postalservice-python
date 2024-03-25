import asyncio
import unittest

import httpx
import postalservice
import logging
from postalservice.utils import SearchResults, SearchParams


class _BaseServiceTestClass(object):

    @classmethod
    def setUpClass(cls):
        # Create a logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("TESTS %(levelname)s: %(message)s ")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        cls.logger = logger

    def test_fetch_code_200(self):
        sparams = SearchParams("comme des garcons")
        res = self.service.fetch_data(sparams.get_dict())
        self.logger.info("Fetched data: %s", res)

        # Assert that the status code is 200
        self.assertEqual(res.status_code, 200)

    def test_fetch_code_200_async(self):
        sparams = SearchParams("comme des garcons")
        res = asyncio.run(self.service.fetch_data_async(sparams.get_dict()))
        self.logger.info("Fetched data: %s", res)

        # Assert that the status code is 200
        self.assertEqual(res.status_code, 200)

    def test_parse_results(self):
        sparams = SearchParams("comme des garcons")
        res: httpx.Response = self.service.fetch_data(sparams.get_dict())
        items: str = self.service.parse_response(res)
        searchresults = SearchResults(items)
        self.logger.info(searchresults)

        # Assert that the count is greater than 0
        self.assertTrue(searchresults.count() > 0)

    def test_parse_results_async(self):
        sparams = SearchParams("comme des garcons")
        res = asyncio.run(self.service.fetch_data_async(sparams.get_dict()))
        items = asyncio.run(self.service.parse_response_async(res))
        searchresults = SearchResults(items)
        self.logger.info(searchresults)

        # Assert that the count is greater than 0
        self.assertTrue(searchresults.count() > 0)

    def test_get_5_results(self):
        sparams = SearchParams("comme des garcons", item_count=5)
        searchresults = self.service.get_search_results(sparams.get_dict())

        # Assert that the count is 5
        self.assertEqual(searchresults.count(), 5)

    def test_get_5_results_async(self):
        sparams = SearchParams("comme des garcons", item_count=5)
        searchresults = asyncio.run(
            self.service.get_search_results_async(sparams.get_dict())
        )

        # Assert that the count is 5
        self.assertEqual(searchresults.count(), 5)

    def test_search_by_size(self):
        size_to_search = "XL"
        sparams = SearchParams("comme des garcons", size=size_to_search)
        searchresults = self.service.get_search_results(sparams.get_dict())

        # Loop through the items and assert the size is XL
        for i in range(searchresults.count()):
            self.logger.info(searchresults.get(i)["size"])
            self.assertTrue(size_to_search in searchresults.get(i)["size"])

    def test_search_by_size_async(self):
        size_to_search = "XL"
        sparams = SearchParams("comme des garcons", size=size_to_search)
        searchresults = asyncio.run(
            self.service.get_search_results_async(sparams.get_dict())
        )

        # Loop through the items and assert the size is XL
        for i in range(searchresults.count()):
            self.assertTrue(size_to_search in searchresults.get(i)["size"])

    def test_search_pagination(self):
        # search normal search
        sparams = SearchParams("comme des garcons", item_count=36)
        searchresults = asyncio.run(
            self.service.get_search_results_async(sparams.get_dict())
        )

        self.logger.info(searchresults)

        # search with pagination, page 2
        sparams = SearchParams("comme des garcons", item_count=36, page=2)
        searchresults_page2 = asyncio.run(
            self.service.get_search_results_async(sparams.get_dict())
        )

        self.logger.info(searchresults_page2)

        # assert page 2 results have something
        self.assertTrue(searchresults_page2.count() > 0)

        # assert different results
        self.assertNotEqual(searchresults.get(0), searchresults_page2.get(0))

    def test_search_empty_params(self):
        sparams = SearchParams("")
        print(sparams.get_dict())
        searchresults = asyncio.run(
            self.service.get_search_results_async(sparams.get_dict())
        )

        self.assertEqual(searchresults.count(), 10)

    def test_search_by_brand(self):
        sparams = SearchParams("junya watanabe", brands=["JUNYA WATANABE"])
        print(sparams.get_dict())
        searchresults = self.service.get_search_results(sparams.get_dict())
        print(searchresults.to_json())
        # Loop through the items and assert the brand is comme des garcons
        for i in range(searchresults.count()):
            self.logger.info(searchresults.get(i)["brand"])
            self.assertTrue("JUNYA WATANABE" in searchresults.get(i)["brand"])
