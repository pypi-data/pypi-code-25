from os import environ

from microcosm.loaders import load_from_dict


class VersionedSecretsManagerLoader:
    pass


def load_from_secretmanager(environment=None):
    if environment is None:
        try:
            environment = environ["MICROCOSM_ENVIRONMENT"]
        except KeyError:
            # noop
            return load_from_dict(dict())

    return VersionedSecretsManagerLoader(environment)
