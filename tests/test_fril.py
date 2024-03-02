import unittest
import postalservice
from tests.baseservicetestclass import _BaseServiceTestClass

class FrilServiceTest(_BaseServiceTestClass, unittest.TestCase):
    def setUp(self) -> None:
        self.service = postalservice.FrilService()

if __name__ == "__main__":
    unittest.main()
