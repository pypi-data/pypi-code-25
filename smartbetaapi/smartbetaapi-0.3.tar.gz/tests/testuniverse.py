import unittest
from smartbeta_api.universe import Universe
from smartbeta_api.apiservice import APIService


class TestUniverse(unittest.TestCase):

    def setUp(self):
        self.api_service = APIService('https://smart-beta.intramundi.com/api', 'C:/Users/Mfricaudet/ca-bundle.crt')
        self.uni = Universe(api_service=self.api_service, entity_ids=[1, 2])

    def test_entity_ids(self):
        self.setUp()
        self.assertEqual(self.uni.entity_ids, [1, 2])


if __name__ == '__main__':
    unittest.main()
