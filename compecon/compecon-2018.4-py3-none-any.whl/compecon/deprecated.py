""" Deprecated:
This file contain useful code tha has been deprecated, just in case I realize I did something wrong in the newer version.
"""

import numpy as np
from numpy.linalg import solve
from .tools import jacobian
from warnings import warn

SQEPS = np.sqrt(np.spacing(1))




class MCPold(object):
    def __init__(self, F, a, b, *args,
                 transform='ssmooth',
                 maxit=100, maxsteps=10,
                 tol=SQEPS, showiters=False):

        a, b = np.atleast_1d(a, b)
        self.a, self.b = a.astype(float), b.astype(float)
        self.ainf = np.isinf(a)
        self.binf = np.isinf(b)


        self.opts = {'transform': transform, 'maxit': maxit, 'maxsteps': maxsteps, 'tol': tol, 'showiters': showiters}

        if callable(F):
            ftmp = F(a, *args)
            if not isinstance(ftmp, tuple):
                self.f = lambda x: (F(x, *args), jacobian(F, x, *args))
            else:
                self.f = lambda x: F(x, *args)
            self.islinear = False
        elif isinstance(F, np.ndarray):
            if len(args) == 1:
                self.q = q = args[0]
                self.f = lambda x: (F.dot(x) + q, F)
                self.islinear = True
            else:
                raise ValueError('If problem is linear, exactly one argument (vector q) must be provided after the bounds')
        else:
            raise ValueError('First argument to MCP must be either a function (nonlinear problem) or a numpy array (linear problem')

    def ssmooth(self, x, jac=False):

        x = np.atleast_1d(x)
        ainf, binf = self.ainf, self.binf
        AINF, BINF = ainf.all(), binf.all()
        Ainf, Binf = ainf.any(), binf.any()


        da, db = self.a - x, self.b - x

        if jac:
            fx, J = self.original(x, True)
            I = -np.identity(x.size)
            J = np.atleast_2d(J)

            # apply the Fischer + transform
            if AINF:
                fplus, Jplus = fx, J
            else:
                fplus, Jplus = fischer(fx, da, J, I)
                if Ainf:
                    fplus[ainf], Jplus[:, ainf] = fx[ainf], J[:, ainf]

            # apply the Fischer - transform
            if BINF:
                fhat, Jhat = fplus, Jplus
            else:
                fhat, Jhat = fischer(fplus, db, Jplus, I, False)
                if Binf:
                    fhat[binf], Jhat[:, binf] = fplus[binf], Jplus[:, binf]
            return fhat, Jhat
        else:
            fx = self.original(x, False)
            # apply the Fischer + transform
            if AINF:
                fplus = fx
            else:
                fplus = fischer(fx, da)
                if Ainf:
                    fplus[ainf] = fx[ainf]

            # apply the Fischer - transform
            if BINF:
                fhat = fplus
            else:
                fhat = fischer(fplus, db, plus=False)
                if Binf:
                    fhat[binf] = fplus[binf]
            return fhat




    def ssmooth(self, x, jac=False):

        x = np.atleast_1d(x)
        ainf, binf = self.ainf, self.binf
        da, db = self.a - x, self.b - x

        fx, J = self.f(x)

        if jac:
            I = -np.identity(x.size)
            J = np.atleast_2d(J)
            fplus, Jplus = fischer(fx, da, J, I)
            fplus[ainf], Jplus[:, ainf] = fx[ainf], J[:, ainf]

            fhat, Jhat = fischer(fplus, db, Jplus, I, False)
            fhat[binf], Jhat[:, binf] = fplus[binf], Jplus[:, binf]
            return fhat, Jhat
        else:
            fplus = fischer(fx, da)   # apply fischer plus
            fplus[ainf] = fx[ainf]

            fhat = fischer(fplus, db, plus=False)
            fhat[binf] = fplus[binf]
            return fhat

    def minmax(self, x, jac=False):

        a, b = self.a, self.b
        x = np.atleast_1d(x)
        da, db = a - x, b - x

        fx, J = self.f(x)
        fhat = np.minimum(np.maximum(fx, da), db)

        if jac:
            J = np.atleast_2d(J)
            Jhat = -np.identity(x.size)
            i = (fx > da) & (fx < db)
            Jhat[i] = J[i]
            return fhat, Jhat
        else:
            return fhat


    def solve(self, x0=None, **kwargs):


        OPTS = self.opts.copy()
        for k, v in kwargs.items():
            if k in OPTS.keys():
                OPTS[k] = v
            else:
                print('Unknown option {}. Valid options are'.format(k), OPTS.keys())

        a, b = self.a, self.b
        Transform = self.ssmooth if OPTS['transform'].lower() == 'ssmooth' else self.minmax

        if x0 is None:
            x = self.q if self.islinear else (a + b) / 2
        else:
            x = np.atleast_1d(x0).astype(np.float64)

        if OPTS['showiters']:
            print('{:4}  {:4}  {:6}'.format('it', 'bstep', 'change'))

        for it in range(OPTS['maxit']):
            fx, J = Transform(x, True)
            fnorm = np.max(np.abs(fx))
            if fnorm < OPTS['tol']:
                break

            dx = - solve(J, fx)
            fnormold = np.inf

            for backstep in range(OPTS['maxsteps']):
                xnew = x + dx
                fxnew = Transform(xnew)
                fnormnew = np.max(np.abs(fxnew))
                if fnormnew < fnorm:
                    break
                if fnormold < fnormnew:
                    dx *= 2
                    break
                fnormold = fnormnew
                dx /= 2

            x += dx
            if OPTS['showiters']:
                print('{:4}  {:4}  {:6.2e}'.format(it, backstep, fnormnew))


        if (it + 1) == OPTS['maxit']:
            print('Failure to converge in MCP.zero after {} iterations, using the {} transformation'.format(it+1,OPTS['transform']))

        x = np.minimum(np.maximum(a, np.real(x)), b)
        return x, fx

''' fixpoint should be included as a method to NLP class'''
def fixpoint(g, x, *args, maxit=100, tol=SQEPS, showiters=False):
    if showiters:
        print('{:^6}  {:^9}\n{}'.format('iter', 'dx', '-' * 18))

    for it in range(maxit):
        xnew = g(x, *args)
        dx = np.linalg.norm(xnew - x)
        if showiters:
            print('{:^6}   {:^9.3e}'.format(it, dx))

        if dx < tol:
            return xnew
        else:
            x = xnew.copy()

    print('Failure to converge in fixpoint, dx = {:.3e}'.format(dx))
    return xnew


