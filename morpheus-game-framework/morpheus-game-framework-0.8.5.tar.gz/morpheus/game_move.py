# executes a move on top of game state, handles potential errors caused by move
class GameMove:
    def execute(self, game_state, params):
        raise NotImplementedError

    def _invalid_move(self, reason):
        raise RuntimeError(reason)
