from pathlib import Path
from pelops import mypyyaml
import os


def read_config(config_filename = 'config.yaml'):
    config_file = Path(config_filename)
    if not config_file.is_file():
        raise FileNotFoundError("config file '{}' not found.".format(config_filename))

    config = mypyyaml.load(open(config_filename, 'r'), Loader=mypyyaml.Loader)
    credentials = mypyyaml.load(open(os.path.expanduser(config["mqtt"]["mqtt-credentials"]), 'r'),
                                Loader=mypyyaml.Loader)
    config["mqtt"].update(credentials["mqtt"])
    config = mypyyaml.dict_deepcopy_lowercase(config)
    return config