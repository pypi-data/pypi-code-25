from pubcontrol.config import Config
from pubcontrol.plugin import PluginManager
import pluggy


PROJECT_NAME = Config().NAME
hookspec = pluggy.HookspecMarker(PROJECT_NAME)
hookimpl = pluggy.HookimplMarker(PROJECT_NAME)


@hookspec
def fetch(register):
    return []


@hookspec
def process(register):
    return []


@hookspec
def model_module():
    pass


@hookspec
def register_models():
    pass


@hookspec
def install():
    pass


PluginManager().add_module(__name__)