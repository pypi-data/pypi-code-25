import unittest
import yaml
from unittest.mock import patch, mock_open
from morpheus.game_config import GameConfig


class GameConfigSpecs(unittest.TestCase):
    def test_must_parse_yaml_correctly(self):
        m = mock_open()
        with patch('builtins.open',
                   mock_open(read_data=GameConfigSpecs._mock_config())) as m:
            self.assertEqual(GameConfig.instance()['player1']['hp'], 100)
            self.assertEqual(GameConfig.instance()['player2']['hp'], 60)

    @staticmethod
    def _mock_config():
        return yaml.dump(
            {'config': {'player1': {'hp': 100}, 'player2': {'hp': 60}}}
        )
