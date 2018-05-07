'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Nov 23, 2017
@author: Niels Lubbes

'''
import time
import sys
import os
import subprocess
from subprocess import call

from orbital.povray.class_pov_input import PovInput

from orbital.povray.povray_aux import get_curve_lst
from orbital.povray.povray_aux import convert_pngs_gif
from orbital.povray.povray_aux import strftime
from orbital.povray.povray_aux import create_dir
from orbital.povray.povray_aux import pov_coef_lst

from orbital.class_orb_tools import OrbTools


def create_pov( pin, fam_lst = [], show_surf = False, ani = False, ft_lst = [] ):
    '''
    Creates a povray image(s) of surface represented by "pin"
    together with families of curves on this surface. The
    output directory is specified by "pin.path".
      
    If "show_surf" is True then include implicit surface
    as povray's poly object (might lead to trouble if 
    coefficients are too large).
      
    If "ani" then the curves are animated as moving in a 
    family. In each frame, all curves in family <fam> are 
    rendered with transparancy <t>, for all (<fam>,<t>) 
    in "ft_lst", such that <fam> is not the family that is 
    animated.      
    
    Parameters
    ----------
    pin : PovInput
        
    fam_lst : list<string> 
        A list of strings denoting family id's.
        
    show_surf : bool     
        
    ani : bool 
        If true then output animated gif.        

    ft_lst : list<(string,float)>
        A list of pairs [(<fam>,<t>),...]
        where <fam> is a string denoting a family id
        and <t> is a float in [0,1] representing transparency.
        This argument is ignored if "ani==False".
                         
    Returns
    -------
    list<string>              
        Returns list of povray string for each family.
          
    '''
    pov_str = ''
    pov_str += create_pov_preamble( pin )
    pov_str += create_pov_axes()
    if show_surf: pov_str += create_pov_surface( pin )

    fam_pov_str_lst = []
    for fam in fam_lst:
        fam_pov_str_lst += [create_pov_curves( pin, fam )]
        pov_str += fam_pov_str_lst[-1]

    # fixed or animated image?
    if not ani:

        prv_fname = pin.fname
        pin.fname = prv_fname + '_' + ''.join( fam_lst ) + '_' + strftime( "%H-%M-%S" )
        pov_raytrace( pin, pov_str )
        pin.fname = prv_fname

    elif ani:

        prv_fname = pin.fname
        for fam in fam_lst:
            pin.fname = prv_fname + '_' + fam + '_' + strftime( "%H-%M-%S" )
            pov_ani( pin, fam, show_surf, ft_lst )
        pin.fname = prv_fname

    return fam_pov_str_lst


def create_pov_preamble_includes():
    '''
    Returns
    -------
    string
        A string of includes in the pre-amble of a povray file.
    '''

    s = ''
    s += '#include "colors.inc"\n'
    s += '#include "stones.inc"\n'
    s += '#include "textures.inc"\n'
    s += '#include "shapes.inc"\n'
    s += '#include "glass.inc"\n'
    s += '#include "metals.inc"\n'
    s += '#include "woods.inc"\n'

    return s


def create_pov_preamble_declares( pin ):
    '''
    Parameters
    ----------
    pin : PovInput 
        PovInput object where the following 
        attributes are set:                                
            "pin.cam_dct"            
            "pin.axes_dct"
            "pin.curve_dct"
            "pin.text_dct"
    
    Returns
    -------
        A string of declare statements in 
        the pre-amble of a povray file.
    '''

    s = ''
    s += '#declare CAM_LOC_X    = ' + str( pin.cam_dct['location'][0] ) + ';\n'
    s += '#declare CAM_LOC_Y    = ' + str( pin.cam_dct['location'][1] ) + ';\n'
    s += '#declare CAM_LOC_Z    = ' + str( pin.cam_dct['location'][2] ) + ';\n'
    s += '\n'
    s += '#declare CAM_LAT_X    = ' + str( pin.cam_dct['lookat'][0] ) + ';\n'
    s += '#declare CAM_LAT_Y    = ' + str( pin.cam_dct['lookat'][1] ) + ';\n'
    s += '#declare CAM_LAT_Z    = ' + str( pin.cam_dct['lookat'][2] ) + ';\n'
    s += '\n'
    s += '#declare CAM_ROT_X    = ' + str( pin.cam_dct['rotate'][0] ) + ';\n'
    s += '#declare CAM_ROT_Y    = ' + str( pin.cam_dct['rotate'][1] ) + ';\n'
    s += '#declare CAM_ROT_Z    = ' + str( pin.cam_dct['rotate'][2] ) + ';\n'
    s += '\n'
    s += '#declare SHOW_AXES    = ' + str( pin.axes_dct['show'] ).lower() + ';\n'
    s += '#declare AXES_LEN     = ' + str( pin.axes_dct['len'] ) + ';\n'
    s += '\n'

    for key in sorted( pin.text_dct.keys() ):
        s += '#declare SHOW_' + key + ' = ' + str( pin.text_dct[key][0] ).lower() + ';\n'
    s += '\n'

    for key in sorted( pin.curve_dct.keys() ):
        s += '#declare WIDTH_' + key + ' = ' + str( pin.curve_dct[key]['width'] ) + ';\n'
    s += '\n'

    for key in sorted( pin.text_dct.keys() ):

        col = str( pin.text_dct[key][1] )[1:-1]
        fin = pin.text_dct[key][2]

        s += '#declare TEXT_' + key + ' = texture\n'
        s += '{\n'
        s += '    pigment { color rgbt  <' + col + '> }\n'
        s += '    finish  { ' + fin + ' }\n'
        s += '}\n'

    s = '\n// start declares\n' + s + '//end declares\n\n'

    return s


def create_pov_preamble_camera( pin ):
    '''
    Parameters
    ----------
    pin : PovInput 
        PovInput object where the following 
        attributes are set:                                
            "pin.shadow"    
            "pin.light_lst"
    
    Returns
    -------
    string
        A string of global settings, camera and light source in povray format.
    '''

    s = ''

    s += '\n'
    s += 'global_settings\n'
    s += '{\n'
    s += '    assumed_gamma   1.0\n'
    s += '    max_trace_level 256\n'
    s += '}\n'

    s += '\n'
    s += 'camera\n'
    s += '{\n'
    s += '    location <  CAM_LOC_X, CAM_LOC_Y, CAM_LOC_Z >\n'
    s += '    look_at  <  CAM_LAT_X, CAM_LAT_Y, CAM_LAT_Z >\n'
    s += '    rotate   <  CAM_ROT_X, CAM_ROT_Y, CAM_ROT_Z >\n'
    s += '}\n'
    s += '\n'

    s += 'background { color rgb<1,1,1> }\n'
    s += '\n'

    sdow = ''
    if not pin.shadow:
        sdow = 'shadowless'

    for light in pin.light_lst:
        coord = str( light ).replace( '(', '<' ).replace( ')', '>' )
        s += 'light_source { ' + coord + ' color red 1 green 1 blue 1 ' + sdow + ' }\n'

    s += '\n'

    return s


def create_pov_preamble( pin ):
    '''
    Parameters
    ----------
    pin : Povinput 
        PovInput object is passed to "create_pov_preamble_declares()".
        
    Returns
    -------
    string
        A string of the pre-amble of a povray file.
    '''

    s = ''
    s += create_pov_preamble_includes()
    s += create_pov_preamble_declares( pin )
    s += create_pov_preamble_camera( pin )

    return s


def create_pov_axes():
    '''
    Returns
    -------
    string
        A string of axes in povray format.
    '''

    s = ''
    s += '#if (SHOW_AXES)'
    s += '''
    #macro Axis( len, tex )
    union
    {
        cylinder
        {
            <0,-len,0>,
            <0,len,0>,
            0.02
            texture { tex }
        }
     
        cone
        {
            <0,len,0>,
            0.1,
            <0,len+0.3,0>,
            0
            texture{ tex }
        }
    } 
    #end
    
    #declare AxisTex1 = texture
    {
        pigment { color rgb<1,0,0>   }
        finish  { phong 1            }
    }
    
    #declare AxisTex2 = texture
    {
        pigment { color rgb<0,1,0>   }
        finish  { phong 1            }
    }
    
    #declare AxisTex3 = texture
    {
        pigment { color rgb<0,0,1>   }
        finish  { phong 1            }
    }

    union
    {
        // x-axis
        object { Axis( AXES_LEN, AxisTex1 ) rotate<0,0,-90> }
    
        // y-yxis
        object { Axis( AXES_LEN, AxisTex2 ) rotate<0,0,0> }
        
        // z-yxis
        object { Axis( AXES_LEN, AxisTex3 ) rotate<90,0,0> }
    }
    '''
    s += '#end\n\n'

    return s


def create_pov_curves( pin, fam, num = -1 ):
    '''
    Parameters
    ----------
    pin : PovInput
        Passed to "povray_aux.get_curve_lst()".
    
    fam : string 
        A string key denoting a family id (eg. 'A'). 
    
    num : int 
         An integer >= -1. 
    
    Returns
    -------
    string
        Returns a povray input string for the curves in the family "fam" 
        up to curve indexed "num" (modulo the total number of curves).          
        If "num" is -1 then all curves in the family are 
        declared in the povray input string.
    '''

    curve_lst = get_curve_lst( pin, fam )

    if num == -1:
        num = len( pin.curve_lst_dct[fam] )

    s = '#if (SHOW_' + fam + ')\n'
    for idx in range( 0, num ):

        # the modulo % is useful for animations to have
        # a break between loops by overdrawing curves
        # after a loop
        #
        curve = curve_lst[idx % len( pin.curve_lst_dct[fam] )]

        # Needed for cubic spline algorithm.
        # Due to a povray bug "curve += curve[0:3]"
        # gives artifacts
        #
        curve += curve[0:]

        # Sweep the curves out by spheres
        #
        s += '\n\n'
        s += 'sphere_sweep\n'
        s += '{\n'
        s += '    cubic_spline\n'
        s += '    ' + str( len( curve ) ) + ',\n'
        for point in curve:
            p_str = ','.join( [ str( coord ) for coord in point ] )
            s += '    <' + p_str + '>, WIDTH_' + fam + '\n'
        s += '    texture { TEXT_' + fam + '}\n'
        s += '}\n'
    s += '#end\n'
    s += '\n\n'

    return s



def create_pov_surface( pin ):
    '''
    Parameters
    ----------
    pin : PovInput 
        PovInput with attributes
            "pin.impl" 
            "pin.text_dct['SURF']" 
    
    Returns
    -------
        A povray string for a POLY object using input equation
        and texture.         
    '''

    d, coef_lst = pov_coef_lst( pin.impl )

    s = ''
    s += '#if (SHOW_SURF)\n'
    s += 'poly\n'
    s += '{\n'
    s += '    ' + str( d ) + ',\n'
    s += '    ' + str( coef_lst ).replace( '[', '<' ).replace( ']', '>' ) + '\n'
    s += '    sturm\n'
    s += '    texture { TEXT_SURF }\n'
    s += '}\n'
    s += '#end\n'
    s += '\n\n'

    return s


def pov_raytrace( pin, pov_str ):
    '''
    Parameters
    ----------
    pin : PovInput     
        The following attributes of the PovInput object are used:
        * pin.path
        * pin.fname
        * pin.width
        * pin.height
        * pin.quality
    
    pov_str : string
        A string of a povray input file.
    
    Returns
    -------
        A povray image at "pin.path + pin.fname + '.pov'". 
    '''

    # set file name
    #
    file_name = pin.path + pin.fname + '.pov'
    output_name = pin.path + pin.fname + '.png'

    # write povray string
    #
    OrbTools.p( 'Writing povray string to:', file_name )
    create_dir( file_name )
    with open( file_name, "w" ) as text_file:
        text_file.write( pov_str )

    # execute povray tracer
    #
    my_env = dict( os.environ )
    my_env['LD_LIBRARY_PATH'] = ''  # prevent problems with C++ libraries

    cmd = ['povray']
    cmd += ['+O' + output_name]
    cmd += ['+W' + str( pin.width )]
    cmd += ['+H' + str( pin.height )]
    cmd += ['+Q' + str( pin.quality )]
    if pin.quality > 5:
        cmd += ['+A']  # antialiasing
    cmd += ['-D']  # no popup window
    cmd += [file_name]

    OrbTools.p( cmd )
    p = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, env = my_env )
    out, err = p.communicate()

    OrbTools.p( 'out =', out )
    OrbTools.p( 'err =', err )


def pov_ani( pin, fam, show_surf = False, ft_lst = [] ):
    '''
    Parameters
    ----------
    pin : PovInput       
        The following attributes of the PovInput object are used:    
        * "pin.path"
        * "pin.fname"
        * "pin.ani_delay"
                                                
    fam : string 
        A string key for the family which should be animated. 
                 
    show_surf : bool
        If True then the surface on which the family lives is rendered.
                         
    ft_lst : list<(string,float)>   
        A list of pairs: [(<fam>,<t>)]
        where <fam> is a string denoting a family id
        and <t> is a float in [0,1] representing transparancy.
    
    Returns
    -------        
        An animated gif at "pin.path". 
        In each frame, all curves in family <fam> are 
        rendered with transparancy <t>, for all (<fam>,<t>) in "ft_lst", 
        such that <fam> is *not* the family that is animated.  
    '''
    # total number of curves that are raytraced in the
    # animation.
    num_curves = 0

    # Raytrace the families and store into indexed ".png"
    # files.
    #
    path = pin.path
    fname = pin.fname
    nc = len( get_curve_lst( pin, fam ) )
    nc += 5  # delays loops between animations
    for idx in range( 0, nc ):

        OrbTools.p( 'idx =', idx, '/', nc )

        # set texture transparency in preamble
        col_dct = {}
        for f, t in ft_lst:
            if f != fam:
                col_dct[f] = pin.text_dct[f][1]
                pin.text_dct[f][1] = tuple( list( col_dct[f][:-1] ) + [t] )
        pov_str = create_pov_preamble( pin )
        for f, t in ft_lst:
            if f != fam:
                pin.text_dct[f][1] = col_dct[f]  # reset to previous value

        # setup implicit surface
        if show_surf:
            pov_str += create_pov_surface( pin )

        # setup curves in animated family
        pov_str += create_pov_curves( pin, fam, idx )

        # setup families in ft_lst
        for f, t in ft_lst:
            if f != fam:
                pov_str += create_pov_curves( pin, f )

        # start raytracing
        pin.fname = fname + '-' + str( idx )
        pin.path = path + 'ani/'
        pov_raytrace( pin, pov_str )

    pin.path = path
    pin.fname = fname

    # create animated gif
    convert_pngs_gif( pin.path, pin.fname, nc, pin.ani_delay )









