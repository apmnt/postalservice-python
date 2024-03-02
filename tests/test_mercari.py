import unittest
import postalservice
from tests.baseservicetestclass import _BaseServiceTestClass

class MercariServiceTest(_BaseServiceTestClass, unittest.TestCase):
    def setUp(self) -> None:
        self.service = postalservice.MercariService()

if __name__ == "__main__":
    unittest.main()
