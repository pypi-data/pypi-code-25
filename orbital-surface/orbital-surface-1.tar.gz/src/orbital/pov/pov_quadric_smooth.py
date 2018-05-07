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
from orbital.sage_interface import sage_pi

from orbital.class_orb_tools import OrbTools

from orbital.class_orb_ring import OrbRing

from orbital.povray.class_pov_input import PovInput
from orbital.povray.povray import create_pov
from orbital.povray.povray_aux import get_time_str
from orbital.povray.povray_aux import rgbt2pov


def quadric_smooth():
    '''
    Construct povray image of rulings on hyperboloid of one sheet.
    '''

    # construct the two rulings on the hyperboloid
    # by rotating lines L1 and L2
    c0, s0, c1, s1, t0 = OrbRing.coerce( 'c0,s0,c1,s1,t0' )
    P = sage_vector( [-2, -1, -0.5] )
    Q = sage_vector( [2, -1, -0.5] )
    L0 = t0 * P + ( t0 - 1 ) * Q;
    L1 = t0 * Q + ( t0 - 1 ) * P;
    M = sage_matrix( [( c1, s1, 0 ), ( -s1, c1, 0 ), ( 0, 0, 1 )] )
    pmz_A_lst = [1] + list( M * L0 )
    pmz_B_lst = [1] + list( M * L1 )

    OrbTools.p( 'pmz_A_lst =', pmz_A_lst )
    for pmz in pmz_A_lst: OrbTools.p( '\t\t', pmz )

    OrbTools.p( 'pmz_B_lst =', pmz_B_lst )
    for pmz in pmz_B_lst: OrbTools.p( '\t\t', pmz )

    # PovInput ring cyclide
    #
    pin = PovInput()

    pin.path = './' + get_time_str() + '_quadric_smooth/'
    pin.fname = 'orb'
    pin.scale = 1
    pin.cam_dct['location'] = ( 0, -10, 0 )
    pin.cam_dct['lookat'] = ( 0, 0, 0 )
    pin.cam_dct['rotate'] = ( 0, 0, 0 )
    pin.shadow = True
    pin.light_lst = [( 0, 0, -5 ), ( 0, -5, 0 ), ( -5, 0, 0 ),
                     ( 0, 0, 5 ), ( 0, 5, 0 ), ( 5, 0, 0 ) ]
    pin.axes_dct['show'] = False
    pin.axes_dct['len'] = 1.2

    pin.width = 400
    pin.height = 800
    pin.quality = 11
    pin.ani_delay = 10

    pin.impl = None

    pin.pmz_dct['A'] = ( pmz_A_lst, 0 )
    pin.pmz_dct['B'] = ( pmz_B_lst, 0 )
    pin.pmz_dct['FA'] = ( pmz_A_lst, 0 )
    pin.pmz_dct['FB'] = ( pmz_B_lst, 0 )

    v0_lst = [sage_QQ( i ) / 10 for i in range( -15, 30, 5 )]  # -15, 35
    v1_lst = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 36 )]
    v1_lst_F = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 2 )]

    pin.curve_dct['A'] = {'step0':v0_lst, 'step1':v1_lst, 'prec':10, 'width':0.1}
    pin.curve_dct['B'] = {'step0':v0_lst, 'step1':v1_lst, 'prec':10, 'width':0.1}
    pin.curve_dct['FA'] = {'step0':v0_lst, 'step1':v1_lst_F, 'prec':10, 'width':0.01}
    pin.curve_dct['FB'] = {'step0':v0_lst, 'step1':v1_lst_F, 'prec':10, 'width':0.01}

    col_A = ( 0.5, 0.0, 0.0, 0.0 )  # red
    col_B = rgbt2pov( ( 28, 125, 154, 0 ) )  # blue

    pin.text_dct['A'] = [True, col_A, 'phong 0.2 phong_size 5' ]
    pin.text_dct['B'] = [True, col_B, 'phong 0.2 phong_size 5' ]
    pin.text_dct['FA'] = [True, ( 0.1, 0.1, 0.1, 0.0 ), 'phong 0.2 phong_size 5' ]
    pin.text_dct['FB'] = [True, ( 0.1, 0.1, 0.1, 0.0 ), 'phong 0.2 phong_size 5' ]


    # raytrace image/animation
    create_pov( pin, ['A', 'B', 'FA', 'FB'] )


