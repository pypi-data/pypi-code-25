'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Aug 10, 2016
@author: Niels Lubbes
'''

import os

from orbital.sage_interface import sage_QQ
from orbital.sage_interface import sage_pi
from orbital.sage_interface import sage_sin
from orbital.sage_interface import sage_cos
from orbital.sage_interface import sage_arctan

from orbital.class_orb_tools import OrbTools


def get_cs( angle ):
    '''
    Parameters
    ----------
    angle: int 
        An integer in [0,360).
    
    Returns
    -------
    (sage_QQ,sage_QQ)
        A pair of rational numbers (a,b) such that 
            a^2+b^2=1
        and ( a, b ) is a rational approximation of 
            ( cos(angle/180*pi), sin(angle/180*pi) ).
    '''
    angle = angle % 360

    radi = ( sage_QQ( angle ) / 180 ) * sage_pi

    if sage_sin( radi ) in sage_QQ and sage_cos( radi ) in sage_QQ:
        return ( sage_QQ( sage_cos( radi ) ), sage_QQ( sage_sin( radi ) ) )

    p0, p1, p2 = get_pt_dct()[angle % 90]

    c = sage_QQ( p0 ) / p2
    s = sage_QQ( p1 ) / p2

    #  90 = pi/2
    #  sin( a + 90 ) =  cos(a)
    #  cos( a + 90 ) = -sin(a)
    dct = {0:( c, s ), 1:( -s, c ), 2:( -c, -s ), 3:( c, s )}

    rc, rs = dct[int( angle ) / int( 90 )]

    return rc, rs


def get_pt_dct( fname = 'cos_sin' ):
    '''
    Reads in a list of Pythagorian triples, which was obtained from:
    <http://www.tsm-resources.com/alists/PythagTriples.txt>
    
    Parameters
    ----------
    fname: string
        Name of file without extention
        The file should contain 3 integers on each line separated by spaces. 
        We expect them to be Pythagorian triples.
        
    Returns
    -------
    dict
        A dictionary 
            { 
                angle : [a,b,c],
                ... 
            }
        where a^2+b^2=c^2 and <angle> corresponds to 
            round(arctan( <b>/<a> )*180/pi)
        The key <angle> runs from 1 to 89 degrees.           
    '''

    key = 'cossin'
    if key in OrbTools.get_tool_dct():
        return OrbTools.get_tool_dct()[key]

    path = os.path.dirname( os.path.abspath( __file__ ) ) + '/'
    file_name = path + fname
    OrbTools.p( 'Calculating Pythagorian triples and angles from:', file_name )

    angle_lst = []
    pt_dct = {}
    with open( file_name + '.txt', 'r' ) as f:
        for line in f:
            ps_lst = line.replace( '\r\n', '' ).split()
            pt0 = [ sage_QQ( ps ) for ps in ps_lst ]  # need to be divisable!

            # Try all combinations
            # while a triple is still small.
            # We assume that the Pythagorian triples are
            # ordered on coefficient size in the input file.
            #
            pt1a = [ pt0[0], pt0[1], pt0[2]]
            pt1b = [ -pt0[0], pt0[1], pt0[2]]
            pt1c = [ pt0[0], -pt0[1], pt0[2]]
            pt1d = [ -pt0[0], -pt0[1], pt0[2]]

            pt2a = [ pt0[1], pt0[0], pt0[2]]
            pt2b = [ -pt0[1], pt0[0], pt0[2]]
            pt2c = [ pt0[1], -pt0[0], pt0[2]]
            pt2d = [ -pt0[1], -pt0[0], pt0[2]]

            for pt in [pt1a, pt1b, pt1c, pt1d, pt2a, pt2b, pt2c, pt2d]:

                if pt[0] ** 2 + pt[1] ** 2 != pt[2] ** 2:
                    raise ValueError( 'Expect a file containing Pythagorian triples:', pt )

                # cos = pt[0]/pt[2], sin = pt[1]/pt[2], tan=sin/cos
                angle = round( sage_arctan( pt[1] / pt[0] ) * 180 / sage_pi )

                if angle not in angle_lst and angle > 0:
                    angle_lst += [angle]
                    pt_dct.update( {angle:pt} )

    OrbTools.p( len( pt_dct.keys() ) )

    OrbTools.get_tool_dct()[key] = pt_dct
    OrbTools.save_tool_dct()

    return pt_dct
