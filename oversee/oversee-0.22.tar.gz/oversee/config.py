import os

import yaml


path = os.path.join(os.path.expanduser('~'), '.oversee.yaml')
with open(path) as f:
    oversee = yaml.load(f)

install = oversee.get('install', {})


def get_aliases(name):
    return oversee.get('{}_aliases'.format(name))


aliases = {}
for key in oversee.get('aliases', {}):
    aliases[key] = oversee['aliases'].get(key)

jetbrains = oversee.get('jetbrains', {})
environments = oversee.get('environments', {})
gitignore = oversee.get('gitignore', {})
