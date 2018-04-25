import yaml
import os

def update(d, ud, overwrite=True):
    for key, value in ud.items():
        if key not in d:
            d[key] = value
        elif isinstance(value, dict):
            update(d[key], value, overwrite=overwrite)
        elif isinstance(value, list) and isinstance(d[key], list):
            d[key] += value
        else:
            if key in d and not overwrite:
                return
            d[key] = value

def load_includes(config, include_path):
    if isinstance(config, dict):
        d = {}

        def load_include(key='$include'):
            value = config[key]
            path = os.path.abspath(os.path.join(os.path.dirname(include_path[-1]), value))
            if path in include_path:
                raise ValueError("Recursive import of {} (path: {})"\
                    .format(path, '->'\
                    .join(['"{}"'\
                    .format(s) for s in include_path])))
            nd = load_config(path, include_path=include_path+[path])
            if nd:
                update(d, nd)

        if '$include' in config:
            load_include('$include')
        for key, value in config.items():
            if key == '$include':
                continue
            result = load_includes(value, include_path=include_path)
            if key in d and isinstance(d[key], dict):
                update(d[key], result)
            else:
                d[key] = result
        if '$include-after' in config:
            load_include('$include-after')
        return d
    elif isinstance(config, list):
        return [load_includes(i, include_path=include_path) for i in config]
    return config
            

def load_config(filename, include_path=None):
    if include_path is None:
        include_path = [os.path.abspath(filename)]
    with open(filename) as input_file:
        config = yaml.load(input_file.read())
    return load_includes(config, include_path=include_path)
