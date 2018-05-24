import unittest

from morpheus import game_object

class TestGameObject(unittest.TestCase):
    def setUp(self):
        self.game_object=game_object.GameObject()

    def test_setting_item(self):
        self.game_object['pussese']=4
        self.assertEqual(self.game_object['pussese'], 4)