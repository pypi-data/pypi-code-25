from morpheus import module_loader


# loads possible game moves and executes them on the state
class GameProcesses:
    def __init__(self):
        self.processes = []
        self._load_processes()

    def process_state(self, game_state):
        for process in self.processes:
            process.execute(game_state)

        return game_state

    # private
    def _load_processes(self):
        loader = module_loader.ModuleLoader()
        process_mod = loader.folder_to_module('processes', 'processes')

        for _, process in loader.objects_from_module('_processes', process_mod):
                self.processes.append(process)

        self.processes = sorted(self.processes, key=lambda proc: proc.priority)
