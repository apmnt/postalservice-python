import asyncio
import unittest
import postalservice
import logging
from postalservice.utils import SearchResults, SearchParams

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("MERCARI TESTS %(levelname)s: %(message)s ")
handler.setFormatter(formatter)
logger.addHandler(handler)


class MercariServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.service = postalservice.MercariService()

    def test_fetch_code_200(self):

        sparams = SearchParams("comme des garcons")

        res = asyncio.run(self.service.fetch_data(sparams.get_dict()))

        # Log the data
        logger.info("Fetched data: %s", res)

        self.assertEqual(res.status_code, 200)

    def test_parse_results_positive_count(self):

        sparams = SearchParams("comme des garcons")

        res = asyncio.run(self.service.fetch_data(sparams.get_dict()))

        items = self.service.parse_response(res)
        searchresults = SearchResults(items)
        # Log the items
        logger.info(searchresults)

        # Log the length of the items
        logger.info("Length of items: %s", searchresults.count())

        self.assertTrue(searchresults.count() > 0)

    def test_search_by_size(self):
        size_to_search = "XL"
        sparams = SearchParams("comme des garcons", sizes=[size_to_search])

        res = asyncio.run(self.service.fetch_data(sparams.get_dict()))

        items = self.service.parse_response(res)
        searchresults = SearchResults(items)

        sizes = "Listing sizes:\n"
        for i in range(searchresults.count()):
            sizes += "Size: " + searchresults.get(i)["size"] + "\n"

        logger.info(sizes)

        # Loop through the items and assert the size is XL
        for i in range(searchresults.count()):
            assert size_to_search in searchresults.get(i)["size"]


if __name__ == "__main__":
    unittest.main()
