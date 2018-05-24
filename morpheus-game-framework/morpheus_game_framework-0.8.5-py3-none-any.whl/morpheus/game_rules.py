from morpheus import module_loader


# loads possible game rules and checks them against the state
class GameRules:
    def __init__(self):
        self.rules = []
        self._load_processes()

    def process_state(self, game_state):
        for rule in self.rules:
            rule.validate_state(game_state)

        return game_state

    # private
    def _load_processes(self):
        loader = module_loader.ModuleLoader()
        rules_module = loader.folder_to_module('rules', 'rules')

        for _, rule in loader.objects_from_module('_rule', rules_module):
                self.rules.append(rule)
