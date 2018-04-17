from .dotdict import DotDict

def named_dict(l):
    """ Creates a DotDict from a list of items that have a ``name`` attribute

    Args:
        l (List[object]): list of objects that have a ``name`` or ``__name__`` attribute

    Returns:
        DotDict[str, object]: mapping of objects' names to objects

    Example:
        >>> import moldesign as mdt
        >>> m1 = mdt.from_name('benzene')
        >>> m2 = mdt.from_name('propane')
        >>> d = named_dict([m1, m2, DotDict])
        >>> list(d.keys())
        ['benzene', 'propane', 'DotDict']
        >>> d.propane
        <propane (Molecule), 11 atoms>
        >>> d.DotDict
        moldesign.utils.classes.DotDict
    """
    return DotDict((_namegetter(obj), obj) for obj in l)


def _namegetter(obj):
    try:
        return obj.name
    except AttributeError:
        return obj.__name__
