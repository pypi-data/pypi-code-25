from __future__ import absolute_import

import importlib.abc
from importlib.machinery import ModuleSpec
import logging
import types
import sys
import io
import json
import attr
from functools import partial
from devconfig.helper import URL, iterload
from devconfig import constructor
from devconfig import mapping

from credstash import getAllSecrets
import yaml

if sys.version_info.major == 3:
    unicode = str

_log = logging.getLogger(__name__)

def url_args_dict(args):
    args_dict = {}
    for k,v in args.items():
        args_dict[k] = v[0] if len(v) == 1 else v
    return args_dict

class CredstashModuleLoader(importlib.abc.Loader):
    def create_module(self, spec):
        return types.ModuleType(spec.name)

    def exec_module(self, module):
        origin = module.__spec__.origin
        _log.debug('Loading all secrets from {} into module {}'.format(origin, module))

        secrets = []
        for name, value in getAllSecrets(region=origin.hostname,
                                table=origin.path,
                                context=url_args_dict(origin.args),
                                ).items():
            _log.debug('{}'.format(name), extra=value if isinstance(value, dict) else {'value': value})
            secrets.append(io.StringIO(unicode('{}: {}'.format(name, value))))
        module.__dict__.update(mapping.merge(*iterload(*secrets, populate=constructor.populate_loader)))

@attr.s
class CredstashModuleFinder(importlib.abc.MetaPathFinder):
    table = attr.ib()
    region = attr.ib()
    key_id = attr.ib()
    context = attr.ib()
    module_name = attr.ib()
    region = attr.ib(default='default-region')

    def find_spec(self, fullname, path, target=None):
        if fullname != self.module_name:
            return
        module_url = URL('credstash://{}'.format(self.region))
        return ModuleSpec(fullname, CredstashModuleLoader(), origin=module_url(args=self.context, path=self.table, fragment=self.key_id))

def get_credstash_module_finder(table, region, key_id, module_name, **context):
    return CredstashModuleFinder(table=table, region=region, key_id=key_id, context=context, module_name=module_name)

def credstash_finder_memoize(table, region, key_id, **context):
    return partial(get_credstash_module_finder, table, region, key_id, **context)