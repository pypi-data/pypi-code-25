# -*- coding: utf-8 -*-
"""create pauli spin matrices and
manipulate quantum entangled states
"""

import numpy as np
import copy
import itertools

__version__ = '2.1.0'

i = 1j
debug = False
sign = lambda a: '+' if a>0 else '-' if a<0 else '+'

base_reprs = {
    'ud':{'up':'u','down':'d'},
    '01':{'up':'0','down':'1'},
    'arrow':{'up':u'\u2191','down':u'\u2193'}
}

base_repr = base_reprs['ud']

def set_base_repr(arg):
    '''set the printout of the base representation:
    
    :param str arg: 'ud', '01', or 'arrow'
    '''
    global base_repr
    base_repr = base_reprs[arg]
    state.bases = {1:['|%s>'%base_repr[x] for x in ['up','down']]}
    state.base_reprs = arg

class state(object):
    # bases = {1:['|u>','|d>'],
    #          2:['|uu>','|ud>','|du>','|dd>']}
    
    bases = {1:['|%s>'%base_repr[x] for x in ['up','down']]}
    base_reprs = 'ud'
    
    def __init__(self,s, bra_flag = False):
        '''initialize with either a basis ket, or a wave function
        '''
        assert isinstance(s,(str,unicode,np.matrix,list))
        if isinstance(s,list):
            s = np.matrix(s)
        if isinstance(s,np.matrix):
            if s.dtype not in (float,complex):
                s = s.astype(float)
            self.n = n = s.size
            self.phi = np.matrix( np.ravel(s).reshape((n,1)) )
            self.n_particles = n_particles = int(np.log2(n))
        elif isinstance(s,(str,unicode)):
            self.n_particles = n_particles = len(s.lstrip('|').rstrip('>'))

        if n_particles not in self.bases:
            self.basis = create_basis(n_particles)
            self.bases[n_particles]=self.basis
        else:
            self.basis = self.bases[n_particles]

        if isinstance(s,(str,unicode)):
            if s.startswith('<') or s.endswith('|'):
                raise Exception,'%s not a ket'%s
            if not s.startswith('|'):
                s = '|'+s
            if not s.endswith('>'):
                s = s+'>'
            assert s in self.basis, '%s not in basis'%s
            k = self.basis.index(s)
            self.name = s
            self.n = len(self.basis)
            self.phi = np.matrix([0.]*self.n).T # the wave function
            self.phi[k] = 1.

        self.bra = False
        self.kind = 'ket'
        
        if bra_flag:
            self._bra()

    def _bra(self):
        '''convert ket to bra
        '''
        if self.bra:
            return
        self.phi = self.phi.H
        if hasattr(self,'name') and self.name in self.basis:
            self.name = '<'+self.name[1:-1]+'|'
        self.basis = ['<'+s[1:-1]+'|' for s in self.basis]
        self.bra = True
        self.kind = 'bra'
        return self
        
    def _ket(self):
        '''convert bra to ket
        '''
        if not self.bra:
            return
        self.phi = self.phi.H
        if hasattr(self,'name') and self.name in self.basis:
            self.name = '|'+self.name[1:-1]+'>'
        self.basis = ['|'+s[1:-1]+'>' for s in self.basis]
        self.bra = False
        self.kind = 'ket'
        return self
        
    def __unicode__(self):
        phi = self.phi
        first_one = True
        s = '0'
        for k in range(self.n):
            phi_k = phi.item(k)
            if phi_k != 0:
                
                if first_one:
                    s = ''
                    if isinstance(phi_k,(float,int)):
                        if phi_k == 1:
                            coef = ''
                        elif phi_k == -1:
                            coef = '- '
                        else:
                            coef = '%g '%phi_k
                    else: # complex
                        if phi_k.imag == 0:
                            if phi_k.real == 1:
                                coef = ''
                            elif phi_k.real == -1:
                                coef = '- '
                            else:
                                coef = '%g '%phi_k.real
                        elif phi_k.real == 0:
                            if phi_k.imag == 1:
                                coef = ' i '
                            else:
                                coef = '%g i '%phi_k.imag
                        else:
                            coef = '( %g %s %g i )'%(phi_k.real,sign(phi_k.imag),abs(phi_k.imag))
                    first_one = False
                    
                else:
                    if isinstance(phi_k,(float,int)):
                        if phi_k == 1:
                            coef = '+ '
                        elif phi_k == -1:
                            coef = '- '
                        else:
                            coef = '%s %g '%(sign(phi_k),abs(phi_k))
                    else: # complex
                        if phi_k.imag == 0:
                            if phi_k.real == 1:
                                coef = ' + '
                            elif phi_k.real == -1:
                                coef = ' - '
                            else:
                                coef = '%s %g '%(sign(phi_k.real),abs(phi_k.real))
                        elif phi_k.real == 0:
                            if phi_k.imag == 1:
                                coef = ' + i '
                            elif phi_k.imag == -1:
                                coef = ' - i '
                            else:
                                coef = '%s %g i '%(sign(phi_k.imag),abs(phi_k.imag))
                        else:
                            coef = '+ ( %g %s %g i )'%(phi_k.real,sign(phi_k.imag),abs(phi_k.imag))

                s += '%s%s '%(coef, self.basis[k])
        return s
    
    def __repr__(self):
        return self.__unicode__().encode('utf-8')
    
    def __add__(self,another):
        """|a> + |b>
        """
        assert isinstance(another,self.__class__)
        assert self.bra == another.bra
        return self.__class__(self.phi + another.phi, bra_flag = self.bra)

    def __sub__(self,another):
        """|a> - |b>
        """
        assert isinstance(another,self.__class__)
        assert self.bra == another.bra
        return self.__class__(self.phi - another.phi)
    
    def __mul__(self,another):
        """
        inner product: <a|b>
        operation on bra: <a|A
        scalar product: <a| alpha or <a| alpha
        outer product: |a><b|
        """
        if debug: print ('state.__mul__')
        assert isinstance(another,(int,float,complex,self.__class__,operator,str))
        if isinstance(another,self.__class__): # either inner or outer product
            if self.bra: # <a|b>
                assert not another.bra,'cannot multiply two bras'
                r = (self.phi*another.phi).item(0)
                if isinstance(r,complex):
                    if r.imag == 0:
                        r = r.real
                return r
            else: # |a><b|
                assert another.bra,'cannot multiply two kets'
                return operator(self.phi*another.phi)
        elif isinstance(another,operator): #  <a|A
            assert self.bra
            phi = (self.phi * another.op).T
            return bra(phi)
        elif isinstance(another,str): # '<a|'*A
            another = self.__class__(another)
            return self*another
        elif isinstance(another,(int,float,complex)):
            if self.bra:
                r = bra(self.phi*another) #  <a| alpha
            else:
                r = ket(self.phi*another) #  |a> alpha
            return r

    def __rmul__(self,num):
        """scalar product alpha |a> or alpha <a|
        """
        if debug: print ('state_base.__rmul__')
        assert isinstance(num,(int,float,complex))
        if self.bra:
            r = bra(self.phi*num) #  <a| alpha
        else:
            r = ket(self.phi*num) #  |a> alpha
        return r

    def __div__(self,other):
        """scalar product |a> / alpha
        If both arguments are states, this is a test of "divides", returning (True/False,byfactor)
        """
        if isinstance(other,state): # check if one state is a multiple of another
            return self.divides(other)
        assert isinstance(other,(int,float,complex))
        r = self.copy()
        r.phi = self.phi/other
        return r

    def divides(self,other):
        assert isinstance(other,state)
        a = self.phi.flat
        b = other.phi.flat
        q = None
        l = []
        for aa,bb in zip(a,b):
            if aa == 0 and bb == 0:
                l.append(True)
            elif bb == 0:
                l.append(False)
            else:
                f = aa/bb
                if q is None:
                    q = f
                l.append(q == f)
        r = np.array(l).all()
        if r:
            return(r,q)
        else:
            return(r,None)
    
    def __truediv__(self,num):
        """scalar product |a> / alpha
        """
        assert isinstance(num,(int,float,complex))
        if self.bra:
            r = bra(self.phi/num) #  <a| alpha
        else:
            r = ket(self.phi/num) #  |a> alpha
        return r

    def __neg__(self):
        return (-1)*self #   - |a>
    
    def __getattr__(self,dot_op):
        '''Unitary operators:
        x.H - Hermetian Transpose
        x.N - Normalize
        '''
        if dot_op == 'H':
            if self.bra:
                return self.copy()._ket()
            return self.copy()._bra()
        if dot_op == 'N':
            return self.normalized()
        else:
            raise AttributeError(self.__repr__(),' object has no attribute ',dot_op)
    
    def __pow__(self,other):
        '''kroneker product
        '''
        return self.kron(other)
    
    def __eq__(self,other):
        assert isinstance(other,self.__class__)
        assert self.bra == other.bra
        return (self.phi == other.phi).all()
    
    def copy(self):
        """deep copy of self
        """
        return copy.deepcopy(self)
    
    def normalize(self):
        """normalizes the wave function
        """
        if self.bra:
            norm = (self.phi*self.phi.H).item(0)
        else:
            norm = (self.phi.H*self.phi).item(0)
        self.phi /= np.sqrt(norm)
    
    def normalized(self):
        """returns the normalized version
        """
        if self.bra:
            norm = (self.phi*self.phi.H).item(0)
        else:
            norm = (self.phi.H*self.phi).item(0)
        return self/np.sqrt(norm)
    
    def density(self):
        """generate the density matrix
        """
        return (self*self.H).op
    
    def _index(self):
        '''makes an index from string representations of basis states to
        interger offset within the state vector
        '''
        s1 = ['u','d']
        s = copy.copy(s1)
        for k in range(self.n_particles-1):
            s = [x+y for x,y in list(itertools.product(s,s1))]
        
        d = dict(zip(s,range(self.n)))
        return d
    
    def density1(self,particle_no=None):
        '''generate the density matrix for one
        of the particles, :var:`particle_no`
        Particle numbers are 0...n_particles-1
        '''
        if particle_no == None: # old style call
            return (self.density1(0),self.density1(1))
        assert particle_no < self.n_particles
        d = self._index()
        p = particle_no
        pstr = '_'
        rho = self.density()
        s1 = ['u','d']
        keys = sorted(d.keys())[::-1] # 'uuu','uud',...
        f = set([key[:p]+pstr+key[p+1:] for key in keys]) # 'u_u','u_d'...
        ind_keys_u,ind_keys_d = [[ff.replace(pstr,s) for ff in f] for s in s1] # [['uuu','uud'...],['udu','udd'...]]
        rho_p = np.matrix(np.zeros((2,2)))
        for z in zip(ind_keys_u,ind_keys_d):
            ind2x2 = [[(z0,z1) for z0 in z] for z1 in z] # [[('dud', 'dud'), ('ddd', 'dud')], [('dud', 'ddd'), ('ddd', 'ddd')]]
            for i in range(2):
                for j in range(2):
                    ii,jj = ind2x2[i][j]
                    rho_p[i,j] += rho[ d[ii],d[jj] ]
        return rho_p

    def correlation(self):
        '''compute the correlation matrix
        '''
        n_particles = self.n_particles
        u = ket([1,0])
        d = ket([0,1])
        Sz = u*u.H - d*d.H
        S0 = u*u.H + d*d.H # operator(np.identity(2))
        c = np.zeros((n_particles, n_particles))
        A = []
        for p1 in range(n_particles):
            Ap = (Sz if p1==0 else S0)
            for p2 in range(1,n_particles):
                Ap = Ap**(Sz if p2==p1 else S0)
            A.append(Ap)
        for i in range(n_particles):
            for j in range(n_particles):
                c[i,j] = (A[i]*self).H*(A[j]*self)
        return c

    def prob(self,A,s):
        """determine the probability of this state being in
        state s after the measurement A
        
        :param operator A:
        :param state s:
        """
        return np.abs(s.H*A*self)**2

    def kron(self,another):
        assert isinstance(another,self.__class__)
        assert self.bra == another.bra
        r = state([0.]*self.n*another.n,self.bra)
        r.phi = np.kron(self.phi,another.phi)
        return r

    def entangled(self):
        '''determine if a 2-particle pure state is entangled.
        This works only for n=2 particle states.
        '''
        assert self.n_particles == 2
        S = entropy(ptrace(self.density(),[0]))
        if np.isclose(S,0.):
            return False
        else:
            return True

class operator(object):
    ops = ['s0','sx','sy','sz']
    sig_0 = np.matrix([[1,0],[0,1]])
    sig_x = np.matrix([[0,1],[1,0]])
    sig_y = np.matrix([[0,-i],[i,0]])
    sig_z = np.matrix([[1,0],[0,-1]])
    op_mats = [sig_0,sig_x,sig_y,sig_z]

    @property
    def matrix(self):
        '''returns the matrix part of the operator object
        '''
        return self.op
    
    def __init__(self, A):
        '''initialize given a square, Hermetian matrix A
        '''
        assert isinstance(A,(str,np.matrix))
        if isinstance(A,str):
            assert A in self.ops
            self.name = A
            k = self.ops.index(A)
            self.op = A = self.__class__.op_mats[k]
        n,m = A.shape
        assert n == m
        self.op = A
        n_particles = int(np.log2(n))
        self.basis = create_basis(n_particles)
        w,v = np.linalg.eig(A)
        self.basis = [v[:,k] for k in range(n)]
        self.observables = list(w)

    def __repr__(self):
        return str(self.op)
    
    def __mul__(self,another):
        """
        multiplication on the left: operator*another
        scalar multiplication: A*alpha
        operation on ket: A |a>
        operator x operator: A*B
        operator x matrix: A*sig
        operator x string (basis state ket): A*'|u>'
        """
        if debug: print ('%r.__mul__(%r)'%(self.__class__,type(another)))
        assert isinstance(another,(str,state,self.__class__,np.matrix,int,float,complex))
        if isinstance(another,(int,float,complex)): # alpha A
            return self.__class__(self.op*another)
        elif isinstance(another,state): # A |a>
            assert not another.bra
            return state(self.op*another.phi)
        elif isinstance(another,self.__class__):  # A*B
            return self.__class__(self.op*another.op)
        elif isinstance(another,np.matrix): # assume this operator*density_matrix
            return self.__class__(self.op*another)
        elif isinstance(another,str): # convert the string to a basis state
            return self*ket(another)

    def __rmul__(self,another):
        """
        multiplication on the right: another*operator
        scalar multiply : A*alpha
        by bra: <a| A
        by matrix: sig*A
        by string (basis state bra): '<a|'*A
        """
        if debug: print ('%r.__rmul__(%r)'%(self.__class__,type(another)))
        assert isinstance(another,(str,state,np.matrix,int,float,complex))
        if isinstance(another,(int,float,complex)):
            return self.__class__(self.op*another) #  A*alpha
        elif isinstance(another,state):
            return bra(another.phi*self.op) # <a| A
        elif isinstance(another,np.matrix):
            return self.__class__(another*self.op) # sig*A
        elif isinstance(another,str):
            return bra(another)*self # convert the string to a basis state
    
    def __add__(self,another):
        """ A+B
        """
        assert isinstance(another,self.__class__)
        return self.__class__(self.op+another.op) # A + B
    
    def __sub__(self,another):
        """ A-B
        """
        assert isinstance(another,self.__class__)
        return self.__class__(self.op-another.op) #  A - B
    
    def __div__(self,num):
        """
        divide by a scalar A/alpha
        """
        assert isinstance(num,(int,float,complex))
        return self.__class__(self.op/num)
        
    def __truediv__(self,num):
        """
        divide by a scalar A/alpha
        """
        assert isinstance(num,(int,float,complex))
        return self.__class__(self.op/num)
        
    def __neg__(self): # -A
        """
        scalar negation -A
        """
        return (-1)*self

    def __eq__(self,other):
        assert isinstance(other,self.__class__)
        return (self.op == other.op).all()
    
    def __pow__(self,other):
        return self.kron(other)
    
    def kron(self,other):
        assert isinstance(other,self.__class__)
        return self.__class__(np.kron(self.op,other.op))
    
    def measure(self,s):
        '''produce the measurement using operator as an observable.
        This produces a single number equal to one of the eigenvalues lambda_i
        of A according to a probability distribution || < e_i | phi > ||^2 and
        collapses the wave function.
        Returns (observed value, collaped state)
        '''
        s = ket(s)
        n = s.n
        assert n == self.op.shape[0]
        E = np.block(self.basis)
        c = np.array(E.H*s.phi)
        c = [c.item(k) for k in range(n)]
        P = [np.abs(x)**2 for x in c]
        k = np.random.choice( range(n), p=P)
        lam = self.observables[k]
        #print('lam = %r'%lam)
        k_set = np.where(np.isclose(self.observables,lam*np.ones(n)))[0] # repeated eigenvalues
        #print('k_set = %r'%k_set)
        ss = ket([0]*n)
        for k in k_set:
            #print('c[k] = %r'%c[k])
            ss += c[k]*ket(self.basis[k])
        ss.normalize()
        return(lam,ss)
    
    def average(self,s):
        '''caluclate the average value of the observable for a given state
        '''
        return bra(s)*self*ket(s)
    
    def eig(self):
        '''calcluate the eigenvalues and eigenvectors of the operator.
        Returns (list of eigenvalues, list of eigenvectors)
        '''
        ev,evec = np.linalg.eig(self.matrix)
        evec = [ket(x) for x in evec.T]
        return ev,evec
    
def ket(s):
    """generate a state vector given the state as a string or a wave function
    or generate the ket version of a bra vector
    """
    assert isinstance(s,(str,unicode,np.matrix,list,state))
    if isinstance(s,(str,unicode)):
        if s.startswith('<') and s.endswith('|'):
            s = '|'+s[1:-1]+'>' # turn it into a ket string
        return state(s)
    elif isinstance(s,(np.matrix,list)):
        return state(s)
    elif isinstance(s,state):
        if not s.bra:
            return s
        return s.copy()._ket()
    raise Exception('%r is not a valid state'%s)

def bra(s):
    """generate a state vector given the state as a string or wave function
    or generate the bra version of a ket vector
    """
    assert isinstance(s,(str,np.matrix,list,state))
    if isinstance(s,str):
        s = ket(s)
        return bra(s)
    elif isinstance(s,(np.matrix,list)):
        return bra( ket(s) )
    elif isinstance(s,state):
        if s.bra:
            return s
        return s.copy()._bra()
    else:
        raise Exception('% is not a valid state'%s)

def create_basis(n):
    '''create a basis set for n particles
    '''
    #s1 = ['u','d']
    s1 = [base_repr['up'],base_repr['down']]
    s = copy.copy(s1)
    for k in range(n-1):
        s = [x+y for x,y in list(itertools.product(s,s1))]
    s = ['|'+x+'>' for x in s]
    return s

def entropy(rho,frac=False,decohere=False):
    """calculate the Von Neumann entropy given the density matrix
    S = sum(p log(p)) where p are the density matrix eigenvalues
    If frac=True, return S/S_max where S_max = log(n) the max entropy.
    If decohere=True then assume decoherent population (off-diagonal elements are zero)
    """
    if decohere:
        w = np.diag(rho)
    else:
        w,v = np.linalg.eig(rho)
    n = w.size
    S = 0
    for k in range(n):
        if w[k] > 0 and not np.isclose(w[k],1.0):
            S -= w[k]*np.log(w[k])
    if frac:
        S_max = np.log(float(n))
        return S/S_max
    else:
        return S

def set_printoptions(**karg):
    '''feed print options to numpy.
    help(numpy.set_printoptions) for more info
    Typical use case:
    
    .. code-block python
        >>> set_printoptions(precisionn=3,suppress=True)
    
    to set the print precision to 3 digits after the decimal point and
    suppress scientific notation
    '''
    np.set_printoptions(**karg)

def _mosh(s1,s2,ps):
    '''mosh string 1 with string 2 putting string 2 characters in posisions ps
    '''
    n = len(s1) + len(s2)
    psk = [ x for x in range(n) if x not in ps ]
    s = np.array(['']*n)
    s[ps] = list(s2)
    s[psk] = list(s1)
    return ''.join(list(s))

def ptrace(rho,ps):
    '''generate the density matrix with specified particles traced out.
    
    :param np.matrix rho: the multi-particle density matrix
    :param list ps: list of particles to trace out; given by number 0,1...n_particles
    
    If the list is empty, return the full density matrix.
    If the list has all the particles, then returns the trace of the full density matrix (always = 1)
    The list must have unique particle numbers which are all < n_particles
    '''
    if len(ps) == 0: return s
    n_particles = int(np.log2(rho.shape[0]))
    n = n_particles
    assert np.array([x < n for x in ps]).all(),'all elements of ps %r must be < number of particles %r'%(ps,[x < n for x in ps])
    assert np.unique(ps).size == len(ps),'elements of ps must be unique: %r'%ps
    ps = sorted(ps)
    nr = 2**len(ps)
    nk = 2**(n - len(ps))
    n = 2**n
    if nk == 1: return 1.
    d,dr,dk = [state([1]*x)._index() for x in [n,nr,nk]]
    di,dri,dki = [sorted(x.keys(),reverse=True) for x in [d,dr,dk]]
    Ms = [ [[ (_mosh(x,z,ps),_mosh(y,z,ps)) for x in dki] for y in dki] for z in dri]
    Msv =  [[[rho[ d[x], d[y] ] for (x,y) in row ] for row in mat ] for mat in Ms ]
    den = np.sum( [ np.array(x) for x in Msv], axis=0 )
    return np.matrix(den)

def Cab(rho):
    '''calculate the 'concurrence' of a two particle system.
    ref: Coffman, V., Kundu, J., & Wootters, W. K. (2000).
    Distributed Entanglement. Physical Review A, 61(5), 5–9.
    http://doi.org/10.1103/PhysRevA.61.052306
    
    :param np.matrix rho:
    
    Presently this only calculates on a two particle system (4x4 density matrix)
    '''
    assert rho.shape == (4,4)
    sy = operator('sy')
    rho_tilde = ((sy**sy)*(rho.conj())*(sy**sy)).op
    lam = np.linalg.eig(rho*rho_tilde)[0].real
    lam = np.clip(lam,0,np.inf)
    lam = np.sqrt(np.sort(lam))[::-1]
    cab = np.max([lam[0]-lam[1]-lam[2]-lam[3],0])
    return cab
    
#====================== Tests =======================
import sys
# https://stackoverflow.com/questions/5067604/determine-function-name-from-within-that-function-without-using-traceback
# for current func name, specify 0 or no argument.
# for name of caller of current func, specify 1.
# for name of caller of caller of current func, specify 2. etc.
currentFuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name

bling = '-'*60
blin2 = '-'*30

def head():
    print ('<%s> %s'%(currentFuncName(1),bling))

def tail():
    print ('<%s> %s PASSED %s'%(currentFuncName(1),blin2,blin2))
    
def test1():
    head()
    uuu = ket('|uuu>')
    print ('%r has %d particles'%(uuu,uuu.n_particles))
    print (uuu)
    tail()
    
def test2():
    head()
    a = ket('|ud>') + ket('|du>')
    print (a)
    b = a.H
    print (b)
    a.normalize()
    print (a)
    print (a.H)
    tail()

def test3():
    head()
    c = bra('<uuduud|')
    print ('*'*60)
    print (c.basis)
    print ('*'*60)
    print (c.bases)
    print ('*'*60)
    tail()

def test4():
    global u,d,A,r,l
    head()
    u = state([1,0])
    d = state([0,1])
    A = u*u.H - d*d.H
    r = (u+d).normalized()
    l = (u-d).normalized()
    A*r
    print (A*r)/l
    assert A*r == l
    tail()

def test5():
    head()
    u = state('|u>')
    d = state('|d>')
    sz = u*u.H - d*d.H
    s0 = u*u.H + d*d.H
    sz1 = sz**s0
    sz2 = s0**sz
    s = u**(u+d).normalized()
    sz1.measure(s)
    sz2.measure(s)
    
    uu = u**u
    ud = u**d
    du = d**u
    dd = d**d
    s = (uu+ud).normalized()
    sz1.measure(s) # (+1,uu+ud)
    sz2.measure(s) # { (+1,uu) or (-1,ud) }
    s = (du+dd).normalized()
    sz1.measure(s) # (-1,du+dd)
    sz2.measure(s) # { (+1,uu) or (-1,dd) }
    
    s = uu + dd
    s.normalize()
    (sz**s0).measure(s) # { (+1,uu} or {-1,dd})}
    s = (u+d)**(u+d)
    s.normalize()
    (sz**s0).measure(s) # { (+1,uu+ud ) or (-1,du+dd) }

    tail()

def test6():
    head()
    u = ket([1,0])
    d = ket([0,1])
    s = (u**d - d**u).N
    Sz = u*u.H - d*d.H
    S0 = u*u.H + d*d.H
    s = ket(list(np.random.normal(size=(8)))).N
    c = s.correlation()
    print c
    P = [s.prob(Sz**S0**S0,ket(x)) for x in s.basis]
    print np.sum(P)
    s1 = (u**d - 0*d**u).N**(u**d + d**u).N
    s2 = (0*u**d - d**u).N**(u**d + d**u).N
    rho = 0.5*s1.density() + 0.5*s2.density()
    print rho
    tail()
    
def all_tests():
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
    test_spin()
    test_entangled()
    test_ptrace()
    test_readme()

s0 = operator('s0')
sx = operator('sx')
sy = operator('sy')
sz = operator('sz')
u = state('|u>')
d = state('|d>')

uu = u**u
ud = u**d
du = d**u
dd = d**d
# singlet state
s = (ud - du).N
# triplet states
t1 = uu
t2 = (ud + du).N
t3 = dd

# spin of an electron
sx_e = sx/2.
sy_e = sy/2.
sz_e = sz/2.
spinx = (sx_e**s0) + (s0**sx_e)
spiny = (sy_e**s0) + (s0**sy_e)
spinz = (sz_e**s0) + (s0**sz_e)
spinx2 = spinx*spinx
spiny2 = spiny*spiny
spinz2 = spinz*spinz
spin2 = spinx2 + spiny2 + spinz2

def test_spin():
    """ calculate the spin of an electron and pairs of electrons
    """
    head()
    print ('spin of the electron along z axis is 1/2:')
    print (u.H*sz_e*u)
    print ('magnitude of the spin is sqrt(3)/2:')
    print ('  quantum number is J=1/2 so')
    print ('  spin = sqrt( J*(J+1) ) = sqrt( (1/2)*(3/2) ) = 0.866')
    print (np.sqrt( u.H*(sx_e*sx_e + sy_e*sy_e + sz_e*sz_e)*u ))
    print ('magnitude of spin of the singlet state is zero:')
    print (np.sqrt( s.H*spin2*s ))
    print ('magnitudes of spins of the triplet states are sqrt(2):')
    print ('  quantum number of paired triplet state is J=1 so')
    print ('  spin = sqrt( J*(J+1) ) = sqrt(2) = 1.414')
    print (np.sqrt( t1.H*spin2*t1 ))
    print (np.sqrt( t2.H*spin2*t2 ))
    print (np.sqrt( t3.H*spin2*t3 ))
    print ('spins of triplet states projected onto z axis:')
    print ('  these are the m quantum nummbers and should be +1, 0, -1')
    print (t1.H*spinz*t1)
    print (t2.H*spinz*t2)
    print (t3.H*spinz*t3)
    tail()
    
def test_entangled(s = s):
    """ the argument can be any mixed state of two particles.
    the singlet state is the default argument.
    """
    head()
    print ('(perhaps) entangled state:')
    print (s)
    print ('Alice and Bob:')
    print (s.density())
    print ("Alice's view:")
    rhoA = ptrace(s.density(),[1])
    rhoB = ptrace(s.density(),[0])
    #rhoA,rhoB = s.density1()
    print (rhoA)
    print ("Bob's view:")
    print (rhoB)
    print ("entropy of Alices's view")
    S = entropy(rhoA)
    S_frac = entropy(rhoA,frac=True)
    print ('S = %.3f which is %.1f%% of max entropy'%(S,S_frac*100))
    print ("entropy of Bob's view")
    S = entropy(rhoB)
    S_frac = entropy(rhoB,frac=True)
    print ('S = %.3f which is %.1f%% of max entropy'%(S,S_frac*100))
    print ('tests for entanglement')
    rho = s.density()
    rhoA = s.density1(0)
    print ('density matrix trace test:')
    print ('trace(rho_Alice^2) =',np.trace(rhoA*rhoA))
    print ('(if it is < 1, the particles are entangled)')
    print ('correlation tests <AB> - <A><B>')
    cor = []
    scor = []
    for a,sa in zip([sx,sy,sz],['x','y','z']):
        cor_row = []
        scor_row = []
        for b,sb in zip([sx,sy,sz],['x','y','z']):
            scor_row.append('c'+sa+sb)
            sigma = (a**s0) # measures first particle without affecting 2nd
            tau = (s0**b) # measures second particle without affecting first
            c = s.H*(sigma*tau)*s - (s.H*sigma*s)*(s.H*tau*s)
            cor_row.append(c)
        scor.append(scor_row)
        cor.append(cor_row)
    cor = np.matrix(cor).real
    scor = np.matrix(scor)
    print ('correlation ')
    print (scor)
    print (cor)
    #         
    # cxx = s.H*((sx**s0)*(s0**sx))*s - (s.H*((sx**s0))*s)*(s.H*((s0**sx))*s)
    # cyy = s.H*((sy**s0)*(s0**sy))*s - (s.H*((sy**s0))*s)*(s.H*((s0**sy))*s)
    # czz = s.H*((sz**s0)*(s0**sz))*s - (s.H*((sz**s0))*s)*(s.H*((s0**sz))*s)
    # print 'correlation x,y,z = ',cxx,cyy,czz
    print ('(if any correlation != 0, the particles are entangled)')
    tail()

def test_ptrace():
    head()
    s = u**d - d**u
    s = (s**s).N
    den = ptrace(s.density(),[1,3])
    den = ptrace(s.density(),[])
    den = ptrace(s.density(),range(s.n_particles))
    tail()

def test_readme():
    # from the README.rst
    print 'Spin states'
    #from qspin2 import bra,ket,u,d,s0,sx,sy,sz
    u = ket('|u>')
    d = ket('|d>')
    print(u)
    print(d)
    print(u+d)
    i=1j
    print(u+i*d)
    print 'Operators'
    print(sx)
    print(sy)
    print(sz)
    print(sz*u)
    print(sz*d)
    print(u.H*sz*u)
    print(u)
    print(u.phi)
    print 'eigenvalues and eigenvectors'
    #import numpy as np
    print(sz)
    ev,evec = np.linalg.eig(sz.matrix)
    print(ev)
    print(evec)
    print(sx) # spin x
    ev, evec = np.linalg.eig(sx.matrix)
    print(ev)
    print(evec)
    ev, evec = sx.eig()
    print(ev)
    print(evec)
    print 'conditional probabilities'
    l = (u+d).N
    print(np.abs(bra(l)*ket(u))**2)
    print(np.abs(l.H*u)**2)
    print(l.prob(sz,u))
    print 'string representation of stste'
    set_base_repr('01')
    u = ket('0')
    d = ket('1')
    s = (u**d - d**u).N
    print(s)
    set_base_repr('arrow')
    u = ket(u'\u2193')
    d = ket(u'\u2191')
    s = (u**d-d**u).N
    print(s)
    set_base_repr('ud')
    u = ket('u')
    d = ket('d')
    
    print 'partial trace'
    s = (u**d - d**u).N
    rho = s.density()
    rhoA = ptrace(rho,[1])
    print(rhoA)
    
    print 'entanglement'
    #from qspin2 import ket
    u = ket('u')
    d = ket('d')
    s = (u**d - d**u).N
    print(s.entangled())
