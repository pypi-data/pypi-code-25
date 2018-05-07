'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jan 21, 2018
@author: Niels Lubbes
'''

from orbital.sage_interface import sage_var
from orbital.sage_interface import sage_factor
from orbital.sage_interface import sage_QQ
from orbital.sage_interface import sage_pi

from orbital.class_orb_tools import OrbTools

from orbital.povray.class_pov_input import PovInput
from orbital.povray.povray import create_pov
from orbital.povray.povray_aux import get_time_str


def veronese():
    '''
    Construct povray image of a 3-web of conics on the Veronese surface.
    '''

    #############################################
    # Construct projection of Veronese surface. #
    #############################################

    c0, s0, c1, s1, t0 = sage_var( 'c0,s0,c1,s1,t0' )
    x, y = sage_var( 'x,y' )

    pmz_A_lst = [ 1, c0 * s0 * s1, c0 * s0 * c1, c0 * c0 * c1 * s1 ]

    P1 = c0 / ( s0 - 1 )
    P2 = c1 / ( s1 - 1 )
    P3 = ( s0 / c0 ) * ( c1 / ( s1 - 1 ) )

    dct_CD = {x:P1, y:P2 }
    den_CD = ( s0 - 1 ) ** 2 * ( s1 - 1 ) ** 2

    dct_ED = {x:P3, y:P2 }
    den_ED = c0 ** 2 * ( s1 - 1 ) ** 2

    pmz_lst = [ x ** 2 + y ** 2 + 1, -x, -x * y, y ]
    pmz_B_lst = [ ( pmz.subs( dct_CD ) * den_CD ).expand() for pmz in pmz_lst  ]
    pmz_C_lst = [ ( pmz.subs( dct_ED ) * den_ED ).expand() for pmz in pmz_lst  ]

    # parametrization of circles
    #
    pmz_C1_lst = [ pmz.subs( {x:t0, y:-t0 - 1} ) for pmz in pmz_lst ]
    pmz_C2_lst = [ pmz.subs( {x:t0, y:-t0 + 1} ) for pmz in pmz_lst ]
    pmz_C3_lst = [ pmz.subs( {x:t0, y:t0 + 1} ) for pmz in pmz_lst ]
    pmz_C4_lst = [ pmz.subs( {x:t0, y:t0 - 1} ) for pmz in pmz_lst ]

    # output
    #
    lst_lst = [( 'A', pmz_A_lst ), ( 'B', pmz_B_lst ), ( 'C', pmz_C_lst )]
    lst_lst += [( 'C1', pmz_C1_lst ), ( 'C2', pmz_C2_lst ), ( 'C3', pmz_C3_lst ), ( 'C4', pmz_C4_lst ), ]
    for A, pmz_lst in lst_lst:
        OrbTools.p( 'pmz_' + A + '_lst =', pmz_lst )
        for pmz in pmz_lst:
            OrbTools.p( '\t\t', sage_factor( pmz ) )


    #############################
    # PovInput Veronese surface #
    #############################

    pin = PovInput()

    pin.path = './' + get_time_str() + '_veronese/'
    pin.fname = 'orb'
    pin.scale = 1
    pin.cam_dct['location'] = ( 0, -1.2, 0 )
    pin.cam_dct['lookat'] = ( 0, 0, 0 )
    pin.cam_dct['rotate'] = ( 35, 0, 45 )
    pin.shadow = True
    pin.light_lst = [( 0, 0, -5 ), ( 0, -5, 0 ), ( -5, 0, 0 ),
                     ( 0, 0, 5 ), ( 0, 5, 0 ), ( 5, 0, 0 ) ]
    pin.axes_dct['show'] = False
    pin.axes_dct['len'] = 0.5
    pin.height = 400
    pin.width = 800
    pin.quality = 11
    pin.ani_delay = 10

    pin.impl = None

    pin.pmz_dct['A'] = ( pmz_A_lst, 0 )
    pin.pmz_dct['B'] = ( pmz_B_lst, 1 )
    pin.pmz_dct['C'] = ( pmz_C_lst, 1 )

    pin.pmz_dct['FA'] = ( pmz_A_lst, 0 )
    pin.pmz_dct['FB'] = ( pmz_B_lst, 1 )
    pin.pmz_dct['FC'] = ( pmz_C_lst, 1 )

    pin.pmz_dct['FA2'] = ( pmz_A_lst, 0 )
    pin.pmz_dct['FB2'] = ( pmz_B_lst, 1 )
    pin.pmz_dct['FC2'] = ( pmz_C_lst, 1 )

    pin.pmz_dct['C1'] = ( pmz_C1_lst, 0 )
    pin.pmz_dct['C2'] = ( pmz_C2_lst, 0 )
    pin.pmz_dct['C3'] = ( pmz_C3_lst, 0 )
    pin.pmz_dct['C4'] = ( pmz_C4_lst, 0 )


    v0_lst = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 5 )]
    v1_A_lst = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 9 )]
    v1_B_lst = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 18 )]
    v1_C_lst = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 9 )]

    v1_lst_F = [ ( sage_QQ( i ) / ( 3 * 180 ) ) * sage_pi for i in range( 0, 3 * 360, 1 )]
    v1_lst_F2 = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 2 )]

    v0_lst_CC = [ sage_QQ( i ) / 10 for i in range( -100, 100, 1 )]

    prec = 50

    pin.curve_dct['A'] = {'step0':v0_lst, 'step1':v1_A_lst, 'prec':prec, 'width':0.01}
    pin.curve_dct['B'] = {'step0':v0_lst, 'step1':v1_B_lst, 'prec':prec, 'width':0.01}
    pin.curve_dct['C'] = {'step0':v0_lst, 'step1':v1_C_lst, 'prec':prec, 'width':0.01}

    pin.curve_dct['FA'] = {'step0':v0_lst, 'step1':v1_lst_F, 'prec':prec, 'width':0.001}
    pin.curve_dct['FB'] = {'step0':v0_lst, 'step1':v1_lst_F, 'prec':prec, 'width':0.001}
    pin.curve_dct['FC'] = {'step0':v0_lst, 'step1':v1_lst_F, 'prec':prec, 'width':0.001}

    pin.curve_dct['FA2'] = {'step0':v0_lst, 'step1':v1_lst_F2, 'prec':prec, 'width':0.001}
    pin.curve_dct['FB2'] = {'step0':v0_lst, 'step1':v1_lst_F2, 'prec':prec, 'width':0.001}
    pin.curve_dct['FC2'] = {'step0':v0_lst, 'step1':v1_lst_F2, 'prec':prec, 'width':0.001}

    pin.curve_dct['C1'] = {'step0':v0_lst_CC, 'step1':[0], 'prec':prec, 'width':0.01}
    pin.curve_dct['C2'] = {'step0':v0_lst_CC, 'step1':[0], 'prec':prec, 'width':0.01}
    pin.curve_dct['C3'] = {'step0':v0_lst_CC, 'step1':[0], 'prec':prec, 'width':0.01}
    pin.curve_dct['C4'] = {'step0':v0_lst_CC, 'step1':[0], 'prec':prec, 'width':0.01}

    col_A = ( 0.6, 0.4, 0.1, 0.0 )
    col_B = ( 0.1, 0.15, 0.0, 0.0 )
    col_C = ( 0.2, 0.3, 0.2, 0.0 )
    colFF = ( 0.1, 0.1, 0.1, 0.0 )
    colCC = ( 0.6, 0.0, 0.0, 0.0 )

    pin.text_dct['A'] = [True, col_A, 'phong 0.2 phong_size 5' ]
    pin.text_dct['B'] = [True, col_B, 'phong 0.2 phong_size 5' ]
    pin.text_dct['C'] = [True, col_C, 'phong 0.2 phong_size 5' ]

    pin.text_dct['FA'] = [True, colFF, 'phong 0.2 phong_size 5' ]
    pin.text_dct['FB'] = [True, colFF, 'phong 0.2 phong_size 5' ]
    pin.text_dct['FC'] = [True, colFF, 'phong 0.2 phong_size 5' ]

    pin.text_dct['FA2'] = [True, colFF, 'phong 0.2 phong_size 5' ]
    pin.text_dct['FB2'] = [True, colFF, 'phong 0.2 phong_size 5' ]
    pin.text_dct['FC2'] = [True, colFF, 'phong 0.2 phong_size 5' ]

    pin.text_dct['C1'] = [True, colCC, 'phong 0.2 phong_size 5' ]
    pin.text_dct['C2'] = [True, colCC, 'phong 0.2 phong_size 5' ]
    pin.text_dct['C3'] = [True, colCC, 'phong 0.2 phong_size 5' ]
    pin.text_dct['C4'] = [True, colCC, 'phong 0.2 phong_size 5' ]


    ############################
    # raytrace image/animation #
    ############################

    # four circles on projection Veronese surface
    pin.cam_dct['location'] = ( 0, -1.5, 0 )
    pin.cam_dct['rotate'] = ( 60, 10, 45 )
    create_pov( pin, ['FA2', 'FB2', 'FC2'] )
    create_pov( pin, ['C1', 'C2', 'C3', 'C4'] + ['FA2', 'FB2', 'FC2'] )

    # hexagonal web on Veronese surface
    pin.cam_dct['location'] = ( 0, -1.2, 0 )
    pin.cam_dct['rotate'] = ( 35, 0, 45 )
    create_pov( pin, ['A', 'B', 'C'] )
    create_pov( pin, ['A', 'B', 'C', 'FA', 'FB', 'FC'] )
    create_pov( pin, ['FA2', 'FB2', 'FC2'] )

