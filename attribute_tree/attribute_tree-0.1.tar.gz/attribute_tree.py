__version__ = '0.1'


def walk(tree):
    """ walks over tree structure

    Function walks over a tree structure yielding each (path, leaf) value

    Parameters
    ----------
    tree : dict, list, tuple
        tree-like structure to walk over

    Returns
    -------
    iterable
        pairs of each (path, leaf) values
    """
    def elements(item):
        if isinstance(item, (list, tuple)):
            for k, v in enumerate(item):
                yield k, v
        else:
            for k, v in item.items():
                yield k, v

    def impl(item, path):
        if isinstance(item, (list, tuple, dict)):
            for k, v in elements(item):
                for y in impl(v, path=path + (k, )):
                    yield y
        else:
            yield path, item
    return impl(tree, tuple())


class attribute_tree(dict):
    """ creates dict based tree-like structure

    Parameters
    ----------
    kwds : keywords
        passed to underlying dictionary
    """

    def __init__(self, **kwds):
        object.__setattr__(self, '__dict__', self)
        for name, value in kwds.items():
            setattr(self, name, value)

    def __setattr__(self, name, value):
        """ x.__setattr__(name, value) <===> x[name] = value

        Adds or changes attribure for a given `name` to `value`.
        If `value` is a dictionary it is changed to attribute_tree.
        If `value` is a collection (list or tuple) each nested
        dictonary is also changed to attribute_tree.

        Parameters
        ----------
        name: str
            name of the attribute
        value
            value of the attribute
        """
        def adapt(x):
            if isinstance(x, dict):
                return attribute_tree(**x)
            elif isinstance(x, (list, tuple)):
                return type(x)(adapt(y) for y in x)
            else:
                return x
        self[name] = adapt(value)

    def __getattr__(self, name):
        """ x.__getattr__(y) <===> x.y

        Returns attribute matching given `name`.
        If `name` is not present creates and returns nested attribute_tree.

        Parameters
        ----------
        name: str
            name of the attribure

        Returns
        -------
        any
            attribute if name present, nested attribute_tree otherwise

        """
        return self.setdefault(name, attribute_tree())

    def __lt__(self, rhs):
        """ checks if self is subset of rhs

        have same semantics like set.__lt__

        Parameters
        ----------
        rhs: attribute_tree
            superset tree

        Returns
        -------
        bool
            True if self is subset of rhs, False otherwise
        """
        return set(walk(self)) < set(walk(rhs))


def keys(tree):
    """ keys(x) <===> <dict>x.keys()

    allows access to underlying dict's keys method

    Parameters
    ----------
    tree: attribute_tree
        attribute_tree from which keys are returned
    """
    return super(attribute_tree, tree).keys()


def items(tree):
    """ items(x) <===> <dict>x.items()

    allows access to underlying dict's items method

    Parameters
    ----------
    tree: attribute_tree
        attribute_tree from which items are returned
    """
    return super(attribute_tree, tree).items()


def values(tree):
    """ values(x) <===> <dict>x.values()

    allows access to underlying dict's values method

    Parameters
    ----------
    tree: attribute_tree
        attribute_tree from which values are returned
    """
    return super(attribute_tree, tree).values()
