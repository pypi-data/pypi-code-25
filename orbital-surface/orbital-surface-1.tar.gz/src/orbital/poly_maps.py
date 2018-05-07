'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Nov 23, 2017

@author: Niels Lubbes
'''
from sage_interface import sage_PolynomialRing
from sage_interface import sage_FractionField
from sage_interface import sage__eval
from sage_interface import sage_ideal
from sage_interface import sage_gcd
from sage_interface import sage_lcm
from sage_interface import sage_SR
from sage_interface import sage_var
from sage_interface import sage_QQ
from sage_interface import sage_factor

from class_orb_tools import OrbTools


def ring_dict( R ):
    '''
    Retrieve a translation dictionary for sage__eval() from 
    an algebraic structure of the sage environment.
    
    Parameters
    ----------
    R : sage_RING
        We the object to have a ".gens_dict()" method.        
    
    Returns
    -------
    dict
        A dictionary where keys are strings and values
        are generators of a sage_RING
    '''

    dct = R.gens_dict()
    while R != R.base():
        R = R.base()
        dct.update( R.gens_dict() )

    return dct



def invert_map( f, X, base = sage_QQ ):
    '''
    Computes the inverse of a map defined by polynomials.
    
    If the parameters f and X are not strings, then
    they are automatically converted to strings.
    
    Parameters
    ----------
    f : string(list<sage_POLY>)
        A string of a list of m+1 polynomials in 
        x=(x0,...,xn) or y=(y0,...,yn) with n<=50 that
        define a projective map:
        F: X ---> P^m
        where P^m denotes projective n-space.

    X : string(list<sage_POLY>)
        A string of a list of polynomials in 
        the same variables as parameter f that 
        define the ideal of a variety X in 
        projective space.
    
    base : sage_RING 
        Ground field of polynomials.           
              
    Returns
    -------
    list<sage_POLY>
            Suppose that the input were polynomials in x.
        The output is of the form
            [ p0(x)-r0(y) ,..., pn(x)-rn(y) ]
        were ri(y) are rational functions and pi(x) are
        polynomials. If f is a birational map, then pi(x)=xi.
        The polynomials live in the polynomial ring R[x]
        where R=B(y) and base ring B is defined by the base
        parameter.  
    '''
    # make sure that the input are strings
    f = str( f )
    X = str( X )

    # if the input are polynomials in x then the output
    # is a list of poynomials in y
    ( vx, vy ) = ( 'x', 'y' ) if 'x' in f else ( 'y', 'x' )

    # detect the number of x-variables occurring
    n_lst = []
    n = 0
    while n < 50:
        if vx + str( n ) in f or vx + str( n ) in X:
            n_lst += [n]
        n = n + 1
    n = max( n_lst )


    # construct ring B(y0,...ym)[x0,...,xn]
    # over fraction field B(y0,...ym)
    # where m is the number of elements in map f and B equals base
    #
    # For example B is rationals sage_QQ so that:
    # xring  = sage_PolynomialRing( sage_QQ, 'x0,x1,x2,x3,x4')
    # yfield = sage_FractionField( sage_PolynomialRing( sage_QQ, 'y0,y1,y2,y3' ) )
    # ring   = sage_PolynomialRing( yfield, 'x0,x1,x2,x3,x4')
    #
    x_lst = [ vx + str( i ) for i in range( n + 1 ) ]
    y_lst = [ vy + str( i ) for i in range( len( f.split( ',' ) ) ) ]
    yfield = sage_FractionField( sage_PolynomialRing( base, y_lst ) )
    ring = sage_PolynomialRing( yfield, x_lst )
    y_lst = yfield.gens()
    x_lst = ring.gens()

    dct = ring_dict( ring )
    X = sage__eval( X, dct )
    f = sage__eval( f, dct )
    map = [ y_lst[i] - f[i] for i in range( len( f ) ) ]
    gb_lst = list( sage_ideal( X + map ).groebner_basis() )

    OrbTools.p( gb_lst )

    return gb_lst



def invert_birational_map( f, X, base = sage_QQ ):
    '''
    Computes the inverse of a birational map.
    
    If the parameters f and X are not strings, then
    they are automatically converted to strings.
    
    Parameters
    ----------
    f : string(list<sage_POLY>)
        A string of a list of m+1 polynomials in 
        x=(x0,...,xn) or y=(y0,...,yn) with n<=50 that
        define a projective map:
        F: X ---> P^m
        where P^m denotes projective n-space.

    X : string(list<sage_POLY>)
        A string of a list of polynomials in 
        the same variables as parameter f that 
        define the ideal of a variety X in 
        projective space.
    
    base : sage_RING 
        Ground field of polynomials.           
                            
    Returns
    -------
    list<sage_POLY>
        Polynomials that define the inverse map
            f^{-1}: P^m ---> X.                   
        If the input were polynomials in x, then the 
        output are polynomials in y, and vice versa. 
        The basefield of the polynomial ring is equal 
        to base.
        
    Raises
    ------
    ValueError
        If parameter f is not a birational map.        
    '''
    ga_lst = invert_map( f, X, base )
    x_lst = ga_lst[0].parent().gens()

    # We expect that ga_lst is of the following form:
    #     [ x0-r0(y), ..., xn-rn(y) ]
    # where f_i are rational functions in y=(y_0,...,ym).
    #
    gb_lst = []
    for ga in ga_lst:
        for x in x_lst:
            if str( x ) in str( ga ):
                gb_lst += [-( ga - x )]

    OrbTools.p( gb_lst )

    # The x-variables did not occur as expected
    for gb in gb_lst:
        if 'x' in str( gb ) and 'y' in str( gb ):
            raise ValueError( 'Input map f=', f, ' is not birational.' )

    # multiply out least common denominator
    den_lst = []
    for gb in gb_lst:
        den_lst += [ gb.denominator() ]
    cden = sage_lcm( den_lst )
    gc_lst = [ gb * cden for gb in gb_lst ]

    # multiply out a common integer factor
    cf = sage_gcd( [sage_SR( gc ) for gc in gc_lst ] )
    gd_lst = [ gc / cf for gc in gc_lst ]

    return gd_lst


def image_map( f, X, base = sage_QQ ):
    '''
    Computes the image f(X) of a variety X
    under a map f, defined by polynomials.
    
    If the parameters f and X are not strings, then
    they are automatically converted to strings.
    
    Parameters
    ----------
    f : string(list<sage_POLY>)
        A string of a list of m+1 polynomials in 
        x=(x0,...,xn) or y=(y0,...,yn) with n<=50 that
        define a projective map:
        f: X ---> P^m
        where P^m denotes projective n-space.

    X : string(list<sage_POLY>)
        A string of a list of polynomials in 
        the same variables as parameter f that 
        define the ideal of a variety X in 
        projective space.
    
    base : sage_RING 
        Ground field of polynomials. 
        
    Returns
    -------
    list<sage_POLY>
        A list of polynomials that define the
        ideal of f(X). The polynomials are in y
        if the input are polynomials in x, and
        vice versa.            
    '''
    # make sure that the input are strings
    f = str( f )
    X = str( X )

    # if the input are polynomials in x then the output
    # is a list of poynomials in y
    ( vx, vy ) = ( 'x', 'y' ) if 'x' in f else ( 'y', 'x' )

    # detect the number of x-variables occurring
    n_lst = []
    n = 0
    while n < 50:
        if vx + str( n ) in f or vx + str( n ) in X:
            n_lst += [n]
        n = n + 1
    n = max( n_lst )

    # construct polynomial ring B[x0,...,xn,y0,...,ym]
    # where B is given by parameter base.
    x_lst = [ vx + str( i ) for i in range( n + 1 ) ]
    y_lst = [ vy + str( i ) for i in range( len( f.split( ',' ) ) ) ]
    mord = 'degrevlex' if base == sage_QQ else 'lexdeg'  # needed for elimination
    xyring = sage_PolynomialRing( base, x_lst + y_lst, mord )
    x_lst = xyring.gens()[:len( x_lst )]
    y_lst = xyring.gens()[len( x_lst ):]

    # coerce into common ring with xi and yi variables
    dct = ring_dict( xyring )
    f_lst = sage__eval( f, dct )
    X_lst = sage__eval( X, dct )
    mf_lst = [ y_lst[i] - f_lst[i] for i in range( len( f_lst ) ) ]

    # compute image by using groebner basis
    OrbTools.p( X_lst + mf_lst )
    try:

        # compute image by using groebner basis
        img_lst = sage_ideal( X_lst + mf_lst ).elimination_ideal( x_lst ).gens()
        OrbTools.p( img_lst )
        return img_lst

    except Exception, e:

        OrbTools.p( 'Exception occurred:', repr( e ) )
        gb_lst = sage_ideal( X_lst + mf_lst ).groebner_basis()
        OrbTools.p( gb_lst )
        e_lst = []
        for gb in gb_lst:
            if vx not in str( gb ):
                e_lst += [gb]
        return e_lst


def preimage_map( f, X, Y, base = sage_QQ ):
    '''
    Computes the preimage f^{-1}(Y) of a variety Y under a map 
    f: X ---> P^m, defined by polynomials, where the domain 
    X is a variety and P^m denotes projective space.
    
    If the parameters f, X and Y are not strings, then
    they are automatically converted to strings.
    
    Parameters
    ----------
    f : string(list<sage_POLY>)
        A string of a list of m+1 polynomials in 
        x=(x0,...,xn) or y=(y0,...,yn) with n<=50 that
        define a projective map:
        f: X ---> P^m
        where P^m denotes projective n-space.

    X : string(list<sage_POLY>)
        A string of a list of polynomials in 
        the same variables as parameter f that 
        define the ideal of a variety X in 
        projective space.

    Y : string(list<sage_POLY>)
        A string of a list of polynomials in y if
        f consists of polynomials in x (and vice versa). 
        Polynomials define the generators of an ideal of 
        a variety Y in projective space.
    
    base : sage_RING 
        Ground field of polynomials.     
        
    Returns
    -------
    list(list<sage_POLY>)
        A list of lists of polynomials. Each list of polynomials
        defines a component in the primary decomposition of the ideal 
        of the preimage f^{-1}(Y). 
        The polynomials are in x or y if parameter f represents 
        polynomials in x respectively y.
        Note that some of the components in the primary decomposition
        are not part of the ideal, but correspond to the locus 
        where the map f is not defined.             
    '''
    # make sure that the input are strings
    f = str( f )
    X = str( X )
    Y = str( Y )

    # if the input are polynomials in x then the output
    # is a list of poynomials in y
    ( vx, vy ) = ( 'x', 'y' ) if 'x' in f else ( 'y', 'x' )

    # detect the number of x-variables occurring
    n_lst = []
    n = 0
    while n < 50:
        if vx + str( n ) in f or vx + str( n ) in X:
            n_lst += [n]
        n = n + 1
    n = max( n_lst )

    # construct polynomial ring B[x0,...,xn,y0,...,ym]
    # where B is given by parameter base.
    x_lst = [ vx + str( i ) for i in range( n + 1 ) ]
    y_lst = [ vy + str( i ) for i in range( len( f.split( ',' ) ) ) ]
    mord = 'degrevlex' if base == sage_QQ else 'lex'  # needed for elimination
    xyring = sage_PolynomialRing( base, y_lst + x_lst, order = mord )
    y_lst = xyring.gens()[:len( y_lst )]
    x_lst = xyring.gens()[len( y_lst ):]


    # coerce into common ring with xi and yi variables
    dct = ring_dict( xyring )
    f_lst = sage__eval( f, dct )
    X_lst = sage__eval( X, dct )
    Y_lst = sage__eval( Y, dct )
    mf_lst = [ y_lst[i] - f_lst[i] for i in range( len( f_lst ) ) ]

    # compute image by using groebner basis
    OrbTools.p( X_lst + mf_lst + Y_lst )
    try:

        img_id = sage_ideal( X_lst + mf_lst + Y_lst ).elimination_ideal( y_lst )
        img_lst = img_id.primary_decomposition()
        img_lst = [ img.gens() for img in img_lst ]
        OrbTools.p( img_lst )
        return img_lst

    except Exception, e:

        OrbTools.p( 'Exception occurred:', repr( e ) )
        gb_lst = sage_ideal( X_lst + mf_lst + Y_lst ).groebner_basis()
        OrbTools.p( gb_lst )
        e_lst = []
        for gb in gb_lst:
            if vy not in str( gb ):
                e_lst += [gb]
        return e_lst


def compose_maps( g, f, base = sage_QQ ):
    '''
    Computes the composition of polynomial maps.
    
    Both parameters and return value are all polynomials 
    in either x=(x0,...,xn) or y=(y0,...,yn) with n<=50,
    but not both.
    
    The input parameters are explicitly converted to 
    strings, in case they are not strings.
    
    Parameters
    ----------
    f : string(list<sage_POLY>)
        A string of a list of b+1 polynomials that
        defines a projective map:
        f: P^a ---> P^b
        where P^a denotes projective n-space.    
        If the value is not a string, then it will
        be converted to a string.
    
    g : string(list<sage_POLY>)
        A string of a list of c+1 polynomials that
        defines a projective map: g: P^b ---> P^c.   
        If the value is not a string, then it will
        be converted to a string.         
    
    base : sage_RING 
        Ground field of polynomials.       
    
    Returns
    -------
    list<sage_POLY>
        The composition of the maps f o g: P^a ---> P^c.    
    '''
    # make sure that the input are strings
    g = str( g )
    f = str( f )

    # check variables
    ( vf, vg ) = ( 'x', 'y' ) if 'x' in f else ( 'y', 'x' )
    if vg not in g:
        g = g.replace( vf, vg )


    # detect the number of vf-variables occurring
    n_lst = []
    n = 0
    while n < 50:
        if vf + str( n ) in f or vg + str( n ) in g:
            n_lst += [n]
        n = n + 1
    n = max( n_lst )

    # construct the ring
    v_lst = []
    v_lst += [ vf + str( i ) for i in range( n + 1 ) ]
    v_lst += [ vg + str( i ) for i in range( n + 1 ) ]
    ring = sage_PolynomialRing( base, v_lst )
    vg_lst = ring.gens()[n + 1:]
    dct = ring_dict( ring )
    g_lst = sage__eval( g, dct )
    f_lst = sage__eval( f, dct )

    # compose the maps
    for i in range( len( f_lst ) ):
        g_lst = [ g.subs( {vg_lst[i]:f_lst[i]} ) for g in g_lst ]

    OrbTools.p( g_lst )

    return g_lst


def euclidean_type_form( X, base = sage_QQ ):
    '''
    Outputs the equation of a hypersurface in P^n in a form 
    so that the intersection with the hyperplane at infinity
    becomes apparent. 
    
    Parameters
    ----------
    X : string(sage_POLY)
        A polynomial in the variables x=(x0,...,xn)
        or y=(y0,...,yn).
    
    base : sage_RING 
        Ground field of polynomials.      
    
    Returns
    -------
    string
        A string of the equations in the normal form
            X1 + X2
        where
            X1 = sage_factor( X.subs({x0:0}) )
            X2 = sage_factor( X-X1 )
        If #variables is equal to 3, then
        also include the form in x,y and z variables.
    '''
    # make sure that the input are strings
    X = str( X )

    # if the input are polynomials in x then the output
    # is a list of poynomials in y
    ( vx, vy ) = ( 'x', 'y' ) if 'x' in X else ( 'y', 'x' )

    # detect the number of x-variables occurring
    n_lst = []
    n = 0
    while n < 50:
        if vx + str( n ) in X:
            n_lst += [n]
        n = n + 1
    n = max( n_lst )


    x_lst = [ vx + str( i ) for i in range( n + 1 ) ]
    ring = sage_PolynomialRing( base, x_lst )
    x_lst = ring.gens()
    dct = ring_dict( ring )
    X = sage__eval( X, dct )
    XA = sage_factor( X.subs( {x_lst[0]:0} ) )
    XB = sage_factor( X - XA )
    assert X == XA + XB
    OrbTools.p( 'X =', XA, '+', XB )
    out = str( XA ) + ' + ' + str( XB )

    if n == 3:
        x0, x1, x2, x3 = ring.gens()
        x, y, z = sage_var( 'x,y,z' )
        W = X.subs( {x1:x, x2:y, x3:z} )
        WA = W.subs( {x0:0} )
        WB = W - WA
        assert W == WA + WB
        WA = sage_factor( WA.subs( {x0:1} ) )
        WB = sage_factor( WB.subs( {x0:1} ) )
        OrbTools.p( 'W =', WA, '+', WB )
        out += '\n' + str( WA ) + ' + ' + str( WB )

    return out


def hilbert_poly( X, base = sage_QQ ):
    '''
    Computes the Hilbert polynomial of an ideal.
    
    Parameters
    ----------
    X : string(sage_POLY)
        A polynomial in the variables x=(x0,...,xn)
        or y=(y0,...,yn).
    
    base : sage_RING 
        Ground field of polynomials.      
    
    Returns
    -------
    sage_POLY
        Hilbert polynomial of ideal.
    
    '''
    # make sure that the input are strings
    X = str( X )

    # if the input are polynomials in x then the output
    # is a list of poynomials in y
    ( vx, vy ) = ( 'x', 'y' ) if 'x' in X else ( 'y', 'x' )

    # detect the number of x-variables occurring
    n_lst = []
    n = 0
    while n < 50:
        if vx + str( n ) in X:
            n_lst += [n]
        n = n + 1
    n = max( n_lst )


    x_lst = [ vx + str( i ) for i in range( n + 1 ) ]
    ring = sage_PolynomialRing( base, x_lst )
    x_lst = ring.gens()
    dct = ring_dict( ring )
    X = sage__eval( X, dct )

    return sage_ideal( X ).hilbert_polynomial()

