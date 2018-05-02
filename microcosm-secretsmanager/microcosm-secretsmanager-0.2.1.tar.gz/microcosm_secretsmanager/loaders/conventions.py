"""
Load configuration according to conventions:

Configuration is loaded from secretsmanager using the following rules:

 1. Loads the JSON file from `secrests/{env}/{service_name}`

 2. Use the version in MICROCOSM_CONFIG_VERSION

If the microcosm environment variables are not present, it skips loading secretsmanager


"""
from os import environ

from microcosm.loaders import load_from_dict

from microcosm_secretsmanager.loaders.base import SecretsManagerLoader


def load_from_secretmanager(environment=None):
    """
    Load the secrets into a dictionary, skip if no environment available

    """
    if environment is None:
        try:
            environment = environ["MICROCOSM_ENVIRONMENT"]
        except KeyError:
            # noop
            return load_from_dict(dict())

    return VersionedSecretsManagerLoader(environment)


class VersionedSecretsManagerLoader(SecretsManagerLoader):

    def __init__(self, environment):
        """
        Construct using KMS key based on environment name.

        """
        super(VersionedSecretsManagerLoader, self).__init__(
            environment,
        )

    def __call__(self, metadata):
        """
        Conditionally load configuration based on the MICROCOSM_SERVICE_VERSION environment variable.

        """
        version = environ.get("MICROCOSM_CONFIG_VERSION")

        if version is None:
            # skip AWS secretsmanager loading
            return {}

        return super(VersionedSecretsManagerLoader, self).__call__(
            metadata,
            version,
        )
