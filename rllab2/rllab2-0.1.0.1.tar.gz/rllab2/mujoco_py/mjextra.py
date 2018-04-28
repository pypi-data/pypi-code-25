def append_objects(cur, extra):
    for i in xrange(cur.ngeom, cur.ngeom + extra.ngeom):
        cur.geoms[i] = extra.geoms[i - cur.ngeom]
    cur.ngeom = cur.ngeom + extra.ngeom
    if cur.ngeom > cur.maxgeom: 
        raise ValueError(u"buffer limit exceeded!")
