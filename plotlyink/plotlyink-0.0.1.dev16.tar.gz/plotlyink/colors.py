import logging
import colorlover as cl
from itertools import cycle
import math

logger = logging.getLogger(__name__)


class ScaleNotFound(Exception):
    def __init__(self, scale, ncolors):
        msg = "colors: '{}' ncolors: {}.".format(scale, ncolors)
        super().__init__(msg)


def perceived_brightness(rgb_color):
    """Compute perceived brightness.

    cf http://www.nbdtech.com/Blog/archive/2008/04/27/Calculating-the-Perceived-Brightness-of-a-Color.aspx
    Args:
        rgb_color (str): example 'rgb(215,200,80)'
    """
    rgb_color = rgb_color[4:-1]
    r, g, b = [int(i) for i in rgb_color.split(',')]
    return math.sqrt(r**2 * 0.241 + g**2 * 0.691 + b**2 * 0.068)


def filter_on_brightness(scale, brightness_thresh=220):
    """Filter a list of rgb on brightness."""
    id_to_keep = []
    for i, c in enumerate(scale):
        if perceived_brightness(c) < brightness_thresh:
            id_to_keep.append(i)
    return [scale[i] for i in id_to_keep]


def find_scale(scale, ncolors):
    """Check if is valid scale for ncolors asked."""
    colors = None
    for scale_type in cl.scales[str(ncolors)]:
        for scale_code in cl.scales[str(ncolors)][scale_type]:
            if scale == scale_code.lower().strip():
                return cl.scales[str(ncolors)][scale_type][scale_code]

    raise ScaleNotFound(scale, ncolors)


def to_plotly_colors_dict(keys, colors='spectral', ncolors=9, filter_brightness=True):
    """From colorlover scale name to plotly colors dict."""
    if isinstance(colors, str):
        colors = colors.lower().strip()

        try:
            colors = find_scale(colors, ncolors)
        except ScaleNotFound as e:
            logger.debug(e)
            raise NotImplementedError

    else:
        raise NotImplementedError

    if filter_brightness:
        colors = filter_on_brightness(colors)

    itercolors = cycle(colors)

    colors_dict = {}
    for k in keys:
        colors_dict[k] = next(itercolors)

    return colors_dict


def to_rgba(color, alpha):
    """
    Converts from rgb to rgba

    Parameters:
    -----------
            color : string
                    Color representation on hex or rgb
            alpha : float
                    Value from 0 to 1.0 that represents the alpha value.

    Example:
            to_rgba('rgb(23,23,23)',.5)
    """
    color = color.lower().strip()
    if 'rgba' in color:
        cl = list(eval(color.replace('rgba', '')))
        if alpha:
            cl[3] = alpha
        return 'rgba' + str(tuple(cl))
    elif 'rgb' in color:
        r, g, b = eval(color.replace('rgb', ''))
        return 'rgba' + str((r, g, b, alpha))
    else:
        raise ValueError("TODO")
