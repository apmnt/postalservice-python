import asyncio
import unittest
import postalservice
import logging
from postalservice.utils import SearchResults

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class MercariServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.service = postalservice.MercariService()

    def test_fetch_code_200(self):
        res = asyncio.run(self.service.fetch_data('comme des'))

        # Log the data
        logger.debug('Fetched data: %s', res)

        self.assertEqual(res.status_code, 200)


    def test_parse_results_positive_count(self):
        res = asyncio.run(self.service.fetch_data('comme des'))
        items = self.service.parse_response(res)
        searchresults = SearchResults(items)
        # Log the items
        logger.debug(searchresults)

        # Log the length of the items
        logger.debug('Length of items: %s', searchresults.count())

        self.assertTrue(searchresults.count() > 0)
        

if __name__ == '__main__':
    unittest.main()