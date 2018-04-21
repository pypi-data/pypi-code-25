import copy
from ipyatomica.visualise import process_vstruct
from ipyatomica.visualise.repeat_cell import _repeat_repeat_cell, _translate_to_repeat_cell, _cslice_repeat_cell
from ipyatomica.visualise.repeat_density import _repeat_repeat_density, _translate_to_repeat_density, \
    _cslice_repeat_density, _resize_repeat_density


def add_repeat(vstruct, repeats=(0, 0, 0)):
    """repeat all elements by their local centre and cell vectors
    vector : ['a','b','c']
    rep : int
    recentre: bool
        if True, move centre by 0.5 * rep * vector
    """
    vstruct['transforms'].append({
        'type': 'local_repeat',
        'repeats': repeats})


def add_translate_to(vstruct, centre=(0., 0., 0.)):
    """translate all elements to new centre coordinate
    centre : (x,y,z)
    """
    vstruct['transforms'].append({
        'type': 'translate_to',
        'centre': centre})


def add_align(vstruct, vector='a', direction=(1, 0, 0)):
    """align all elements (locally) in a cartesian direction
    vector : ['a','b','c']
    direction : (x,y,z)
    """
    vstruct['transforms'].append({
        'type': 'local_align',
        'cvector': vector,
        'direction': direction})


def add_resize(vstruct, sfraction=1.):
    """resize data array
    for example array of shape (16,16,16) with sfraction 0.5
    -> shape (8,8,8)

    sfraction : float
        resize data by fraction
    """
    vstruct['transforms'].append({
        'type': 'resize',
        'sfraction': sfraction})


def add_slice(vstruct, normal=(1, 0, 0), lbound=None, ubound=None, centre=None):
    """slice all elements
    norma : array((3,))
        the vector normal to the slice planes
    ubound : None or float
        the fractional length (+/-) along the vector to create the upper slice plane
        if None, no upper bound
    lbound : None or float
        the fractional length (+/-) along the vector to create the lower slice plane
        if None, no lower bound
    origin : array((3,))
        the origin of the vector,
        if None, use local centre
    """
    vstruct['transforms'].append({
        'type': 'slice',
        'normal': normal,
        'lbound': lbound,
        'ubound': ubound,
        'centre': centre})


def apply_transforms(vstruct):
    """

    Parameters
    ----------
    vstruct: dict

    Returns
    -------
    newstruct: dict

    """
    tfuncs = {
        'repeat_cell': {
            'local_repeat': _repeat_repeat_cell,
            'translate_to': _translate_to_repeat_cell,
            # 'local_align': _align_repeat_cell,
            'slice': _cslice_repeat_cell
        },
        # 'repeat_poly': {
        #     'local_repeat': _repeat_repeat_poly,
        #     'recentre': _recentre_repeat_poly,
        #     'local_align': _align_repeat_poly,
        #     'slice': _cslice_repeat_poly
        # },
        'repeat_density': {
            'local_repeat': _repeat_repeat_density,
            'translate_to': _translate_to_repeat_density,
            'slice': _cslice_repeat_density,
            'resize': _resize_repeat_density,
        }
    }

    new_struct = process_vstruct(vstruct, deepcopy=True)

    gtransforms = new_struct.pop('transforms')
    new_struct['transforms'] = []

    for e in new_struct['elements']:

        # apply global transforms
        for trans in gtransforms:
            trans = copy.deepcopy(trans)
            ttype = trans.pop('type')
            tset = tfuncs[e['type']]
            if ttype not in tset:
                raise ValueError(
                    'a {0} transform is not available for {1}'.format(ttype, e['type']))
            tset[ttype](e, **trans)

        # apply local transforms
        ltransforms = e.pop('transforms')
        e['transforms'] = []
        for trans in ltransforms:
            trans = copy.deepcopy(trans)
            ttype = trans.pop('type')
            tset = tfuncs[e['type']]
            if ttype not in tset:
                raise ValueError(
                    'a {0} transform is not available for {1}'.format(ttype, e['type']))
            tset[ttype](e, **trans)

    return new_struct
