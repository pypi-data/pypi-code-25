import yaml


def parse_config(path: str) -> dict:
    """
    Parses the config from yaml
    :param path: path of the config file
    :return: config dict
    """
    with open(path) as stream:
        config_dict = yaml.load(stream)
        return config_dict


def get_class(kls: str) -> type:
    """
    Gets class by name and imports all modules needed
    :param kls:
    :return:
    """
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m
