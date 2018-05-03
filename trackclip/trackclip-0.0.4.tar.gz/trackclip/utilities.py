def rect_vertices(xywh, integers):
    """
    p1 ----- p4
      |     |
    p2 ----- p3
    """
    if integers:
        xywh = map(lambda e: int(round(e)), xywh)

    x, y, w, h = xywh

    return (x, y), (x, y + h), (x + w, y + h), (x + w, y)