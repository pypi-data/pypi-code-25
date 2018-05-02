"""Load and dump databases to disk."""


def load(source, classes):
    """Load 0 or more objects from source and instantiate them with the classes
    found in the classes iterable. They will be returned as a list which can be
    passed to session.add_all for example. No saving will be performed. Pass a
    dictionary as source with name: list-of-dictionaries as pairs."""
    objects = []  # All the created objects.
    classes = {x.__name__: x for x in classes}
    for name, data in source.items():
        cls = classes[name]
        for datum in data:
            # Let's load.
            objects.append(cls(**datum))
    return objects


def dump(objects, f, convert_name=None):
    """Return a dictionary suitable for loading with the load function. Objects
    will be dumped with the f function. If convert_name is given it must be a
    callable which takes a class name as the only argument, and returns a
    suitable alternative name. This is primarily useful for quick convertions
    in the context of database migrations and the like."""
    d = {}
    for obj in objects:
        name = obj.__class__.__name__
        if convert_name is not None:
            name = convert_name(name)
        d[name] = d.get(name, [])
        d[name].append(f(obj))
    return d


__all__ = ['load', 'dump']
