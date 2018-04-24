import grew
import network

def _compute_next(rs,todo):
    next = set()
    for g in todo:
        sucs_g = grew.run(rs,g)
        if sucs_g != [g]:
            next |= set(sucs_g)
    return next

#latex is_terminating
def is_terminating(rs,gr):
    def loop(todo, seen):
        next = _compute_next(rs, todo)
        return next == set() or (not next.intersection(seen) and
                                    loop(next, seen.union(next)))
    return loop(set([gr]), set([gr]))
#/latex

