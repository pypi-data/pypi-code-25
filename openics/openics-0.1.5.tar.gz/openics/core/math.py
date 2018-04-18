import numpy as np


def distance(p0, p1, mode='euclid'):
    x0, x1 = p0[0], p1[0]
    y0, y1 = p0[1], p1[1]

    formula = {
        'euclid': np.sqrt(np.power(x0-x1, 2) + np.power(y0-y1, 2)),
        'city_block': np.abs(x0-x1) + np.abs(y0-y1),
    }

    if mode not in formula:
        mode = 'euclid'

    return formula[mode].astype(np.float)


def centroid(points):
    px, py = 0, 0
    num_points = len(points)
    for p in points:
        p = p[0]
        px += p[0]
        py += p[1]
    centroid = (
        int(px/num_points),
        int(py/num_points)
    )

    return centroid
