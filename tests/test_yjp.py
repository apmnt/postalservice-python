import unittest
import postalservice
from tests.baseservicetestclass import _BaseServiceTestClass

class YJPServiceTest(_BaseServiceTestClass, unittest.TestCase):
    def setUp(self) -> None:
        self.service = postalservice.YJPService()

if __name__ == "__main__":
    unittest.main()
