'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jan 16, 2018
@author: Niels Lubbes
'''

from orbital.sage_interface import sage_QQ
from orbital.sage_interface import sage_pi

from orbital.prod.class_orb_input import OrbInput
from orbital.prod.orb_product import orb_product

from orbital.povray.class_pov_input import PovInput
from orbital.povray.povray import create_pov
from orbital.povray.povray_aux import get_time_str


def dp6_sing():
    '''
    Creates povray image of the projection of a sextic weak del Pezzo surface 
    wdP6 in S^5. This surface contains 2 families of conics. One of these 
    families has a base point at the isolated singularity of wdP6
    '''
    # init OrbInput
    #
    pmat = []
    pmat += [[1, 0, 0, 0] + [ 0, 0, 0, -1, -1]]
    pmat += [[0, 1, 0, 0] + [ 0, 0, 0, 0, 0]]
    pmat += [[0, 0, 1, 0] + [ 0, 0, 0, 0, 0]]
    pmat += [[0, 0, 0, 1] + [ -1, 0, 0, 0, 0]]
    p_tup = ( 'M' + str( pmat ), 'I', 'I' )
    o_tup = ( 'I', 'Oprpr', 'I' )
    v_tup = ( 'T[0, 1, 1, 0, 0, 0, 0]', 'Rrppr[37,0,0,90]', 'T[0, -1, -1, 0, 0, 0, 0]' )

    input = OrbInput().set( p_tup, o_tup, v_tup )
    input.do['pmz'] = True
    input.do['bpt'] = False
    input.do['imp'] = True
    input.do['dde'] = True
    input.do['prj'] = True
    input.do['fct'] = False
    input.do['gen'] = False
    input.do['sng'] = False
    input.do['tst'] = False

    # init OrbOutput.prj_pmz_lst
    #
    o = orb_product( input )
    pmz_AB_lst = o.prj_pmz_lst

    # init PovInput
    #
    pin = PovInput()

    pin.path = './' + get_time_str() + '_dp6_sing/'
    pin.fname = 'orb'
    pin.scale = 1
    pin.cam_dct['location'] = ( 0, 0, -3 )
    pin.cam_dct['lookat'] = ( 0, 0, 0 )
    pin.cam_dct['rotate'] = ( 250, 330, 0 )
    pin.shadow = True
    pin.light_lst = [( 0, 0, -5 ), ( 0, -5, 0 ), ( -5, 0, 0 ),
                     ( 0, 0, 5 ), ( 0, 5, 0 ), ( 5, 0, 0 ) ]
    pin.axes_dct['show'] = False
    pin.axes_dct['len'] = 1.2
    pin.height = 400
    pin.width = 800
    pin.quality = 11
    pin.ani_delay = 10
    pin.impl = None

    v0_lst = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 5 )]
    v1_lst = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 10 )]
    v1_F_lst = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 2 )]

    pin.pmz_dct['A'] = ( pmz_AB_lst, 0 )
    pin.pmz_dct['B'] = ( pmz_AB_lst, 1 )
    pin.pmz_dct['FA'] = ( pmz_AB_lst, 0 )
    pin.pmz_dct['FB'] = ( pmz_AB_lst, 1 )

    pin.curve_dct['A'] = {'step0':v0_lst, 'step1':v1_lst, 'prec':10, 'width':0.05}
    pin.curve_dct['B'] = {'step0':v0_lst, 'step1':v1_lst, 'prec':10, 'width':0.05}
    pin.curve_dct['FA'] = {'step0':v0_lst, 'step1':v1_F_lst, 'prec':10, 'width':0.01}
    pin.curve_dct['FB'] = {'step0':v0_lst, 'step1':v1_F_lst, 'prec':10, 'width':0.01}

    col_A = ( 0.4, 0.0, 0.0, 0.0 )
    col_B = ( 0.2, 0.3, 0.2, 0.0 )
    colFF = ( 0.1, 0.1, 0.1, 0.0 )

    pin.text_dct['A'] = [True, col_A, 'phong 0.2 phong_size 5' ]
    pin.text_dct['B'] = [True, col_B, 'phong 0.2 phong_size 5' ]
    pin.text_dct['FA'] = [True, colFF, 'phong 0.2 phong_size 5' ]
    pin.text_dct['FB'] = [True, colFF, 'phong 0.2 phong_size 5' ]


    if True:

        # raytrace image/animation
        #
        create_pov( pin, ['A', 'B'] )
        create_pov( pin, ['A', 'B', 'FA', 'FB'] )
        return

    else:

        # very low quality for fast debugging
        #
        pin.width = 100
        pin.height = 75
        pin.quality = 4
        v_lst = [ ( sage_QQ( i ) / 180 ) * sage_pi for i in range( 0, 360, 2 * 36 )]

        pin.curve_dct['A'] = {'step0':v_lst, 'step1':v_lst, 'prec':5, 'width':0.02}
        pin.curve_dct['B'] = {'step0':v_lst, 'step1':v_lst, 'prec':5, 'width':0.02}

        create_pov( pin, ['A', 'B'] )
        return


