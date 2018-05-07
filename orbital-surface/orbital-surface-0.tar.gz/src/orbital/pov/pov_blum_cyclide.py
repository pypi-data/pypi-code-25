'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jan 16, 2018
@author: Niels Lubbes
'''

from orbital.sage_interface import sage_QQ
from orbital.sage_interface import sage_PolynomialRing
from orbital.sage_interface import sage_var
from orbital.sage_interface import sage_identity_matrix
from orbital.sage_interface import sage_invariant_theory
from orbital.sage_interface import sage_matrix
from orbital.sage_interface import sage_vector
from orbital.sage_interface import sage_pi

from orbital.class_orb_tools import OrbTools

from orbital.surface_in_quadric import approx_QQ
from orbital.surface_in_quadric import get_surf
from orbital.surface_in_quadric import get_proj

from orbital.povray.class_pov_input import PovInput
from orbital.povray.povray import create_pov
from orbital.povray.povray_aux import get_time_str
from orbital.povray.povray_aux import rgbt2pov

from linear_series.class_poly_ring import PolyRing
from linear_series.class_base_points import BasePointTree
from linear_series.class_linear_series import LinearSeries


def blum_cyclide():
    '''
    Construct a povray image of 6 families of circles on a smooth Darboux cyclide.
    This surface is also known as the Blum cyclide.
    '''

    # construct dct
    a0 = PolyRing( 'x,y,v,w', True ).ext_num_field( 't^2 + 1' ).root_gens()[0]  # i

    bpt_1234 = BasePointTree( ['xv', 'xw', 'yv', 'yw'] )
    bpt_1234.add( 'xv', ( -1 * a0, 1 * a0 ), 1 )  # e1
    bpt_1234.add( 'xv', ( 1 * a0, -1 * a0 ), 1 )  # e2
    bpt_1234.add( 'xw', ( -2 * a0, 2 * a0 ), 1 )  # e3
    bpt_1234.add( 'xw', ( 2 * a0, -2 * a0 ), 1 )  # e4

    bpt_12 = BasePointTree( ['xv', 'xw', 'yv', 'yw'] )
    bpt_12.add( 'xv', ( -1 * a0, 1 * a0 ), 1 )  # e1
    bpt_12.add( 'xv', ( 1 * a0, -1 * a0 ), 1 )  # e2

    bpt_34 = BasePointTree( ['xv', 'xw', 'yv', 'yw'] )
    bpt_34.add( 'xw', ( -2 * a0, 2 * a0 ), 1 )  # e3
    bpt_34.add( 'xw', ( 2 * a0, -2 * a0 ), 1 )  # e4

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

    sig = ( 4, 1 )
    pol_lst = ls_22.get_implicit_image()

    # determine signature
    x_lst = sage_PolynomialRing( sage_QQ, [ 'x' + str( i ) for i in range( sum( sig ) )] ).gens()
    for pol in pol_lst:

        if pol.degree() == 2:
            M = sage_invariant_theory.quadratic_form( pol, x_lst ).as_QuadraticForm().matrix()
            D, V = sage_matrix( sage_QQ, M ).eigenmatrix_right()  # D has first all negative values on diagonal
            cur_sig = ( len( [ d for d in D.diagonal() if d < 0 ] ), len( [ d for d in D.diagonal() if d > 0 ] ) )
        else:
            cur_sig = '[no signature]'
        OrbTools.p( '\t\t', pol, cur_sig )

    # obtain surface in sphere
    coef_lst = [0, -1, -1]
    dct = get_surf( ls_22, sig, coef_lst )

    # construct projection matrix P
    U, J = dct['UJ']
    U.swap_rows( 0, 4 )
    J.swap_columns( 0, 4 )
    J.swap_rows( 0, 4 )
    assert dct['M'] == approx_QQ( U.T * J * U )
    approxU = approx_QQ( U )
    P = sage_identity_matrix( 5 ).submatrix( 0, 0, 4, 5 )
    P[0, 4] = -1;
    P = P * approxU
    OrbTools.p( ' approx_QQ( U ) =', list( approx_QQ( U ) ) )
    OrbTools.p( ' approx_QQ( J ) =', list( approx_QQ( J ) ) )
    OrbTools.p( ' P              =', list( P ) )

    # call get_proj
    f_xyz, pmz_AB_lst = get_proj( dct['imp_lst'], dct['pmz_lst'], P )
    f_xyz_deg_lst = [f_xyz.degree( sage_var( v ) ) for v in ['x', 'y', 'z']]

    # compute reparametrization
    ring = PolyRing( 'x,y,v,w,c0,s0,c1,s1' )  # construct polynomial ring with new generators
    p_lst = ring.coerce( ls_22.pol_lst )
    x, y, v, w, c0, s0, c1, s1 = ring.gens()
    X = 1 - s0; Y = c0;  # see get_S1xS1_pmz()
    V = 1 - s1; W = c1;
    CB_dct = { x:X, y:Y, v:X * W + Y * V, w: X * V - Y * W }
    DB_dct = { x:X, y:Y, v:4 * X * W - Y * V, w: X * V + Y * W }
    EB_dct = { x:X, y:Y, v:40 * W * X ** 2 + 25 * W * Y ** 2 + 24 * V * X * Y, w:40 * V * X ** 2 + 16 * V * Y ** 2 - 15 * W * X * Y  }
    AF_dct = { x:-10 * Y * V ** 2 - 25 * Y * W ** 2 + 9 * X * V * W, y:15 * X * V ** 2 + 24 * X * W ** 2 - 15 * Y * V * W, v:V, w:W  }
    pmz_CB_lst = list( P * sage_vector( [ p.subs( CB_dct ) for p in p_lst] ) )
    pmz_DB_lst = list( P * sage_vector( [ p.subs( DB_dct ) for p in p_lst] ) )
    pmz_EB_lst = list( P * sage_vector( [ p.subs( EB_dct ) for p in p_lst] ) )
    pmz_AF_lst = list( P * sage_vector( [ p.subs( AF_dct ) for p in p_lst] ) )


    # output
    OrbTools.p( 'f_xyz =', f_xyz_deg_lst, '\n', f_xyz )
    OrbTools.p( 'pmz_AB_lst =\n', pmz_AB_lst )
    OrbTools.p( 'pmz_CB_lst =\n', pmz_CB_lst )
    OrbTools.p( 'pmz_DB_lst =\n', pmz_DB_lst )
    OrbTools.p( 'pmz_EB_lst =\n', pmz_EB_lst )
    OrbTools.p( 'pmz_AF_lst =\n', pmz_AF_lst )

    # mathematica
    pmz_lst = [ ( pmz_AB_lst, 'AB' ),
                ( pmz_CB_lst, 'CB' ),
                ( pmz_DB_lst, 'DB' ),
                ( pmz_EB_lst, 'EB' ),
                ( pmz_AF_lst, 'AF' )]

    OrbTools.p( 'Mathematica input for ParametricPlot3D:' )
    for pmz, AB in pmz_lst:
        s = 'pmz' + AB + '=' + str( pmz )
        s = s.replace( '[', '{' ).replace( ']', '}' )
        print( s )

    # PovInput for Blum cyclide
    #
    pin = PovInput()
    pin.path = './' + get_time_str() + '_blum_cyclide/'
    pin.fname = 'orb'
    pin.scale = 1
    pin.cam_dct['location'] = ( 0, -7, 0 )
    pin.cam_dct['lookat'] = ( 0, 0, 0 )
    pin.cam_dct['rotate'] = ( 20, 180, 20 )
    pin.shadow = True
    pin.light_lst = [( 0, 0, -5 ), ( 0, -5, 0 ), ( -5, 0, 0 ),
                     ( 0, 0, 5 ), ( 0, 5, 0 ), ( 5, 0, 0 ),
                     ( -5, -5, -5 ), ( 5, -5, 5 ), ( -5, -5, 5 ), ( 5, -5, -5 ) ]
    pin.axes_dct['show'] = False
    pin.axes_dct['len'] = 1.2
    pin.height = 400
    pin.width = 800
    pin.quality = 11
    pin.ani_delay = 10
    pin.impl = None

    start0 = sage_QQ( 1 ) / 10  # step0=10 step1=15
    v0_lst = [ start0 + ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 10 )]
    v1_lst = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 15 )]
    v1_lst_F = [ start0 + ( sage_QQ( i ) / 360 ) * sage_pi for i in range( 0, 720, 1 )]

    v1_lst_WE = [1.8, 2.3, 2.7, 3.1, 3.5, 3.8, 4.134, 4.31, 4.532, 4.7, 4.9, 5.08, 5.25, 5.405, 5.553, 5.7, 5.84]
    v1_lst_WF = [1.69, 1.87, 2.07, 2.26, 2.5, 2.72, 2.96, 3.2, 3.42, 3.65, 3.81]
    v1_lst_WD = [ 5.44, 5.56, 5.68, 5.81, 5.95, 6.1, 6.27, 6.474]  # [5.01, 5.12, 5.22, 5.32,

    v1_lst_SA = [6.5]; v1_lst_SE = [5.4];
    v1_lst_SB = [5.95]; v1_lst_SF = [2.28];
    v1_lst_SC = [4.83]; v1_lst_SD = [5.55];

    pin.pmz_dct['A'] = ( pmz_AB_lst, 0 )
    pin.pmz_dct['B'] = ( pmz_AB_lst, 1 )
    pin.pmz_dct['C'] = ( pmz_CB_lst, 0 )
    pin.pmz_dct['D'] = ( pmz_DB_lst, 0 )
    pin.pmz_dct['E'] = ( pmz_EB_lst, 0 )
    pin.pmz_dct['F'] = ( pmz_AF_lst, 1 )
    pin.pmz_dct['WD'] = ( pmz_DB_lst, 0 )
    pin.pmz_dct['WE'] = ( pmz_EB_lst, 0 )
    pin.pmz_dct['WF'] = ( pmz_AF_lst, 1 )
    pin.pmz_dct['SA'] = ( pmz_AB_lst, 0 )
    pin.pmz_dct['SB'] = ( pmz_AB_lst, 1 )
    pin.pmz_dct['SC'] = ( pmz_CB_lst, 0 )
    pin.pmz_dct['SD'] = ( pmz_DB_lst, 0 )
    pin.pmz_dct['SE'] = ( pmz_EB_lst, 0 )
    pin.pmz_dct['SF'] = ( pmz_AF_lst, 1 )
    pin.pmz_dct['FA'] = ( pmz_AB_lst, 0 )
    pin.pmz_dct['FB'] = ( pmz_AB_lst, 1 )
    pin.pmz_dct['FC'] = ( pmz_CB_lst, 0 )
    pin.pmz_dct['FD'] = ( pmz_DB_lst, 0 )
    pin.pmz_dct['FE'] = ( pmz_EB_lst, 0 )
    pin.pmz_dct['FF'] = ( pmz_AF_lst, 1 )

    pin.curve_dct['A'] = {'step0':v0_lst, 'step1':v1_lst, 'prec':10, 'width':0.05}
    pin.curve_dct['B'] = {'step0':v0_lst, 'step1':v1_lst, 'prec':10, 'width':0.05}
    pin.curve_dct['C'] = {'step0':v0_lst, 'step1':v1_lst, 'prec':10, 'width':0.05}
    pin.curve_dct['D'] = {'step0':v0_lst, 'step1':v1_lst, 'prec':10, 'width':0.05}
    pin.curve_dct['E'] = {'step0':v0_lst, 'step1':v1_lst, 'prec':10, 'width':0.05}
    pin.curve_dct['F'] = {'step0':v0_lst, 'step1':v1_lst, 'prec':10, 'width':0.05}

    pin.curve_dct['WD'] = {'step0':v0_lst, 'step1':v1_lst_WD, 'prec':10, 'width':0.05}
    pin.curve_dct['WE'] = {'step0':v0_lst, 'step1':v1_lst_WE, 'prec':10, 'width':0.05}
    pin.curve_dct['WF'] = {'step0':v0_lst, 'step1':v1_lst_WF, 'prec':10, 'width':0.05}

    pin.curve_dct['SA'] = {'step0':v0_lst, 'step1':v1_lst_SA, 'prec':10, 'width':0.05}
    pin.curve_dct['SB'] = {'step0':v0_lst, 'step1':v1_lst_SB, 'prec':10, 'width':0.05}
    pin.curve_dct['SC'] = {'step0':v0_lst, 'step1':v1_lst_SC, 'prec':10, 'width':0.05}
    pin.curve_dct['SD'] = {'step0':v0_lst, 'step1':v1_lst_SD, 'prec':10, 'width':0.06}
    pin.curve_dct['SE'] = {'step0':v0_lst, 'step1':v1_lst_SE, 'prec':10, 'width':0.05}
    pin.curve_dct['SF'] = {'step0':v0_lst, 'step1':v1_lst_SF, 'prec':10, 'width':0.05}

    pin.curve_dct['FA'] = {'step0':v0_lst, 'step1':v1_lst_F, 'prec':10, 'width':0.01}
    pin.curve_dct['FB'] = {'step0':v0_lst, 'step1':v1_lst_F, 'prec':10, 'width':0.01}
    pin.curve_dct['FC'] = {'step0':v0_lst, 'step1':v1_lst_F, 'prec':10, 'width':0.01}
    pin.curve_dct['FD'] = {'step0':v0_lst, 'step1':v1_lst_F, 'prec':10, 'width':0.01}
    pin.curve_dct['FE'] = {'step0':v0_lst, 'step1':v1_lst_F, 'prec':10, 'width':0.01}
    pin.curve_dct['FF'] = {'step0':v0_lst, 'step1':v1_lst_F, 'prec':10, 'width':0.01}

    col_A = rgbt2pov( ( 28, 125, 154, 0 ) )  # blue
    col_B = rgbt2pov( ( 74, 33, 0, 0 ) )  # brown
    col_C = rgbt2pov( ( 75, 102, 0, 0 ) )  # green
    col_E = col_A
    col_F = col_B
    col_D = col_C
    colFF = rgbt2pov( ( 179, 200, 217, 0 ) )  # light blue

    pin.text_dct['A'] = [True, col_A, 'phong 0.2' ]
    pin.text_dct['B'] = [True, col_B, 'phong 0.2' ]
    pin.text_dct['C'] = [True, col_C, 'phong 0.2' ]
    pin.text_dct['E'] = [True, col_E, 'phong 0.2' ]
    pin.text_dct['F'] = [True, col_F, 'phong 0.2' ]
    pin.text_dct['D'] = [True, col_D, 'phong 0.2' ]
    pin.text_dct['WE'] = [True, col_E, 'phong 0.2' ]
    pin.text_dct['WF'] = [True, col_F, 'phong 0.2' ]
    pin.text_dct['WD'] = [True, col_D, 'phong 0.2' ]
    pin.text_dct['SA'] = [True, col_A, 'phong 0.2' ]
    pin.text_dct['SB'] = [True, col_B, 'phong 0.2' ]
    pin.text_dct['SC'] = [True, col_C, 'phong 0.2' ]
    pin.text_dct['SE'] = [True, col_E, 'phong 0.2' ]
    pin.text_dct['SF'] = [True, col_F, 'phong 0.2' ]
    pin.text_dct['SD'] = [True, col_D, 'phong 0.2' ]
    pin.text_dct['FA'] = [True, colFF, 'phong 0.2' ]
    pin.text_dct['FB'] = [True, colFF, 'phong 0.2' ]
    pin.text_dct['FC'] = [True, colFF, 'phong 0.2' ]
    pin.text_dct['FE'] = [True, colFF, 'phong 0.2' ]
    pin.text_dct['FF'] = [True, colFF, 'phong 0.2' ]
    pin.text_dct['FD'] = [True, colFF, 'phong 0.2' ]

    # raytrace image/animation
    F_lst = ['FA', 'FB', 'FC']
    S_lst = ['SA', 'SB', 'SC', 'SD', 'SE', 'SF']
    create_pov( pin, ['A', 'B', 'C'] )
    create_pov( pin, ['A', 'B', 'C'] + F_lst )
    create_pov( pin, ['WD', 'WE', 'WF'] )
    create_pov( pin, ['WD', 'WE', 'WF'] + F_lst )
    create_pov( pin, S_lst + F_lst )

    # ABC - EFD
    create_pov( pin, ['A', 'B'] + F_lst )
    create_pov( pin, ['E', 'F'] + F_lst )






