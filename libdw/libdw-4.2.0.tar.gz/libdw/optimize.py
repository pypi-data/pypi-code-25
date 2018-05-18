"""
Procedures for finding values of a function to optimize its output.
"""

import operator

def floatRange(lo, hi, stepsize):
    """
    :returns: a list of numbers, starting with ``lo``, and increasing
     by ``stepsize`` each time, until ``hi`` is equaled or exceeded.

    ``lo`` must be less than ``hi``; ``stepsize`` must be greater than 0.
    """
    result = []
    if stepsize == 0:
       print('Stepsize is 0 in floatRange')
       return result
    v = lo
    while v < hi:
        result.append(v)
        v += stepsize
    return result

def argopt(f, stuff, comp):
    """
    :param f: a function that takes a single argument of some type
     ``x`` and returns a value of some type ``y``
    :param stuff: a list of elements of type ``x``
    :param comp: a function that takes two arguments of type ``y`` and
     returns a Boolean;  it is intended to return ``True`` if the first
     argument is 'better' than the second.
    :returns: a pair ``(bestVal, bestArg)``, where ``bestArg`` is the
     element of ``stuff`` such that ``f(bestArg)`` is better, according
     to ``comp`` than ``f`` applied to any other element of ``stuff``, and
     ``bestVal`` is ``f(bestArg)``.
    
    The types ``x`` and ``y`` are not actual types;  they're just
    intended to show that the types of the functions have to match up
    in the right way.
    
    For example, get the team with the highest score, you might do
    something like

    ``argopt(seasonScore, ['ravens', 'crows', 'buzzards'], operator.gt)``

    where ``seasonScore`` is a function that takes the name of a team
    and returns a numerical score.
    """
    bestValSoFar = None
    bestArgSoFar = None
    for x in stuff:
        v = f(x)
        if bestValSoFar == None or comp(v, bestValSoFar):
            bestValSoFar = v
            bestArgSoFar = x
    return (bestValSoFar, bestArgSoFar)

def optOverLine(objective, xmin, xmax, numXsteps, 
               compare = operator.lt):
    """
    :param objective: a function that takes a single number as an
               argument and returns a value
    :param compare: a function from two values (of the type returned
               by ``objective``) to a Boolean;  should return ``True``
               if we like the first argument better.
    :returns: a pair, ``(objective(x), x)``.  ``x`` one of the numeric
               values achieved by starting at ``xmin`` and taking
               ``numXsteps`` equal-sized steps up to ``xmax``;  the
               particular value of ``x`` returned is the one for which
               ``objective(x)`` is best, according to the ``compare``
               operator. 
    """
    if type(numXsteps) != int:
        raise Exception('numXsteps should be an integer number of steps')
    return argopt(objective, floatRange(xmin, xmax, 
                                        (xmax - xmin) / float(numXsteps)),
                  compare)

def optOverGrid(objective, 
               xmin, xmax, numXsteps, 
               ymin, ymax, numYsteps, 
               compare = operator.lt):
    """
    Like ``optOverLine``, but ``objective`` is now a function from two
    numerical values, one chosen from the ``x`` range and one chosen
    from the ``y`` range.  It returns ``(objective(x, y), (x, y))`` for
    the optimizing pair ``(x,y)``.
    """
    ((score, y), x) = \
             optOverLine(lambda x: optOverLine(lambda y: objective(x, y),
                                               ymin, ymax, numYsteps,
                                               compare),
                         xmin, xmax, numXsteps,
                         lambda sv1,sv2:compare(sv1[0], sv2[0]))
    return (score, (x, y))
