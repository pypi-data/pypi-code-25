import json
from morpheus import module_loader


# loads possible game moves and executes them on the state
class GameMoves:
    def __init__(self):
        self.moves = {}
        self._load_moves()

    def execute_moves(self, game_state, params):
        err = []
        try:
            self._process_player_moves('player_1', game_state, params)
        except RuntimeError as error:
           err = error.args
        try:
            self._process_player_moves('player_2', game_state, params)
        except RuntimeError as error:
            if err:
                raise RuntimeError(err[0], err[1], error.args[0], error.args[1])
            raise RuntimeError(error.args[0], error.args[1])
        if err:
            raise RuntimeError(err[0], err[1])
        return game_state

    def _process_player_moves(self, player_tag, game_state, params):
        if isinstance(params[player_tag], list):
            for move in params[player_tag]:
                if isinstance(move, dict):
                    for move_name, move_data in move.items():
                        self._execute_move(game_state, move_name, move_data)
                else:
                    raise RuntimeError("Invalid move format. Move must be a dict.\n" + move, player_tag)
        else:
            raise RuntimeError("Moves must be stored in a list.\n" + params[player_tag], player_tag)

    def _execute_move(self, state, move_name, move_data):
        if move_name in self.moves.keys():
            self.moves[move_name].execute(state, move_data)
        else:
            raise RuntimeError('No such move ' + move_name, move_data[0])

    def _load_moves(self):
        loader = module_loader.ModuleLoader()
        moves_module = loader.folder_to_module('moves', 'moves')

        for name, move in loader.objects_from_module('_move', moves_module):
                self.moves[name] = move
