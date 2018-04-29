import yaml


def load_config(conf_path):
    with open(conf_path, 'r') as f:
        config = yaml.load(f)

    return config
