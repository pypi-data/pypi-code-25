import yaml


# loads configuration files
class GameConfig:
    __instance = None

    def __init__(self):
        if GameConfig.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            with open('game_configuration.yaml', 'r') as stream:
                GameConfig.__instance = yaml.load(stream)['config']

    @staticmethod
    def instance():
        if GameConfig.__instance is None:
            GameConfig()

        return GameConfig.__instance

