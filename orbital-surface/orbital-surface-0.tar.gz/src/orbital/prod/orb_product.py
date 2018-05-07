'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jul 8, 2016
@author: Niels Lubbes


The main functionality of this module is accessed via the method orb_product()
'''

import warnings

from orbital.class_orb_tools import OrbTools

from orbital.prod.class_orb_input import OrbInput
from orbital.prod.class_orb_output import OrbOutput

from orbital.class_orb_ring import OrbRing

from orbital.prod.orb_matrices import get_pmat

from orbital.sage_interface import sage_PolynomialRing
from orbital.sage_interface import sage_QQ
from orbital.sage_interface import sage_GF
from orbital.sage_interface import sage_var
from orbital.sage_interface import sage__eval
from orbital.sage_interface import sage_matrix
from orbital.sage_interface import sage_vector
from orbital.sage_interface import sage_ideal
from orbital.sage_interface import sage_maple
from orbital.sage_interface import sage_magma
from orbital.sage_interface import sage_diff
from orbital.sage_interface import sage_gcd

from linear_series.class_linear_series import LinearSeries
from linear_series.class_poly_ring import PolyRing


def get_emb_dim( imp_lst ):
    '''
    Computes the embedding dimension.
    
    Parameters
    ----------
    imp_lst : list<OrbRing.R>
        A list of homogeneous polynomials in QQ[x0,...,x8]
        representing a variety S in the projective 7-sphere S^7.
    
    Returns
    -------
    int
        The minimal number n so that S is contained in S^n.
        Thus so that S is not contained in a hyperplane section of S^n.    
    '''
    dim = 7
    for imp in imp_lst:
        if imp.total_degree() == 1:
            dim = dim - 1
    return dim


def get_deg_dim( imp_lst ):
    '''
    Parameters
    ----------
    imp_lst : list<OrbRing.R>
        A list of homogenous polynomials in QQ[x0,...,x8]
        representing a variety S in projective 8-space P^8.
    
    Returns
    -------
    int[]
        A 2-tuple of integers consisting of
        the degree and the dimension of the variety S.
    '''
    # consider ideal in ring of the right dimension.
    R = sage_PolynomialRing( sage_QQ, sage_var( 'y0,y1,y2,y3,y4,y5,y6,y7,y8' ), order = 'degrevlex' )
    I = R.ideal( sage__eval( str( imp_lst ).replace( 'x', 'y' ), R.gens_dict() ) )

    # compute Hilbert polynomial: (deg/dim!)*t^dim + ...
    hpol = I.hilbert_polynomial()

    dim = hpol.degree()

    deg = hpol
    for i in range( dim ):
        deg = deg.diff()

    OrbTools.p( 'hpol =', hpol, ' (deg, dim)=', ( deg, dim ) )

    return deg, dim


def get_project( pol_lst, pmat ):
    '''
    Parameters
    ----------
    pol_lst : list<OrbRing.R> 
        A list of homogeneous polynomials in QQ[x0,...,x8].
    
    pmat : sage_matrix    
        A matrix defined over the rationals QQ.    
    
    Returns
    -------
    tuple
        A 2-tuple of polynomials:        
        * a homogeneous polynomial F in QQ[x0,x1,x2,x3].             
        * F(1,x,y,z) in QQ[x,y,z] (affine polynomial)
    '''

    Ry = sage_PolynomialRing( sage_GF( 2 ), sage_var( 'y0,y1,y2,y3,y4,y5,y6,y7,y8' ), order = 'degrevlex' )
    v = OrbRing.coerce( '[v0,v1,v2,v3,v4,v5,v6,v7,v8]' )
    x = OrbRing.coerce( '[x0,x1,x2,x3,x4,x5,x6,x7,x8]' )
    vx_dct = {v[i]:x[i] for i in range( 9 )}

    OrbTools.p( "\n" + str( pmat ) )

    tries = 0
    projected = False
    while not projected:

        # obtain the linear equations of the projection map
        pmat = sage_matrix( OrbRing.R, list( pmat ) )
        leq_lst = list( pmat * sage_vector( x ) )

        # compute the image of this projection map
        proj_lst = [ v[i] - leq_lst[i] for i in range( len( leq_lst ) ) ]
        p_lst = sage_ideal( pol_lst + proj_lst ).elimination_ideal( x ).gens()

        # obtain a polynomial in x0,...,x8
        p_lst = [p.subs( vx_dct ) for p in p_lst]
        fx = p_lst[0]

        tries += 1
        if len( fx.variables() ) < 4 or len( p_lst ) != 1:

            pmat = get_pmat( True )

            if tries % 100 == 0:
                OrbTools.p( 'tries =', tries, p_lst )

            if tries == 1000:
                return -1
        else:
            projected = True

    w0, w1, w2, w3 = fx.variables()
    fx = fx.subs( {w0:x[0], w1:x[1], w2:x[2], w3:x[3]} )

    x0, x1, x2, x3 = OrbRing.coerce( 'x0,x1,x2,x3' )
    x, y, z = sage_var( 'x,y,z' )
    fxyz = fx.subs( {x0:1, x1:x, x2:y, x3:z} )

    OrbTools.p( fx )
    OrbTools.p( fxyz )

    return fx, fxyz


def get_factor_lst( pol ):
    '''
    The method requires that the maple-command 
    is in "os.environ['PATH']".
    See [https://www.maplesoft.com].
    
    Parameters
    ----------
    pol : OrbRing.R  
        A polynomial.
    
    Returns
    -------
    list
        Return a list of factors of "pol": 
        [ (<factor>,<multiplicity>),... ] 
        If Maple is not accessible, then
        returns the empty-list [] 
    '''
    try:
        sage_maple.eval( 'fct := evala(AFactors(' + str( pol ) + '));' )
    except:
        return []

    fct_lst = sage_maple.eval( 'lprint(fct);' )
    fct_lst = str( fct_lst ).split( ',' )

    OrbTools.p( fct_lst )

    cf = fct_lst[0].replace( '[', '' ).replace( ']', '' ).strip()
    new_lst = []
    for i in range( 1, len( fct_lst ), 2 ):
        fact = fct_lst[i].replace( '[', '' ).replace( ']', '' ).strip()
        mult = fct_lst[i + 1].replace( '[', '' ).replace( ']', '' ).strip()
        new_lst += [( fact, mult )]

    OrbTools.p( cf )
    OrbTools.p( len( new_lst ), new_lst )

    return new_lst


def get_genus( pol, plane = 'x1+2*x2+17*x3+11*x0' ):
    '''
    The method requires that the maple-command 
    is in "os.environ['PATH']". 
    See [https://www.maplesoft.com].
    
    Parameters
    ----------
    pol : OrbRing.R
        A polynomial in QQ[x0,x1,x2,x3].
    
    plane : string 
        A String of a linear polynomial in QQ[x0,x1,x2,x3].
        
    Returns
    -------
    int
        An integer denoting the geometric genus of
        the curve given by the intersection of the 
        surface defined by "pol", with the plane defined 
        by "plane". If this geometric genus is not defined, 
        then -2 is returned. 
        If Maple is not installed then -3 is returned.
    '''
    OrbTools.p( pol )

    # obtain an equation for the curve defined
    # intersecting a plane with the zero-set of pol.
    plane = OrbRing.coerce( plane )
    K = sage_ideal( pol, plane ).groebner_basis()
    P = K[0]
    if P.total_degree() <= 1:
        P = K[1]
    P = P.subs( {OrbRing.coerce( 'x3' ):1} )

    # compute geometric genus with Maple.
    try:
        sage_maple.eval( 'with(algcurves);' )
    except:
        return -3

    sage_maple.eval( 'P := ' + str( P ) + ';' )
    gen = sage_maple.eval( 'genus(P,x1,x2);' )

    OrbTools.p( gen )

    try:
        return int( gen )
    except ValueError:
        return -2


def get_sing_lst( pol, probable = True ):
    '''
    The method requires that the magma-command 
    is in "os.environ['PATH']".    
    See [http://magma.maths.usyd.edu.au/magma/].
    
    Parameters
    ----------
    pol : OrbRing.R       
        A homogeneous polynomial in QQ[x0,x1,x2,x3].
        
    probable : boolean
        If True, performs a non-deterministic version of a 
        radical decomposition algorithm, which is faster.
        The correctness of output is not guaranteed in this case.
    
    Returns
    -------
    list
        Suppose that X is the surface defined by the zero-set of "pol".
        The output is a list           
            [ (<I>, <H>), ... ]          
        where <I> is the ideal of a component in singular locus of X, 
        and <H> is the Hilbert polynomial of this ideal.
        If Magma is not accessible, then the empty-list [] is returned.
        
    '''
    x0, x1, x2, x3 = OrbRing.coerce( 'x0,x1,x2,x3' )
    df_str = str( [sage_diff( pol, x0 ), sage_diff( pol, x1 ), sage_diff( pol, x2 ), sage_diff( pol, x3 )] )[1:-1]

    OrbTools.p( df_str )

    mi = ''
    mi += 'P<x0,x1,x2,x3> := PolynomialRing(RationalField(), 4);\n'
    mi += 'MI := ideal< P |' + df_str + '>;\n'

    if probable:
        mi += 'MD := ProbableRadicalDecomposition( MI );\n'
    else:
        mi += 'MD := RadicalDecomposition( MI );\n'
    mi += '#MD;\n'

    try:
        mo1 = int( sage_magma.eval( mi ) )
    except:
        return []

    sing_lst = []
    Ry = sage_PolynomialRing( OrbRing.num_field, sage_var( 'y0,y1,y2,y3' ), order = 'degrevlex' )
    for idx in range( mo1 ):

        comp = str( sage_magma.eval( 'Basis(MD[' + str( idx + 1 ) + ']);\n' ) )
        comp = comp.replace( '\n', '' )

        # compute hilbert polynomial of component in singular locus
        compy = sage__eval( comp.replace( 'x', 'y' ), Ry.gens_dict() )
        idy = Ry.ideal( compy )
        hpol = idy.hilbert_polynomial()

        sing_lst += [( comp, hpol )]
        OrbTools.p( idx, sing_lst[-1] )

    OrbTools.p( sing_lst )

    return sing_lst


def get_pmz( pmat, omat, vmat ):
    '''
    Parameters
    ----------
    pmat : sage_matrix
        A 4x9 invertible matrix with entries in QQ. 
        A matrix represents a projection from 
        a 7-sphere in projective 8-space to projective 3-space.
        
    omat : sage_matrix 
        A 9x9 invertible matrix with entries in QQ[c1,s1]. 
        This matrix represents a projective curve 
        in the automorphism group of the projective 7-sphere.
        Thus "omat" represents a 1-parameter subgroup in Aut(S^7).
                    
    vmat : sage_matrix 
        A 9x9 invertible matrix with entries in QQ. 
        This matrix represents an element in Aut(S^7),
        which transforms a standard circle (see below).
        
    Returns
    -------
    list
        Two lists of elements in QQ[c0,s0,c1,s1].
        The 1st list has length 9 and the 2nd list has length 4.
        The 1st list represent a parametrization 
              S^1xS^1--->S^7
        of a surface in S^7 and the 2nd list the parametrization 
              S^1xS^1--->P^3
        of the surface projected into
        P^3 (projective 3-space) using "pmat". 
        Here (c0,s0) and (c1,s1) are points on S^1.
                    
    Notes
    -----
    The surface in S^7 is obtained by applying a 1-parameter subgroup to a 
    circle C. Here C is the "vmat"-transform of the standard circle B in S^7 
    where
    B = { x | -x0^2+x1^2+x2^2==0 } and S^7 = { x | -x0^2+x1^2+...+x8^2==0 }.             
    '''
    c1, s1 = OrbRing.coerce( 'c1,s1' )
    pmz_lst = list( omat * vmat * sage_vector( [1, c1, s1, 0, 0, 0, 0, 0, 0] ) )
    prj_pmz_lst = list( pmat * omat * vmat * sage_vector( [1, c1, s1, 0, 0, 0, 0, 0, 0] ) )

    return pmz_lst, prj_pmz_lst


def get_orb_bp_tree( pmz_lst ):
    '''
    Parameters
    ----------
    pmz_lst : list
        A list of 9 elements p0,...,p8 in QQ[c0,s0,c1,s1]
        such that -p0^2+p1^2+...+p8^2==0.
        Some of the polynomials can be equal to zero. 
        The list should represent a parametrization:
            S^1xS^1--->S^7.
        Here (c0,s0) is a points on S^1 such that
        thus c0^2+s0^2-1==0. Similarly for (c1,s1).
                                                                                 
    Returns
    -------
    linear_series.BasePointTree
        Base points of a parametrizing map given by the composition:
            P^1xP^1---->S^1xS^1--->S^7--->S^n          
        with 2<=n<=7. The composition of the latter two maps 
        are defined by omitting the zero polynomials from "pmz_lst". 
    '''

    # setup dictionary for reparametrization'
    #
    c0, s0, c1, s1 = OrbRing.coerce( 'c0,s0,c1,s1' )
    dct1 = {}
    dct1[c0] = '2*t0*t1/(t0^2+t1^2)'
    dct1[s0] = '(-t0^2+t1^2)/(t0^2+t1^2)'
    dct1[c1] = '2*v0*v1/(v0^2+v1^2)'
    dct1[s1] = '(-v0^2+v1^2)/(v0^2+v1^2)'
    for key in dct1: dct1[key] = OrbRing.coerce( dct1[key] )

    # apply reparametrization and multiply out denominators
    # where we only consider non-zero entries
    #
    ps_lst = [ pmz for pmz in pmz_lst if pmz != 0 ]
    gcm1 = OrbRing.coerce( '(t0^2+t1^2)*(v0^2+v1^2)' )
    ps_lst = [ OrbRing.coerce( ps.subs( dct1 ) * gcm1 ) for ps in ps_lst ]

    # ensure that polynomials are co-prime
    #
    gcd1 = sage_gcd( ps_lst )
    ps_lst = [ OrbRing.coerce( ps / gcd1 ) for ps in ps_lst ]
    OrbTools.p( 'gcd =', gcd1 )
    OrbTools.p( 'ps_lst =', ps_lst )

    # Verify whether "ps_lst" represents a map P^1xP^1--->S^n
    # where "n==len(ps_lst)".
    #
    sum1 = sum( [-ps_lst[0] ** 2] + [ ps ** 2 for ps in ps_lst[1:] ] )
    OrbTools.p( 'sum =', sum1 )
    if sum1 != 0:
        warnings.warn( 'Warning: Not parametrization of surface in S^7: ' + str( sum1 ), )

    # set coordinates x,y,v,w
    #
    t0, t1, v0, v1 = OrbRing.coerce( 't0,t1,v0,v1' )
    dct2 = {}
    dct2[t0] = sage_var( 'x' )
    dct2[t1] = sage_var( 'y' )
    dct2[v0] = sage_var( 'v' )
    dct2[v1] = sage_var( 'w' )
    xyvw_lst = [ str( ps.subs( dct2 ) ) for ps in ps_lst ]

    #
    # Compute base point tree using "linear_series" package
    #
    ls = LinearSeries( xyvw_lst, PolyRing( 'x,y,v,w', True ) )
    bp_tree = ls.get_bp_tree()
    OrbTools.p( ls )
    OrbTools.p( bp_tree )

    return bp_tree


def get_imp( omat, vmat ):
    '''
    Parameters
    ----------
    omat : sage_matrix 
        A 9x9 invertible matrix with entries in QQ[c0,s0]. 
        This matrix represents a projective curve 
        in the automorphism group of the projective 7-sphere.
        Thus "omat" represents a 1-parameter subgroup in Aut(S^7).
                    
    vmat : sage_matrix  
        A 9x9 invertible matrix with entries in QQ. 
        This matrix represents an element in Aut(S^7),
        which transforms a standard circle.    

    Returns
    -------
    list<OrbRing.R>
        A list of elements in QQ[x0,...,x8].
        This list represent the generators of the ideal corresponding to 
        the variety, which is obtained by applying a 1-parameter subgroup to
        a circle C. Here C is the "vmat"-transform of 
        the standard circle B in S^7 where        
        B = { x | -x0^2+x1^2+x2^2==0 } and S^7 = { x | -x0^2+x1^2+...+x8^2==0 }.   
    '''

    # declare list of coordinate variables
    v_lst = OrbRing.coerce( '[v0,v1,v2,v3,v4,v5,v6,v7,v8]' )
    x_lst = OrbRing.coerce( '[x0,x1,x2,x3,x4,x5,x6,x7,x8]' )
    c_lst = OrbRing.coerce( '[c0,s0]' )

    # construct generators of ideal of orbital product
    g_lst = []

    # v[i] coordinates of points on a circle C in S^7
    vmatI = vmat.inverse()
    g_lst += list( vmatI * sage_vector( v_lst ) )[3:]
    g_lst += OrbRing.coerce( '[-v0^2+v1^2+v2^2+v3^2+v4^2+v5^2+v6^2+v7^2+v8^2]' )

    # consider all point that are an orbit of C
    # the 1-parameter subgroup of Aut(S^7)
    # represented by the matrix omat
    e_lst = list( omat * sage_vector( v_lst ) )
    g_lst += [ x_lst[i] - e_lst[i] for i in range( 0, 8 + 1 ) ]
    g_lst += OrbRing.coerce( '[-x0^2+x1^2+x2^2+x3^2+x4^2+x5^2+x6^2+x7^2+x8^2]' )
    g_lst += OrbRing.coerce( '[s0^2+c0^2-1]' )

    # compute the resulting variety by elimination
    g_ideal = OrbRing.R.ideal( g_lst )
    imp_lst = list( g_ideal.elimination_ideal( v_lst + c_lst ).gens() )

    return imp_lst


def get_pmz_verify( o ):
    '''
    Parameters
    ----------
        o : OrbOutput
    
    Returns
    -------
    Boolean
        * Return "None" if the test could not be performed because
          either parametrization or implicit equation was not available.            
        * Return "True" if implicit equation of projected surface
          agrees with parametrization composed with projection.          
        * Return "False" if both parametrization and implicit equation were 
          available but do not agree.               
    '''

    if not o.input.do['pmz'] or not o.input.do['imp']:
        return None

    if o.prj_pol == -1 or o.gen == -2:
        return False

    OrbTools.p( 'Testing parametrization...' )
    c0, s0, c1, s1 = OrbRing.coerce( 'c0,s0,c1,s1' )
    x0, x1, x2, x3 = OrbRing.coerce( 'x0,x1,x2,x3' )
    f = o.prj_pol
    p = o.prj_pmz_lst
    fp = o.prj_pol.subs( {x0:p[0], x1:p[1], x2:p[2], x3:p[3]} )
    test = fp.reduce( [c0 * c0 + s0 * s0 - 1, c1 * c1 + s1 * s1 - 1] )
    OrbTools.p( test )
    if test != 0:
        return False

    return True


def orb_product( input ):
    '''    
    Parameters
    ----------
    input : OrbInput
        A 1-parameter subgroup in Aut(S^7) and a circle in S^7.    
        
    Returns
    -------
    OrbOutput 
        A surface (or curve) S, which is obtained by applying 
        the 1-parameter subgroup to the circle in S^7.    
        
    Notes
    -----
    For additional info on the input and output we  
    refer to the documentation of "OrbInput" and "OrbOutput".
    '''

    o = OrbOutput( input )

    if input.do['pmz']:
        o.pmz_lst, o.prj_pmz_lst = get_pmz( input.pmat, input.omat, input.vmat )

    if input.do['bpt']:
        o.bp_tree = get_orb_bp_tree( o.pmz_lst )

    if input.do['imp']:
        o.imp_lst = get_imp( input.omat, input.vmat )
    else:
        return o  # cannot obtain remaining attributes without "o.imp_lst"

    # Compute remaining attributes
    #
    if input.do['dde']:
        o.emb = get_emb_dim( o.imp_lst )
        o.deg, o.dim = get_deg_dim( o.imp_lst )

    if input.do['prj']:
        o.prj_pol, o.xyz_pol = get_project( o.imp_lst, input.pmat )

    if input.do['fct']:
        o.fct_lst = get_factor_lst( o.prj_pol )

    if input.do['gen']:
        o.gen = get_genus( o.prj_pol )

    if input.do['sng']:
        o.sng_lst = get_sing_lst( o.prj_pol )

    # Test whether parametrization agrees with implicitization.
    #
    if input.do['tst']:
        o.pmz_test = get_pmz_verify( o )

    return o






