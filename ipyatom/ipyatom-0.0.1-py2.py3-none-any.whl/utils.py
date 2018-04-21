import numpy as np
import pandas as pd  # TODO remove pandas dependancy
from matplotlib.colors import to_hex as color_to_hex

from ipyatomica.utils import get_data_path
from ipyatomica import data


def slice_mask(points, vector, lbound=None, ubound=None, origin=(0, 0, 0), current=None):
    """compute mask for points within the lower and upper planes

    Properties
    ----------
    points : array((N,3))
    vector : array((3,))
        the vector normal to the slice planes
    ubound : None or float
        the fractional length (+/-) along the vector to create the upper slice plane
    lbound : None or float
        the fractional length (+/-) along the vector to create the lower slice plane
    origin : array((3,))
        the origin of the vector

    Examples
    --------
    >>> points = [[0,0,-5],[0,0,0],[0,0,5]]
    >>> slice_mask(points,[0,0,1],ubound=1)
    array([ True,  True, False], dtype=bool)

    >>> slice_mask(points,[0,0,1],lbound=1)
    array([False, False,  True], dtype=bool)

    >>> slice_mask(points,[0,0,1],lbound=-1,ubound=1)
    array([False,  True, False], dtype=bool)

    >>> slice_mask(points,[0,0,1],lbound=1,origin=[0,0,2])
    array([False, False,  True], dtype=bool)

    """
    if current is None:
        mask = np.array([True for _ in points])
    else:
        mask = np.array(current)

    if ubound is not None:
        cpoints = np.array(points) - np.array(origin) - np.array(vector) * ubound
        mask = mask & (np.einsum('j,ij->i', vector, cpoints) <= 0)
    if lbound is not None:
        cpoints = np.array(points) - np.array(origin) - np.array(vector) * lbound
        mask = mask & (np.einsum('j,ij->i', vector, cpoints) >= 0)

    return mask


def round_to_base(x, base=.1):
    """ round a number to a specified base

    Parameters
    ----------
    x: float
    base: float

    Returns
    -------
    rounded: float

    Examples
    --------
    >>> round_to_base(21, base=1)
    21.0
    >>> round_to_base(21, base=6)
    24.0
    >>> round_to_base(21, base=.8)
    20.8
    >>> round_to_base(1.1234567, base=1e-5)
    1.12346
    >>> round_to_base(1.1234567, base=0.06)
    1.14

    """
    return float(round(base * round(float(x)/base), len(str(round(1./base)))))


def fmt_scientific(value, pos=None, sfigs=3, min_exponent=2):
    r""" format values as scientific value $a \times 10^b

    Parameters
    ----------
    value: float
    pos:
        for use with matplotlib.ticker.FuncFormatter
    sfigs: int
        number of significat figures
    min_exponent:
        only use power notation if abs(b) >= min_exponent

    Returns
    -------
    value: str

    Examples
    --------
    >>> fmt_scientific(1.0, sfigs=3, min_exponent=2)
    '1.00'
    >>> fmt_scientific(0.123456, sfigs=3, min_exponent=2)
    '0.123'
    >>> fmt_scientific(0.123456, sfigs=3, min_exponent=1)
    '$1.23 \\times 10^{-1}$'
    >>> fmt_scientific(1.123456, sfigs=3, min_exponent=2)
    '1.12'
    >>> fmt_scientific(123456, sfigs=3, min_exponent=2)
    '$1.23 \\times 10^{5}$'
    >>> fmt_scientific(0.0000123456, sfigs=3, min_exponent=2)
    '$1.23 \\times 10^{-5}$'
    >>> fmt_scientific(0.0000123466, sfigs=4, min_exponent=2)
    '$1.235 \\times 10^{-5}$'

    """
    base, exponent = '{{:.{}e}}'.format(sfigs-1).format(value).split('e')
    if abs(int(exponent)) < min_exponent:
        base_len = 0 if str(value).split(".")[0] == "0" else len(str(value).split(".")[0])
        return '{{0:.{}f}}'.format(sfigs - base_len).format(float(value))
    else:
        return r'${{0:.{}f}} \times 10^{{{{{{1}}}}}}$'.format(sfigs-1).format(float(base), int(exponent))


def get_default_atom_map(rcovalent=True):
    """ get default atom map

    Parameters
    ----------
    rcovalent: bool
        if True, use covalent radii, else use van der Waal radii

    Returns
    -------

    """
    csv_path = get_data_path(data, "atom_data.csv")
    df = pd.read_csv(csv_path, comment="#")
    df = df.apply(pd.to_numeric, axis=0, errors='ignore')
    df.set_index('Symbol', inplace=True)
    df = df.rename(columns={"RCov" if rcovalent else "RVdW": "radius", "Number": "anum"})
    df["color_fill"] = df.apply(lambda row: color_to_hex((row.Red, row.Green, row.Blue)), axis=1)
    df["color_outline"] = None
    df["transparency"] = 1
    return df[["radius", "color_fill", "color_outline", "transparency", "anum"]].T.to_dict()
