import asyncio
import unittest
import postalservice
import logging

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class PostalServiceTest(unittest.TestCase):
    def test_fetch_code_200(self):
        service = postalservice.MercariService()
        res = asyncio.run(service.fetch_data('comme des'))

        # Log the data
        logger.debug('Fetched data: %s', res)

        self.assertEqual(res.status_code, 200)


if __name__ == '__main__':
    unittest.main()