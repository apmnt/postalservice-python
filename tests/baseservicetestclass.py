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

    def test_parse_results(self):

        sparams = SearchParams("comme des garcons")
        res: httpx.Response = self.service.fetch_data(sparams.get_dict())
        print(res)
        items: str = self.service.parse_response(res)
        searchresults = SearchResults(items)
        self.logger.info(searchresults)

        # Assert that the count is greater than 0
        self.assertTrue(searchresults.count() > 0)

    def test_search_by_size(self):

        size_to_search = "XL"
        sparams = SearchParams("comme des garcons", size=size_to_search)
        searchresults = self.service.get_search_results(sparams.get_dict())

        # Loop through the items and assert the size is XL
        for i in range(searchresults.count()):
            print(searchresults.get(i)["size"])
            self.assertTrue(size_to_search in searchresults.get(i)["size"])

    def test_search_by_size_async(self):

        size_to_search = "XL"
        sparams = SearchParams("comme des garcons", size=size_to_search)
        searchresults = asyncio.run(self.service.get_search_results_async(sparams.get_dict()))

        # Loop through the items and assert the size is XL
        for i in range(searchresults.count()):
            self.assertTrue(size_to_search in searchresults.get(i)["size"])
