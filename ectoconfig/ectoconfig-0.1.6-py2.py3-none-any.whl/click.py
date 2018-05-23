"""Support for injecting loaded configuration into click."""

try:
    import click
except ImportError:
    click = None
    print("'click' not found!")
    print("please run `pip install ectoconfig[click]`")

import os
import sys
from .config import Config


def EctoConfigClickCommand(ecto_params=None):     # pragma: no coverage
    """
    Returns a click.Command that injects values from configuration as defaults.

    :param ecto_params: dict    - must contain a 'name' key
                                  can contain a 'path' or 'paths' key
                                  can contain a 'prefix' key
                                  can contain an 'also_append' key
    :returns ClassType          - instance of click.Command
    """

    if ecto_params is None:
        ecto_params = {'name': os.path.basename(sys.argv[0])}

    if not isinstance(ecto_params, dict):
        raise TypeError("must be of type dict")

    if 'name' not in ecto_params:
        raise KeyError("'name' key is missing")

    class ClickCommandWithEctoConfig(click.Command):
        """A click.Command that incjects EctoConfig variables as default values."""
        
        def invoke(self, ctx):
            """
            Overload the click.Command.invoke method.

            :param ctx: obj     - click context
            """
            c = Config(ecto_params['name'])

            if 'path' in ecto_params:
                c.add_config_path(ecto_params['path'])
            if 'paths' in ecto_params:
                [
                    c.add_config_path(p)
                    for p in ecto_params['paths']
                ]
            if 'prefix' in ecto_params:
                c.set_env_prefix(ecto_params['prefix'])

            config = c.read_in_config()

            for param, value in ctx.params.items():
                if value is None and param in config:
                    ctx.params[param] = config[param]

            if 'also_append' in ecto_params and ecto_params['also_append']:
                for param, value in config.items():
                    if param not in ctx.params:
                        ctx.params[param] = value

            return super(ClickCommandWithEctoConfig, self).invoke(ctx)
    
    return ClickCommandWithEctoConfig
