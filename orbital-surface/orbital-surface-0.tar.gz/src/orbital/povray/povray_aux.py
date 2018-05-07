'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Nov 23, 2017
@author: Niels Lubbes
'''

import os
import subprocess

from copy import copy

from time import gmtime
from time import strftime

from orbital.sage_interface import sage_PolynomialRing
from orbital.sage_interface import sage_QQ
from orbital.sage_interface import sage__eval
from orbital.sage_interface import sage_cos
from orbital.sage_interface import sage_sin
from orbital.sage_interface import sage_pi

from orbital.class_orb_tools import OrbTools

from orbital.class_orb_ring import OrbRing

from orbital.povray.class_pov_input import PovInput


def pov_exp_lst( d, v, tbl = [] ):
    '''
    Called by "pov_coef_lst".
    
    Parameters
    ----------
    d : int 
        A positive integer.
    
    v : int  
        A positive integer.
    
    tbl : list  
        A list of lists of length "v", should always be []
        unless called recursively on its output. 
    
    Returns
    -------
    list
        An ordered list of exponents in "v" variables.
        This is used for the povray poly object:
        http://www.povray.org/documentation/3.7.0/r3_4.html#r3_4_5_3_2
    '''

    if tbl == []:
        tbl = [ v * [0] ]

    if d == 0:
        return tbl

    ntbl = []
    for row in tbl:
        for idx in range( len( row ) ):
            nrow = copy( row )
            nrow[idx] += 1
            if nrow not in tbl + ntbl:
                ntbl += pov_exp_lst( d - 1, v, [nrow] )

    out_lst = []
    add_lst = []
    for val in ntbl:
        added = False
        for add in add_lst:
            added = added or ( add == val )
        if not added:
            out_lst += [val]
            add_lst += [val]

    return out_lst


def pov_coef_lst( poly ):
    '''
    Parameters
    ----------
    poly : string 
        A string representing a polynomial in QQ[x,y,z].
    
    Returns
    -------
    tuple
        A 2-tuple (<degree poly>, <coefficient list of poly>)
        where the coefficient list is ordered according to 
        povray's poly object:
        http://www.povray.org/documentation/3.7.0/r3_4.html#r3_4_5_3_2
    '''

    R = sage_PolynomialRing( sage_QQ, 'x,y,z', order = 'degrevlex' )  # lower degree equations first
    x, y, z = R.gens()
    poly = sage__eval( str( poly ), R.gens_dict() )

    d = poly.total_degree()
    v = len( poly.variables() )

    exp_lst = pov_exp_lst( d, v + 1 )

    coef_lst = []
    for exp in exp_lst:
        coef_lst += [ poly.coefficient( {x:exp[0], y:exp[1], z:exp[2]} ) ]

    return d, coef_lst


def pov_nopow( poly ):
    '''
    Parameters
    ----------
    poly : string 
        A string representing a polynomial in QQ[x,y,z].
    
    Returns
    -------
    string
        A string representation of the polynomial "poly" 
        without '^'-power symbols.
    
    Example
    -------
        "x^3*y^2*z+x^2*y" --> "x*x*x*y*y*z+x*x*y"
    '''

    R = PolynomialRing( QQ, var( 'x,y,z' ), order = 'degrevlex' )  # lower degree equations first
    x, y, z = R.gens()
    poly = sage_eval( str( poly ), R.gens_dict() )

    dct = {}
    for i in range( 2, poly.total_degree() + 1 ):
        dct.update( {'x^' + str( i ): ( i * 'x*' )[:-1] } )
        dct.update( {'y^' + str( i ): ( i * 'y*' )[:-1] } )
        dct.update( {'z^' + str( i ): ( i * 'z*' )[:-1] } )

    return reduce( lambda x, y: x.replace( y, dct[y] ), dct, str( poly ) )


def rgbt2pov( rgbt, gamma = 2.2 ):
    '''
    Converts RGB colors to Povray colors. 
    
    For more info see:
    <http://news.povray.org/povray.general/thread/%3Cweb.4a5865409e9a3ab0e4e47a1b0@news.povray.org%3E/>
    
    Parameters
    ----------
    rgbt : tuple
        A tuple consisting of 4 values: 
        Integer r in [0,255] defining the red component. 
        Integer g in [0,255] defining the green component.
        Integer b in [0,255] defining the blue component.    
        Integer t in [0,255] defining the transparency.    

    Returns
    -------
    tuple
        A tuple consisting of 4 entries for rgbt value in Povray:
        (r/255^2.2, g/255^2.2, b/255^2.2, t/255 ) 
        
    Note
    ----
    The output is used for setting "pin.text_dct", which is used in 
    "povray.create_pov_preamble_declares()".
    '''
    return ( ( rgbt[0] / 255.0 ) ** 2.2, ( rgbt[1] / 255.0 ) ** 2.2, ( rgbt[2] / 255.0 ) ** 2.2, rgbt[3] / 255.0 )


def get_pmz_value( pmz_lst, v0, v1, prec = 50 ):
    '''
    Parameters
    ----------
    pmz_lst : list<sage_POLY> 
        A list of 4 polynomials in QQ[c0,s0,c1,s1].
    
    v0 : sage_REALNUMBER      
        A real number in [0,2*pi)
    
    v1 : sage_REALNUMBER       
        A real number in [0,2*pi)
    
    prec : int    
        Number of digits.

    scale : int
        A positive integer.
    
    Returns
    -------
    list<float>
        Returns a point in R^3 represented by a list of 3 float 
        values with precision "prec":  
            F(a,b)=[ x, y, z  ].
        Here F(a,b) is represented by "pmz_lst" and
        has the following domain and range:  
              F: [0,2*pi)X[0,2*pi) ---> R^3.
        The parametrization is a map in terms of cosine and sine.   
        
        If F is not defined at the point it first looks at (v0-dv,v1-dv) 
        where dv is very small. If that does not work, then we return None.
               
    '''
    c0, s0, c1, s1, t0, t1 = OrbRing.coerce( 'c0,s0,c1,s1,t0,t1' )

    dct = {c0:sage_cos( v0 ), s0:sage_sin( v0 ), c1:sage_cos( v1 ), s1:sage_sin( v1 ), t0:v0, t1:v1}


    if type( pmz_lst[0] ) == int:
        W = sage_QQ( pmz_lst[0] )
    else:
        W = pmz_lst[0].subs( dct )

    X = pmz_lst[1].subs( dct )
    Y = pmz_lst[2].subs( dct )
    Z = pmz_lst[3].subs( dct )

    if W == 0:
        return None

    XW = round( X / W, prec )
    YW = round( Y / W, prec )
    ZW = round( Z / W, prec )

    return [ XW, YW, ZW ]


def get_curve_lst( pin, fam ):
    '''
    Parameters
    ----------
    pin : PovInput
        The following attributes of the PovInput object are used:
        * "pin.pmz_dct"
        * "pin.scale"
        * "pin.curve_dct"
        * "pin.curve_lst_dct"
                                         
    fam : string 
        A key string for a family id (eg. 'A').
        
    Returns
    -------
    list
        Returns a list of lists of points. Each list of points
        defines points on a curve. v1_lstD
        
        Returns "pin.curve_lst_dct[<fam>]"  if 
            "pin.curve_lst_dct[<fam>]!=None". 
    
        Otherwise let us assume w.l.o.g. that "fam=='A'"
        such that "pin.curve_lst_dct['A']==None".          
        
        We set "pin.curve_lst_dct['A']" as follows:
            pin.curve_lst_dct['A'] = [ <curveA<0>>, <curveA<1>>, ... ]            
        where           
          * <curveA<n>> is a list of points 
                [x,y,z] 
            on a curve in family with id 'A', which are 
            scaled with "pin.scale". 
          
          * The space between points in <curveA<n>> is 
            determined by "pin.curve_dct['A']['step0']".

          * The space between <curveA<n>> and <curveA<n+1>> is  
            determined by values in "pin.curve_dct['A']['step1']".

          * The precision of points in <curveA<n>> is 
            determined by values in "pin.curve_dct['A']['prec']".          
          
        Returns pin.curve_lst_dct['A'].
    '''

    OrbTools.p( fam )

    if fam in pin.curve_lst_dct and pin.curve_lst_dct[fam] != None:
        OrbTools.p( 'Already computed ', fam )
        return pin.curve_lst_dct[fam]

    pmz_lst, fam_id = pin.pmz_dct[fam]
    pmz_lst = OrbRing.coerce( pmz_lst )

    # loop through lists of parameter values
    pin.curve_lst_dct[fam] = []
    for v1 in pin.curve_dct[fam]['step1']:
        curve = []
        for v0 in pin.curve_dct[fam]['step0']:

            if fam_id == 0:
                point = get_pmz_value( pmz_lst, v0, v1, pin.curve_dct[fam]['prec'] )
            elif fam_id == 1:
                point = get_pmz_value( pmz_lst, v1, v0, pin.curve_dct[fam]['prec'] )
            else:
                raise ValueError( 'Expect pin.pmz_dct[fam][1] in [0,1]: ', fam_id )

            # add points to curve if map is defined
            if point != None:
                point = [ coord * pin.scale for coord in point  ]
                curve += [point]


        # need at least 3 points for cubic interpolation
        if len( curve ) >= 3:

            # add curve to family
            pin.curve_lst_dct[fam] += [curve]

    return pin.curve_lst_dct[fam]


def get_time_str():
    '''
    Returns
    -------
    string
        A string of the current local time.
    
    Example
    -------
        '2016-08-09__15-01-31'
    '''
    return strftime( "%Y-%m-%d__%H-%M-%S" )


def create_dir( file_name ):
    '''
    Creates the directory in which the file resides, 
    in case this directory does not exists.
      
    Parameters
    ----------
    file_name : string
        An absolute path to a file.

    Returns
    -------
    bool              
        Returns True if the directory was created and
        False otherwise.
    '''
    if not os.path.exists( os.path.dirname( file_name ) ):

        try:

            os.makedirs( os.path.dirname( file_name ) )

        except OSError as exc:
            # race condition ?
            if exc.errno != errno.EEXIST:
                raise

        return True
    else:
        return False


def convert_pngs_gif( path, fname, num_curves, ani_delay ):
    '''
    Creates an animated gif file with name "[path]+[fname].gif".

    Parameters
    ---------- 
    path : string      
        Location (ending with '/') of "ani/" directory containing
        png-files with name 
            "[fname]-#.png"
        where # is a number in [0,num_curves]
    
    fname : string      
        A string. 
    
    num_curves : int 
        A positive integer.

    ani_delay : int 
        A positive integer.    
    '''
    # We now convert the ray traced images into an animated
    # gif using the following linux command:
    #
    #    convert -resize 768x576 -delay 20 -loop 0 `ls -v orb?*.png` orb-ani.gif
    #

    file_name_prefix = path + 'ani/' + fname
    OrbTools.p( file_name_prefix )
    cmd = ['convert']
    cmd += ['-delay', str( ani_delay )]
    cmd += [ '-loop', '0']
    for idx in range( 0, num_curves ):
        cmd += [file_name_prefix + '-' + str( idx ) + '.png']
    cmd += [path + fname + '.gif']

    p = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE )

    out, err = p.communicate()
    OrbTools.p( 'out =', out )
    OrbTools.p( 'err =', err )




