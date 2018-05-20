import abc
import importlib
from typing import Callable, Optional, Union


class AbstractSettings(metaclass=abc.ABCMeta):
    debug: Optional[bool] = None
    use_reloader: Optional[bool] = None
    host: Optional[str] = None
    port: Optional[int] = None
    router: Union[str, Callable] = 'mountapi.routing.AbstractRouter'
    runner: Union[str, Callable] = 'mountapi.runners.AbstractRunner'
    schema: Union[str, Callable] = 'mountapi.schema.AbstractSchema'

    @classmethod
    def init_resource(cls, setting_name: str, **kwargs) -> None:
        setting = getattr(cls, setting_name)
        mod_name, resource_name = setting.rsplit('.', 1)
        mod = importlib.import_module(mod_name)
        resource = getattr(mod, resource_name)
        setattr(cls, setting_name, resource(**kwargs))


class DefaultSettings(AbstractSettings):
    debug = True
    use_reloader = True
    host = 'localhost'
    port = 8080
    router = 'mountapi.routing.Router'
    runner = 'mountapi.runners.AsyncRunner'
    schema = 'mountapi.schema.Schema'
