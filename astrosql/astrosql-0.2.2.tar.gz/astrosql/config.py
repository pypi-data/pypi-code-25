import yaml
from pathlib import Path


def load(filepath):
    if filepath.is_file():
        with filepath.open() as ymlfile:
            file = yaml.safe_load(ymlfile)
            return file
    else:
        raise FileNotFoundError("{} not found".format(filepath))


def get_config():
    config_file = Path.home()/'.astrosql'/'config.yml'
    config = load(config_file)
    if 'forward' in config:
        config_file = Path(config['forward'])
        # if config_file.is_absolute():
        config = load(config_file)
        # else:
        #     config = load(Path(__file__).parent/config_file)
    return config
