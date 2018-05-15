"""A module that can build instances of plant components into a valide aide_draw yaml"""
from aide_render.builder_classes import DP, Component
from .yaml import yaml
from time import strftime
import os

def extract_types(instance: object, collect_types: list, recurse_types: list) -> dict:
    """Take in an instance of a class and recursively extract all specified types from the class's attributes to
    construct a dict.

    Parameters
    ----------
    instance
        The instance that will be filtered.
    collect_types
        The instance types
    recurse_types
        The instance types on which to recurse.



    """
    d_prime = {}

    class_dict = dict(vars(instance.__class__))
    try:
        instance_dict = dict(vars(instance))
    except TypeError:
        instance_dict = instance

    d = {}

    if class_dict:
        d.update(class_dict)
    if instance_dict:
        d.update(instance_dict)

    if d:
        for name, var in d.items():
            for t in collect_types:
                if isinstance(var, t):
                    d_prime[name] = var
                    break
            for t in recurse_types:
                if isinstance(var, t):
                    d_prime[name] = extract_types(var, collect_types, recurse_types)
                    break
    return d_prime


def render_design(component_instance: Component, folder_path, filename = None, stream=None):
    """Build the YAML as necessary to construct the Fusion model.

    Parameters
    ----------

    Examples
    --------

    >>> from .builder_classes import HP, DP, Component
    >>> from aide_design.play import u
    >>> from .templates.lfom import LFOM
    >>> my_lfom = LFOM(HP(20,u.L/u.s))
    >>> render_design(my_lfom, "./test_output")

    Now there should be a design_<date>.yaml design file that represents the component model.
    """

    if not filename:
        filename = "design_" + strftime("%Y_%m_%d_%H_%M_%S") + ".yaml"

    dp_dict = extract_types(component_instance, [DP], [Component])

    file_path = os.path.join(os.path.abspath(folder_path), filename)
    with open(file_path, mode = 'x') as file:
        yaml.dump(dp_dict, stream=file)


