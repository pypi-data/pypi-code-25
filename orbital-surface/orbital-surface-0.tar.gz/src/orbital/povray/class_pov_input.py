'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Nov 23, 2017
@author: Niels Lubbes

'''

class PovInput:
    '''
    This object represent input for generating a povray image.
    
    Attributes
    ----------
    impl : sage_POLY
        Polynomial for implicit equation of a surface in QQ[x,y,z].
    
    pmz_dct : dict
        A dictionary of parametrizations.
        For the keys we use characters in [A-Z].
        The values are 2-tuples:        
            (<pmz>,<fam12>)        
        where        
          * <pmz> is a list of 4 polynomials in
            QQ[c0,s0,c1,s1]/<c0^2+s0^2-1,c1^2+s1^2-1>
            which define a parametrization of surface
            in projective 3-space:
                S^1xS^1 ---> P^3.        
          * <fam12> is an integer either 0 or 1.
            If 0 then the 1st S^1 parametrizes a curve in
            a family. If 1 then the 2nd S^1.

    path : string
        Path for output file. Path should end with '/'-character
    
    fname : string
        Name for output file without extension.
    
    scale : int
        Scaling factor.
        
    axes_dct : dict
        Dictionary with attributes for axis.
        {
            'show' : boolean denotes whether to show camera,
            'len'  : int denoting length of axis,
        }
         
    cam_dct : dict
        Dictionary with attributes for camera. 
        {
            'location': (int,int,int),
            'lookat'  : (int,int,int), 
            'rotate'  : (int,int,int). 
        }        
        Each value is a triple of integers denoting the location and 
        direction of camera. Finally, the camera is rotated along 
        x- ,y- and z- axes with specified angles. 

    light_lst : list<(double,double,double)>
        A list of 3-tuples (x,y,z) corresponding to coordinates
        for lights

    shadow : bool
        If False, then the Povray light type is shadowless. 
                           
    width : int 
        Width of image.
    
    height : int
        Height of image.
 
    quality : int
        Quality of image is defined by an integer between 0-11.
            0, 1      Just show quick colors. Use full ambient lighting only.
                      Quick colors are used only at 5 or below.
            2, 3      Show specified diffuse and ambient light.
            4         Render shadows, but no extended lights.
            5         Render shadows, including extended lights.
            6, 7      Compute texture patterns, compute photons
            8         Compute reflected, refracted, and transmitted rays.
            9, 10, 11 Compute media and radiosity.        
        See also:
            http://www.povray.org/documentation/view/3.6.1/223/            
    
    ani_delay : int 
        Delay in ms between frames of animation.
                
    curve_dct: dict
        {
            'step0': list<sage_REALNUMBER>, 
            'step1': list<sage_REALNUMBER>, 
            'prec' : int, 
            'width': double
        }
        The OrbOutput object "self.o" represents to families of curves A and B.        
        Family A is represented as a list:        
           self.curve_lst_dct['A']=[ <curveA(0)>, <curveA(1)>, ... ]        
        where
          
          * <curveA(#)> is a list of points on a curve in family A.        
          
          * The list 'step0' is a list of parameter values for the 
            points in the curve <curveA(#)> so that each point in 
            this curve is obtained by evaluating the map map pmz_dct['A'] 
            at a parameter value. Thus the space between points in 
            <curveA<n>> is determined by "step0".
          
          * The list 'step1' is a list of parameter values for 
            curves in family. The space between <curve(n)> and <curve(n+1)>
            is determined by the space between parameters in "step1".        
          
          * The precision of points in <curveA(#)> is determined by "prec".        
          
          * The curves in family A are sweeped out by spheres
            with radius "width".        
        See also "povray_aux.get_curve_lst()"
        for how the following attributes are used.
            
    curve_lst_dct : dict
        Place holder for the curve lists if computed by 
        method "povray_aux.get_curve_lst()".
        
    text_dct : dict
        Dictionary for texture.
        {
            'SURF': [<show>, <rgbt>, <finish>],
            'A'   : [<show>, <rgbt>, <finish>],
            ...
        }
        The textures where 'SURF' is the identifier for surface and 
        A-Z are id's for families of curves.
            <show>   : A boolean. In .pov file: #if <show>...#end
            <rgbt>   : red, green, blue, transparency
            <finish> : see povray documentation for texture{ finish{...} }                
    '''


    def __init__( self ):
        '''
        Constructor.
        '''

        self.impl = None
        self.pmz_dct = {}
        self.path = '/home/niels/Desktop/n/src/output/orb/povray/'
        self.fname = 'orb'
        self.scale = 1

        self.axes_dct = {}
        self.axes_dct['show'] = True
        self.axes_dct['len'] = 3

        self.cam_dct = {}
        self.cam_dct['location'] = ( 0, 0, -3 )
        self.cam_dct['lookat'] = ( 0, 0, 0 )
        self.cam_dct['rotate'] = ( 0, 0, 0 )

        self.light_lst = [( 0, 0, -5 ), ( 0, -5, 0 ), ( -5, 0, 0 ),
                          ( 0, 0, 5 ), ( 0, 5, 0 ), ( 5, 0, 0 ) ]
        self.shadow = True

        self.width = 100
        self.height = 75
        self.quality = 3  # quality is between 0-11

        self.ani_delay = 10

        self.curve_dct = {}
        self.curve_dct['A'] = {'step0':2 * 36, 'step1':36, 'prec':5, 'width':0.02}

        self.text_dct = {}
        self.text_dct['SURF'] = [True, ( 0.2, 0.7, 0.3, 0.0 ), 'F_Glass10']
        self.text_dct['A'] = [True, ( 0.5, 0.0, 0.0, 0.0 ), 'phong 0.2 phong_size 5' ]

        # Examples for colors
        # -------------------
        # red   = ( 0.5, 0.0, 0.0, 0.0 )
        # green = ( 0.2, 0.3, 0.2, 0.0 )
        # beige = ( 0.8, 0.6, 0.2, 0.0 )

        self.curve_lst_dct = {}  # used by "povray_aux.get_curve_lst()"


    # human readable string representation of object
    def __str__( self ):
        return 'PovInput<' + self.path + self.fname + '>'



