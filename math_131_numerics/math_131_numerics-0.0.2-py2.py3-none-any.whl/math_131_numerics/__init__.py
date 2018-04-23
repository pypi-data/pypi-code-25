'''Package including standard numerical methods taught in numerics class at UC
Merced. Ths includes includes bisection method, fixed-point, Newton's, Secant,
Lagrange interpolant, Numerical differentiation, Trapezoid rule, Simpsons's
rule, Euler's, Taylor's, Runge-Kutta and Adams methods'''

__version__='0.0.2'
def bisection_method(f, a, b, tol, N):
    '''
    Solve root-finding problem using bisection method
    
    paragraph with more detail
    Hypothesis ``f(a) * f(b) < 0``
    
    Parameters
    ==========
    f : function
        continuous function 
    a : real number
        lower bound for search interval
    b : real number
        upper bound for search interval
    tol : real number
        tolerance error
    N : integer
        maximum number of iterations
    
    Returns
    =======
    tuple (x, err, k) where x is the root, err the absolute error, k the number of iterations
    return (None, None, k+1) if not enough iterations for expected tolerence error
    
    '''
    err = (b-a)/2
    k = 0
    while err >= tol and k <= N:
        x = (b+a)/2
        if f(x) == 0:
            print('done !')
            return x, err, k
        if f(a) * f(x) < 0:
            b = x
        if f(x) * f(b) < 0:
            a = x
        err = (b-a)/2
        
        if err < tol or f(x) == 0:
            print('Convergence in', k, 'steps')
            return x, err, k
        k = k+1
        
    if k == N+1:
        print('No convergence, need more iterations')
        return None, None, k
