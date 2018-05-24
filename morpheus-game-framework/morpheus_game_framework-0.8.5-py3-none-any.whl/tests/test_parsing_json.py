import unittest
from morpheus import game_state, game_object


class ParsingGameState(unittest.TestCase):
    def setUp(self):
        self.game_state = game_state.GameState()

    def test_generating_json_from_state_containing_basic_data_types(self):
        self.game_state.hp = 100
        self.game_state.name = 'John'

        self.assertDictEqual(self.game_state.json(),
                             {'hp': 100, 'name': 'John'})

    def test_generating_json_from_state_with_composites_of_basic_types(self):
        self.game_state.units = ['archer', 'soldier', 'horseman']
        self.game_state.player_data = {'player1': {'hp': 100},
                                       'player2': {'hp': 60}}

        self.assertDictEqual(
            self.game_state.json(),
            {'units': ['archer', 'soldier', 'horseman'],
             'player_data': {
                 'player1': {'hp': 100},
                 'player2': {'hp': 60}
             }})

    def test_generating_json_from_state_with_basic_game_objects(self):
        player_1 = game_object.GameObject()
        player_1.hp = 100
        player_1.type = 'assassin'

        player_2 = game_object.GameObject()
        player_2.hp = 120
        player_2.type = 'warrior'

        self.game_state.player_1 = player_1
        self.game_state.player_2 = player_2

        self.assertDictEqual(
            self.game_state.json(),
            {'player_1': {'hp': 100, 'type': 'assassin'},
             'player_2': {'hp': 120, 'type': 'warrior'}})

    def test_generating_json_of_state_withcomposite_game_objects(self):
        p1 = game_object.GameObject()
        p1.hp = 200

        p2 = game_object.GameObject()
        p2.hp = 150

        nature = game_object.GameObject()
        nature.weather = 'sunny'

        economy = game_object.GameObject()
        economy.inflation = 2.0

        self.game_state.players = [p1, p2]
        self.game_state.world = {'nature': nature, 'economy': economy}

        self.assertDictEqual(
            self.game_state.json(),
            {'players': [{'hp': 200}, {'hp': 150}],
             'world': {'nature': {'weather': 'sunny'},
                       'economy': {'inflation': 2.0}}})

    def test_generating_json_of_nested_game_objects(self):
        player = game_object.GameObject()
        unit = game_object.GameObject()
        unit.hp = 100
        unit.type = 'archer'

        weapon = game_object.GameObject()
        weapon.damage = 60
        weapon.used = False

        unit.weapon = weapon
        unit.shield = None
        player.unit = unit

        self.game_state.player = player

        self.assertDictEqual(
            self.game_state.json(),
            {'player': {'unit': {'hp': 100, 'type': 'archer',
                                 'weapon': {'damage': 60,
                                            'used': False},
                                 'shield': None}}})
