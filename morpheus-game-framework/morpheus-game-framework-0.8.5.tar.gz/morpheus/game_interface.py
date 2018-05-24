from . import game_state
from . import game_moves
from . import game_processes
from . import game_rules

class GameInterface:
    def __init__(self, players, wrapper):
        self.players = players
        self.game_state = game_state.GameState()
        self.wrapper = wrapper

        self.game_moves = game_moves.GameMoves()
        self.game_processes = game_processes.GameProcesses()
        self.game_rules = game_rules.GameRules()

        self.game_flow = []
        self.error = {'timeout': {'player_1': False, 'player_2': False},
                      'stack': {'player_1': None, 'player_2': None}
                      }

    def set_up(self):
        pass

    def process_turn(self, responses):
        pass

    def step_simulation(self):
        pass

    def player_timeout(self, player):
        self.error['timeout'][player] = True

    def add_stack_trace(self, player, trace):
        self.error['stack'][player] = trace

    def store_state(self):
        self.game_flow.append(self.game_state.json())

    def append_error_handling(self):
        self.game_flow.append(self.error)
