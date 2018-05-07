'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jan 16, 2018
@author: Niels Lubbes
'''

from orbital.sage_interface import sage_QQ
from orbital.sage_interface import sage_var
from orbital.sage_interface import sage_vector
from orbital.sage_interface import sage_pi

from orbital.surface_in_quadric import get_surf
from orbital.surface_in_quadric import approx_QQ
from orbital.surface_in_quadric import get_prj_mat
from orbital.surface_in_quadric import get_proj
from orbital.surface_in_quadric import get_S1xS1_pmz

from orbital.povray.class_pov_input import PovInput
from orbital.povray.povray import create_pov
from orbital.povray.povray_aux import get_time_str
from orbital.povray.povray_aux import rgbt2pov

from linear_series.class_linear_series import LinearSeries
from linear_series.class_base_points import BasePointTree
from linear_series.class_poly_ring import PolyRing



def dp6_smooth():
    '''
    Creates povray image of the projection of a smooth sextic del Pezzo 
    surface in S^5. This surface contains 3 families of conics that 
    form a hexagonal web. 
    '''

    # compute parametrizations of canonical model
    a0 = PolyRing( 'x,y,v,w', True ).ext_num_field( 't^2 + 1' ).root_gens()[0]
    bp_tree = BasePointTree( ['xv', 'xw', 'yv', 'yw'] )
    bp = bp_tree.add( 'xv', ( -a0, a0 ), 1 )
    bp = bp_tree.add( 'xv', ( a0, -a0 ), 1 )
    ls_AB = LinearSeries.get( [2, 2], bp_tree )
    ls_CB = LinearSeries.get( [1, 1], bp_tree )

    # compute surface in quadric of signature (6,1)
    c_lst = [-1, -1, 0, 0, 0, -1, 1, 0, -1, -1, -1]
    dct = get_surf( ls_AB, ( 6, 1 ), c_lst )

    # compute projection to P^3
    U, J = dct['UJ']
    U.swap_rows( 0, 6 );J.swap_columns( 0, 6 );J.swap_rows( 0, 6 )
    approxU = approx_QQ( U )
    P = get_prj_mat( 4, 7, 0 )
    P[0, 6] = -1;P[3, 3] = 0;P[3, 4] = 1
    P = P * approxU
    f_xyz, pmz_AB_lst = get_proj( dct['imp_lst'], dct['pmz_lst'], P )

    # compute reparametrization
    ring = PolyRing( 'x,y,v,w,c0,s0,c1,s1' )  # construct polynomial ring with new generators
    x, y, v, w, c0, s0, c1, s1 = ring.gens()
    X = 1 - s0; Y = c0;  # see get_S1xS1_pmz()
    V = 1 - s1; W = c1;
    CB_dct = { x:X, y:Y, v:X * W + Y * V, w: X * V - Y * W }
    pmz_CB_lst = [ p.subs( CB_dct ) for p in ring.coerce( ls_AB.pol_lst )]
    pmz_CB_lst = list( P * dct['Q'] * sage_vector( pmz_CB_lst ) )

    # set PovInput as container
    # put very low quality for testing purposes
    pin = PovInput()

    pin.path = './' + get_time_str() + '_dp6_smooth/'
    pin.fname = 'orb'
    pin.scale = 1
    pin.cam_dct['location'] = ( 0, 0, sage_QQ( -21 ) / 10 )
    pin.cam_dct['lookat'] = ( 0, 0, 0 )
    pin.cam_dct['rotate'] = ( 310, 0, 0 )
    pin.shadow = True
    pin.light_lst = [( 0, 0, -4 ), ( 0, -4, 0 ), ( -4, 0, 0 ), ( 0, 4, 0 ), ( 4, 0, 0 ),
                     ( -5, -5, -5 ), ( 5, 5, -5 ), ( -5, 5, -5 ), ( 5, -5, -5 ) ]
    pin.axes_dct['show'] = False
    pin.axes_dct['len'] = 1.2
    pin.height = 400
    pin.width = 800
    pin.quality = 11
    pin.ani_delay = 1
    pin.impl = None

    v0_lst = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 10 )]
    v1_lst = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 15 )]
    v1_F_lst = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 1 )]

    pin.pmz_dct['A'] = ( pmz_AB_lst, 0 )
    pin.pmz_dct['B'] = ( pmz_AB_lst, 1 )
    pin.pmz_dct['C'] = ( pmz_CB_lst, 0 )
    pin.pmz_dct['FA'] = ( pmz_AB_lst, 0 )
    pin.pmz_dct['FB'] = ( pmz_AB_lst, 1 )
    pin.pmz_dct['FC'] = ( pmz_CB_lst, 0 )

    pin.curve_dct['A'] = {'step0':v0_lst, 'step1':v1_lst, 'prec':10, 'width':0.018}
    pin.curve_dct['B'] = {'step0':v0_lst, 'step1':v1_lst, 'prec':10, 'width':0.018}
    pin.curve_dct['C'] = {'step0':v0_lst, 'step1':v1_lst, 'prec':10, 'width':0.018}
    pin.curve_dct['FA'] = {'step0':v0_lst, 'step1':v1_F_lst, 'prec':10, 'width':0.003}
    pin.curve_dct['FB'] = {'step0':v0_lst, 'step1':v1_F_lst, 'prec':10, 'width':0.003}
    pin.curve_dct['FC'] = {'step0':v0_lst, 'step1':v1_F_lst, 'prec':10, 'width':0.003}

    # ( 0.4, 0.0, 0.0, 0.0 ), ( 0.2, 0.3, 0.2, 0.0 ), ( 0.8, 0.6, 0.2, 0.0 )
    col_A = rgbt2pov( ( 75, 102, 0, 0 ) )  # green /
    col_B = rgbt2pov( ( 74, 33, 0, 0 ) )  # brown -
    col_C = rgbt2pov( ( 28, 125, 154, 0 ) )  # blue \
    colFF = rgbt2pov( ( 179, 200, 217, 0 ) )  # light blue

    pin.text_dct['A'] = [True, col_A, 'phong 0.2' ]
    pin.text_dct['B'] = [True, col_B, 'phong 0.2' ]
    pin.text_dct['C'] = [True, col_C, 'phong 0.2' ]
    pin.text_dct['FA'] = [True, colFF, 'phong 0.8' ]
    pin.text_dct['FB'] = [True, colFF, 'phong 0.8' ]
    pin.text_dct['FC'] = [True, colFF, 'phong 0.8' ]

    # raytrace image/animation
    create_pov( pin, ['A', 'B', 'C'] )
    create_pov( pin, ['A', 'B', 'C', 'FA', 'FB', 'FC'] )
    create_pov( pin, ['A', 'FA', 'FB', 'FC'] )
    create_pov( pin, ['B', 'FA', 'FB', 'FC'] )
    create_pov( pin, ['C', 'FA', 'FB', 'FC'] )



