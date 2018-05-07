'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jan 21, 2018
@author: Niels Lubbes
'''

from orbital.sage_interface import sage_var
from orbital.sage_interface import sage_vector
from orbital.sage_interface import sage_matrix
from orbital.sage_interface import sage_factor
from orbital.sage_interface import sage_QQ
from orbital.sage_interface import sage_pi
from orbital.sage_interface import sage_n

from orbital.class_orb_tools import OrbTools

from orbital.class_orb_ring import OrbRing

from orbital.povray.class_pov_input import PovInput
from orbital.povray.povray import create_pov
from orbital.povray.povray_aux import get_time_str

from linear_series.class_poly_ring import PolyRing
from linear_series.class_base_points import BasePointTree
from linear_series.class_linear_series import LinearSeries


def CH1_cyclide():
    '''
    Creates povray image of a CH1 cyclide, which is
    an inversion of a Circular Hyperboloid of 1 sheet.    
    '''

    # Construct a trigonometric parametrization by rotating a circle.
    r, R = 1, 1
    c0, s0, c1, s1 = sage_var( 'c0,s0,c1,s1' )
    x, y, v, w, a0 = sage_var( 'x,y,v,w,a0' )
    q2 = sage_QQ( 1 ) / 2
    MX = sage_matrix( [( 1, 0, 0 ), ( 0, c1, s1 ), ( 0, -s1, c1 )] )
    MXc = MX.subs( {c1:a0, s1:a0} )  # a0=1/sqrt(2)=cos(pi/4)=sin(pi/4)
    MZ = sage_matrix( [( c1, s1, 0 ), ( -s1, c1, 0 ), ( 0, 0, 1 )] )
    V = sage_vector( [r * c0, 0, r * s0] )
    V = MXc * V
    V[0] = V[0] + R
    pmz_AB_lst = list( MZ * V )
    OrbTools.p( 'V =', V )
    OrbTools.p( 'pmz_AB_lst =', pmz_AB_lst )
    for pmz in pmz_AB_lst: OrbTools.p( '\t\t', sage_factor( pmz ) )


    # Convert the trigonometric parametrization to a rational parametrization
    # We convert via the following formulas,
    #
    #     cos(s) = (y^2-x^2) / (y^2+x^2)
    #     sin(s) = 2*x*y / (y^2+x^2)
    #     y=1; x = arctan( s/2 )
    #
    C0 = ( y ** 2 - x ** 2 ) / ( y ** 2 + x ** 2 )
    S0 = 2 * x * y / ( y ** 2 + x ** 2 )
    C1 = ( w ** 2 - v ** 2 ) / ( w ** 2 + v ** 2 )
    S1 = 2 * v * w / ( w ** 2 + v ** 2 )
    den = ( y ** 2 + x ** 2 ) * ( w ** 2 + v ** 2 )
    dct = {c0:C0, s0:S0, c1:C1, s1:S1 }
    pmz_lst = [den] + [ ( elt.subs( dct ) * den ).simplify_full() for elt in list( MZ * V ) ]
    OrbTools.p( 'pmz_lst =', pmz_lst )
    for pmz in pmz_lst:
        OrbTools.p( '\t\t', sage_factor( pmz ) )

    # do a basepoint analysis on the rational parametrization
    # The True argument is for resetting the number field to QQ!
    ring = PolyRing( 'x,y,v,w', True ).ext_num_field( 't^2-1/2' )
    ls = LinearSeries( [str( pmz ) for pmz in pmz_lst], ring )
    OrbTools.p( ls.get_bp_tree() )

    # construct linear series for families of conics
    ring = PolyRing( 'x,y,v,w' )  # construct polynomial ring over new ground field
    OrbTools.p( ring )
    x, y, v, w = ring.gens()
    a0, a1 = ring.root_gens()

    p1 = [ 'xv', ( 0, 2 * a0 * a1 ) ]
    p2 = [ 'xv', ( 0, -2 * a0 * a1 ) ]
    p3 = [ 'xv', ( a1, 2 * a0 * a1 ) ]
    p4 = [ 'xv', ( -a1, -2 * a0 * a1 ) ]

    bpt_1234 = BasePointTree( ['xv', 'xw', 'yv', 'yw'] )
    bpt_1234.add( p1[0], p1[1], 1 )
    bpt_1234.add( p2[0], p2[1], 1 )
    bpt_1234.add( p3[0], p3[1], 1 )
    bpt_1234.add( p4[0], p4[1], 1 )

    bpt_12 = BasePointTree( ['xv', 'xw', 'yv', 'yw'] )
    bpt_12.add( p1[0], p1[1], 1 )
    bpt_12.add( p2[0], p2[1], 1 )

    bpt_34 = BasePointTree( ['xv', 'xw', 'yv', 'yw'] )
    bpt_34.add( p3[0], p3[1], 1 )
    bpt_34.add( p4[0], p4[1], 1 )

    ls_22 = LinearSeries.get( [2, 2], bpt_1234 )  # |2(l1+l2)-e1-e2-e3-e4|
    ls_21 = LinearSeries.get( [2, 1], bpt_1234 )
    ls_12 = LinearSeries.get( [1, 2], bpt_1234 )
    ls_11a = LinearSeries.get( [1, 1], bpt_12 )
    ls_11b = LinearSeries.get( [1, 1], bpt_34 )

    OrbTools.p( 'linear series 22 =\n', ls_22 )
    OrbTools.p( 'linear series 21 =\n', ls_21 )
    OrbTools.p( 'linear series 12 =\n', ls_12 )
    OrbTools.p( 'linear series 11a =\n', ls_11a )
    OrbTools.p( 'linear series 11b =\n', ls_11b )

    # compute reparametrization from the linear series of families
    ring = PolyRing( 'x,y,v,w,c0,s0,c1,s1' )  # construct polynomial ring with new generators
    OrbTools.p( ring )
    x, y, v, w, c0, s0, c1, s1 = ring.gens()
    a0, a1 = ring.root_gens()
    pmz_AB_lst = [1] + ring.coerce( pmz_AB_lst )
    pmz_lst = ring.coerce( pmz_lst )

    X = 1 - s0; Y = c0;
    V = 1 - s1; W = c1;
    CB_dct = {x:X, y:Y, v:W * X - 2 * a0 * V * Y, w:V * X + 2 * a0 * W * Y};
    pmz_CB_lst = [ pmz.subs( CB_dct ) for pmz in pmz_lst ]  # CB  11b

    # output
    OrbTools.p( 'pmz_AB_lst =\n', pmz_AB_lst )
    OrbTools.p( 'pmz_CB_lst =\n', pmz_CB_lst )

    # approximate by map defined over rational numbers
    ci_idx = 0  # index defining the complex embedding
    OrbTools.p( 'complex embeddings =' )
    for i in range( len( a0.complex_embeddings() ) ):
        a0q = OrbRing.approx_QQ_coef( a0, i )
        OrbTools.p( '\t\t' + str( i ) + ' =', a0q, sage_n( a0q ) )
    pmz_AB_lst = OrbRing.approx_QQ_pol_lst( pmz_AB_lst, ci_idx )
    pmz_CB_lst = OrbRing.approx_QQ_pol_lst( pmz_CB_lst, ci_idx )

    # mathematica input
    ms = ''
    for pmz, AB in [ ( pmz_lst, 'ZZ' ), ( pmz_AB_lst, 'AB' ), ( pmz_CB_lst, 'CB' ) ]:
        s = 'pmz' + AB + '=' + str( pmz ) + ';'
        s = s.replace( '[', '{' ).replace( ']', '}' )
        ms += '\n' + s
    OrbTools.p( 'Mathematica input =', ms )

    # PovInput ring cyclide
    #
    pin = PovInput()

    pin.path = './' + get_time_str() + '_CH1_cyclide/'
    pin.fname = 'orb'
    pin.scale = 1
    pin.cam_dct['location'] = ( 0, -5, 0 )
    pin.cam_dct['lookat'] = ( 0, 0, 0 )
    pin.cam_dct['rotate'] = ( 20, 0, 0 )
    pin.shadow = True
    pin.light_lst = [( 1, 0, 0 ), ( 0, 1, 0 ), ( 0, 0, 1 ),
                     ( -1, 0, 0 ), ( 0, -1, 0 ), ( 0, 0, -1 ),
                     ( 10, 0, 0 ), ( 0, 10, 0 ), ( 0, 0, 10 ),
                     ( -10, 0, 0 ), ( 0, -10, 0 ), ( 0, 0, -10 )]
    pin.axes_dct['show'] = False
    pin.axes_dct['len'] = 1.2
    pin.height = 400
    pin.width = 800
    pin.quality = 11
    pin.ani_delay = 10

    pin.impl = None

    pin.pmz_dct['A'] = ( pmz_AB_lst, 0 )
    pin.pmz_dct['B'] = ( pmz_AB_lst, 1 )
    pin.pmz_dct['C'] = ( pmz_CB_lst, 0 )

    pin.pmz_dct['FA'] = ( pmz_AB_lst, 0 )
    pin.pmz_dct['FB'] = ( pmz_AB_lst, 1 )
    pin.pmz_dct['FC'] = ( pmz_CB_lst, 0 )

    v0_lst = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 10 )]

    v1_lst_A = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 180, 360, 10 )]
    v1_lst_B = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 180, 10 )]
    v1_lst_C = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 180, 10 )]

    v1_lst_FA = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 180, 360, 2 )]
    v1_lst_FB = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 180, 2 )]
    v1_lst_FC = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 180, 2 )]

    prec = 50

    pin.curve_dct['A'] = {'step0':v0_lst, 'step1':v1_lst_A, 'prec':prec, 'width':0.03}
    pin.curve_dct['B'] = {'step0':v0_lst, 'step1':v1_lst_B, 'prec':prec, 'width':0.03}
    pin.curve_dct['C'] = {'step0':v0_lst, 'step1':v1_lst_C, 'prec':prec, 'width':0.03}

    pin.curve_dct['FA'] = {'step0':v0_lst, 'step1':v1_lst_FA, 'prec':prec, 'width':0.02}
    pin.curve_dct['FB'] = {'step0':v0_lst, 'step1':v1_lst_FB, 'prec':prec, 'width':0.02}
    pin.curve_dct['FC'] = {'step0':v0_lst, 'step1':v1_lst_FC, 'prec':prec, 'width':0.02}

    col_A = ( 0.6, 0.4, 0.1, 0.0 )
    col_B = ( 0.1, 0.15, 0.0, 0.0 )
    col_C = ( 0.2, 0.3, 0.2, 0.0 )
    colFF = ( 0.1, 0.1, 0.1, 0.0 )

    pin.text_dct['A'] = [True, col_A , 'phong 0.2 phong_size 5' ]
    pin.text_dct['B'] = [True, col_B , 'phong 0.2 phong_size 5' ]
    pin.text_dct['C'] = [True, col_C , 'phong 0.2 phong_size 5' ]
    pin.text_dct['FA'] = [True, colFF, 'phong 0.2 phong_size 5' ]
    pin.text_dct['FB'] = [True, colFF, 'phong 0.2 phong_size 5' ]
    pin.text_dct['FC'] = [True, colFF, 'phong 0.2 phong_size 5' ]

    # raytrace image/animation
    create_pov( pin, ['A', 'B', 'C'] )
    create_pov( pin, ['A', 'B', 'C', 'FA', 'FB', 'FC'] )
    create_pov( pin, ['A', 'B', 'FA', 'FB'] )
    create_pov( pin, ['B', 'C', 'FA', 'FB'] )

