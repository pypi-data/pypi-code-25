from pathlib import Path
from pelops import mypyyaml
import os


def read_config(config_filename='config.yaml'):
    config_file = Path(config_filename)
    if not config_file.is_file():
        raise FileNotFoundError("config file '{}' not found.".format(config_filename))

    with open(config_filename, 'r') as f:
        config = mypyyaml.load(f, Loader=mypyyaml.Loader)

    try:
        with open(os.path.expanduser(config["mqtt"]["mqtt-credentials"]), 'r') as f:
            credentials_mqtt = mypyyaml.load(f, Loader=mypyyaml.Loader)
    except KeyError:
        pass
    else:
        config["mqtt"].update(credentials_mqtt["mqtt"])

    try:
        with open(os.path.expanduser(config["influx"]["influx-credentials"]), 'r') as f:
            credentials_influx = mypyyaml.load(f, Loader=mypyyaml.Loader)
    except KeyError:
        pass
    else:
        config["influx"].update(credentials_influx["influx"])

    config = mypyyaml.dict_deepcopy_lowercase(config)
    return config