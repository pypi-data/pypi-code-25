'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jan 16, 2018
@author: Niels Lubbes
'''

from orbital.sage_interface import sage_QQ
from orbital.sage_interface import sage_var
from orbital.sage_interface import sage_matrix
from orbital.sage_interface import sage_vector
from orbital.sage_interface import sage_factor
from orbital.sage_interface import sage_n
from orbital.sage_interface import sage_sqrt
from orbital.sage_interface import sage_pi

from orbital.class_orb_tools import OrbTools

from orbital.povray.class_pov_input import PovInput
from orbital.povray.povray import create_pov
from orbital.povray.povray_aux import get_time_str
from orbital.povray.povray_aux import rgbt2pov

from linear_series.class_poly_ring import PolyRing
from linear_series.class_base_points import BasePointTree
from linear_series.class_linear_series import LinearSeries



def ring_cyclide():
    '''
    Creates povray image of 4 families of circles on a ring cyclide. 
    '''

    # We construct a trigonometric parametrization of the ring cyclide,
    # by rotating a circle of radius r along a circle of radius R.
    R = 2; r = 1;
    x, y, v, w, c0, s0, c1, s1 = sage_var( 'x,y,v,w,c0,s0,c1,s1' )
    V = sage_vector( [r * c0 + R, 0, r * s0] )
    M = sage_matrix( [( c1, -s1, 0 ), ( s1, c1, 0 ), ( 0, 0, 1 )] )
    pmz_AB_lst = [1] + list( M * V )
    OrbTools.p( 'pmz_AB_lst =', pmz_AB_lst )
    for pmz in pmz_AB_lst:
        OrbTools.p( '\t\t', sage_factor( pmz ) )

    # convert pmz_AB_lst to rational parametrization pmz_lst
    C0 = ( y ** 2 - x ** 2 ) / ( y ** 2 + x ** 2 )
    S0 = 2 * x * y / ( y ** 2 + x ** 2 )
    C1 = ( w ** 2 - v ** 2 ) / ( w ** 2 + v ** 2 )
    S1 = 2 * v * w / ( w ** 2 + v ** 2 )
    den = ( y ** 2 + x ** 2 ) * ( w ** 2 + v ** 2 )
    dct = {c0:C0, s0:S0, c1:C1, s1:S1 }
    pmz_lst = [den] + [ ( elt.subs( dct ) * den ).simplify_full() for elt in list( M * V ) ]
    OrbTools.p( 'pmz_lst =', pmz_lst )

    # find basepoints
    ls = LinearSeries( pmz_lst, PolyRing( 'x,y,v,w' , True ) )
    OrbTools.p( ls.get_bp_tree() )

    # construct linear series for families of conics
    a0, a1 = PolyRing( 'x,y,v,w' ).ext_num_field( 't^2+1/3' ).ext_num_field( 't^2+1' ).root_gens()

    p1 = [ 'xv', ( -a0, a1 ) ]
    p2 = [ 'xv', ( a0, -a1 ) ]
    p3 = [ 'xv', ( -a0, -a1 ) ]
    p4 = [ 'xv', ( a0, a1 ) ]

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

    # compute reparametrization
    ring = PolyRing( 'x,y,v,w,c0,s0,c1,s1' )  # construct polynomial ring with new generators
    pmz_lst = ring.coerce( pmz_lst )
    x, y, v, w, c0, s0, c1, s1 = ring.gens()
    X = 1 - s0; Y = c0;  # see get_S1xS1_pmz()
    V = 1 - s1; W = c1;
    q = sage_n( sage_sqrt( 3 ) ).exact_rational()  # approximation of sqrt(3)
    CB_dct = { x:X, y:Y, v: W * X + q * V * Y, w: V * X - q * W * Y }
    DB_dct = { x:X, y:Y, v: W * X - q * V * Y, w: V * X + q * W * Y }
    pmz_CB_lst = [ pmz.subs( CB_dct ) for pmz in pmz_lst ]
    pmz_DB_lst = [ pmz.subs( DB_dct ) for pmz in pmz_lst ]

    # output
    OrbTools.p( 'pmz_AB_lst =\n', pmz_AB_lst )
    OrbTools.p( 'pmz_CB_lst =\n', pmz_CB_lst )
    OrbTools.p( 'pmz_DB_lst =\n', pmz_DB_lst )

    # mathematica
    for pmz, AB in [ ( pmz_AB_lst, 'AB' ), ( pmz_CB_lst, 'CB' ), ( pmz_DB_lst, 'DB' )]:
        s = 'pmz' + AB + '=' + str( pmz ) + ';'
        s = s.replace( '[', '{' ).replace( ']', '}' )
        print( s )

    # PovInput ring cyclide
    #
    pin = PovInput()

    pin.path = './' + get_time_str() + '_ring_cyclide/'
    pin.fname = 'orb'
    pin.scale = 1
    pin.cam_dct['location'] = ( 0, -7, 0 )
    pin.cam_dct['lookat'] = ( 0, 0, 0 )
    pin.cam_dct['rotate'] = ( 55, 0, 0 )  # 45
    pin.shadow = True
    pin.light_lst = [( 0, 0, -5 ), ( 0, -5, 0 ), ( -5, 0, 0 ),
                     ( 0, 0, 5 ), ( 0, 5, 0 ), ( 5, 0, 0 ),
                     ( -5, -5, -5 ), ( 5, -5, 5 ), ( -5, -5, 5 ), ( 5, -5, -5 ) ]
    pin.axes_dct['show'] = False
    pin.axes_dct['len'] = 1.2
    pin.width = 800
    pin.height = 400
    pin.quality = 11
    pin.ani_delay = 10

    pin.impl = None

    pin.pmz_dct['A'] = ( pmz_AB_lst, 0 )
    pin.pmz_dct['B'] = ( pmz_AB_lst, 1 )
    pin.pmz_dct['C'] = ( pmz_CB_lst, 0 )
    pin.pmz_dct['D'] = ( pmz_DB_lst, 0 )
    pin.pmz_dct['FA'] = ( pmz_AB_lst, 0 )
    pin.pmz_dct['FB'] = ( pmz_AB_lst, 1 )
    pin.pmz_dct['FC'] = ( pmz_CB_lst, 0 )
    pin.pmz_dct['FD'] = ( pmz_DB_lst, 0 )
    pin.pmz_dct['WA'] = ( pmz_AB_lst, 0 )
    pin.pmz_dct['WB'] = ( pmz_AB_lst, 1 )
    pin.pmz_dct['WC'] = ( pmz_CB_lst, 0 )
    pin.pmz_dct['WD'] = ( pmz_DB_lst, 0 )

    v0_lst = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 10 )]
    v1_lst = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 24 )]

    v1_lst_A = [ sage_pi / 2 + ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 12 )]
    v1_lstFF = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 1 )]

    v1_lst_WA = [0.1, 0.52, 0.94, 1.36, 1.78, 2.2, 2.61, 3.04, 3.45, 3.88, 4.3, 4.712, 5.13, 5.55, 5.965]
    v1_lst_WB = [0, 0.7, 1.31, 1.8, 2.18, 2.5, 2.77, 3.015, 3.26, 3.51, 3.78, 4.099, 4.49, 4.97, 5.579];
    v1_lst_WD = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 24 )]
    v1_lst_WC = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 24 )]

    pin.curve_dct['A'] = {'step0':v0_lst, 'step1':v1_lst_A, 'prec':10, 'width':0.05}
    pin.curve_dct['B'] = {'step0':v0_lst, 'step1':v1_lst, 'prec':10, 'width':0.05}
    pin.curve_dct['C'] = {'step0':v0_lst, 'step1':v1_lst, 'prec':10, 'width':0.05}
    pin.curve_dct['D'] = {'step0':v0_lst, 'step1':v1_lst, 'prec':10, 'width':0.05}
    pin.curve_dct['FA'] = {'step0':v0_lst, 'step1':v1_lstFF, 'prec':10, 'width':0.02}
    pin.curve_dct['FB'] = {'step0':v0_lst, 'step1':v1_lstFF, 'prec':10, 'width':0.02}
    pin.curve_dct['FC'] = {'step0':v0_lst, 'step1':v1_lstFF, 'prec':10, 'width':0.02}
    pin.curve_dct['FD'] = {'step0':v0_lst, 'step1':v1_lstFF, 'prec':10, 'width':0.02}
    pin.curve_dct['WA'] = {'step0':v0_lst, 'step1':v1_lst_WA, 'prec':10, 'width':0.05}
    pin.curve_dct['WB'] = {'step0':v0_lst, 'step1':v1_lst_WB, 'prec':10, 'width':0.05}
    pin.curve_dct['WC'] = {'step0':v0_lst, 'step1':v1_lst_WC, 'prec':10, 'width':0.05}
    pin.curve_dct['WD'] = {'step0':v0_lst, 'step1':v1_lst_WD, 'prec':10, 'width':0.05}


    # A = | rotated circle
    # B = - horizontal circle
    # C = / villarceau circle
    # D = \ villarceau circle
    col_A = rgbt2pov( ( 28, 125, 154, 0 ) )  # blue
    col_B = rgbt2pov( ( 74, 33, 0, 0 ) )  # brown
    col_C = rgbt2pov( ( 75, 102, 0, 0 ) )  # green
    col_D = rgbt2pov( ( 187, 46, 0, 0 ) )  # red/orange
    colFF = rgbt2pov( ( 179, 200, 217, 0 ) )  # light blue

    pin.text_dct['A'] = [True, col_A, 'phong 0.2 phong_size 5' ]
    pin.text_dct['B'] = [True, col_B, 'phong 0.2 phong_size 5' ]
    pin.text_dct['C'] = [True, col_C, 'phong 0.2 phong_size 5' ]
    pin.text_dct['D'] = [True, col_D, 'phong 0.2 phong_size 5' ]
    pin.text_dct['FA'] = [True, colFF, 'phong 0.2 phong_size 5' ]
    pin.text_dct['FB'] = [True, colFF, 'phong 0.2 phong_size 5' ]
    pin.text_dct['FC'] = [True, colFF, 'phong 0.2 phong_size 5' ]
    pin.text_dct['FD'] = [True, colFF, 'phong 0.2 phong_size 5' ]
    pin.text_dct['WA'] = [True, col_A, 'phong 0.2 phong_size 5' ]
    pin.text_dct['WB'] = [True, col_B, 'phong 0.2 phong_size 5' ]
    pin.text_dct['WC'] = [True, col_C, 'phong 0.2 phong_size 5' ]
    pin.text_dct['WD'] = [True, col_D, 'phong 0.2 phong_size 5' ]


    # raytrace image/animation
    create_pov( pin, ['A', 'C', 'D'] )
    create_pov( pin, ['A', 'C', 'D'] + ['FA', 'FC', 'FD'] )

    create_pov( pin, ['WA', 'WB', 'WC', 'WD'] )
    create_pov( pin, ['WA', 'WB', 'WC', 'WD'] + ['FA', 'FC', 'FD'] )

    create_pov( pin, ['WA', 'WB', 'WD'] )
    create_pov( pin, ['WA', 'WB', 'WD'] + ['FA', 'FC', 'FD'] )


