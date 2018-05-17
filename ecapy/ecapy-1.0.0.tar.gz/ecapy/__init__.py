from ctypes import cdll,c_double,POINTER,c_int,CFUNCTYPE
from os import path

here = path.abspath(path.dirname(__file__))
lib_path = here + '/eca.so'


def eca(
    fobj,
    D,
    N = -1,
    K = 7,
    η_max = 2.0,
    P_bin = 0.02,
    P_exploit = 0.95,
    max_evals = -1,
    low_bound = -100.0,
    up_bound  =  100.0,
    minimize  = False):
    
    if N < 0:
        N = K*D

    if max_evals < 0:
        max_evals = 10000*D

    lib = cdll.LoadLibrary(lib_path)


    CMPFUNC = CFUNCTYPE(c_double, POINTER(c_double), c_int)

    f = lambda x, d: fobj(x[:d])

    fobj_c  = CMPFUNC(f)

    lib.eca.restype = POINTER(c_double)
    
    x = lib.eca(fobj_c,
                c_int(D),
                c_int(N),
                c_int(K),
                c_double(η_max),
                c_double(P_bin),
                c_double(P_exploit),
                c_int(max_evals),
                c_double(low_bound),
                c_double(up_bound),
                c_int(0 if minimize else 1),
                )

    return x[:D], x[D]
