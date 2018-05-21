from importlib import import_module


def get_class(class_fqn):
    """Returns the class given its fully qualified name

    :param class_fqn: a string representing a class' fully qualified name (module.class)
    :return: the class
    """
    parts = class_fqn.rsplit('.', 1)
    return getattr(import_module(parts[0]), parts[1])
