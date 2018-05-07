'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Aug 7, 2016
@author: Niels Lubbes
'''

from orbital.sage_interface import sage_factor

from orbital.class_orb_ring import OrbRing


class OrbOutput:
    '''
    This "OrbOutput" object represents a surface (or curve) S, which is 
    obtained by applying a 1-parameter subgroup to a circle in S^7.
    
    The 1-parameter subgroup is represented by "input.omat".
    
    The circle C is represented by "input.vmat" applied to the circle 
    Zeroset<(-x0^2-x1^2-x2^2,x3,x4,x5,x6,x7,x8)>.
    
    Attributes
    ----------
    input : OrbInput
        Is set when instantiating this object.
    
    pmz_lst : list<OrbRing.R>
        A list of 9 polynomials in
            QQ[c0,s0,c1,s1]/<c0^2+s0^2-1,c1^2+s1^2-1>
        which define a parametrization of surface S
        in the 7-sphere S^7:
            S^1xS^1--->S^7.        
        Note that (c0,s0) and (c1,s1) are each 
        coordinates for a circle S^1.    
        
    prj_pmz_lst : list<OrbRing.R>
        A list representing a parametrization of a
        projection of S into projective 3-space P^3:
            S^1xS^1--->P^3.        
        The projection is defined by "self.input.pmat".
        
    bp_tree : linear_series.BasePointTree
        Represents (infinitely near) base points
        of a parametrizing map:        
            P^1xP^1---->S^n,    
        where 2<=n<=7. This map is obtain by composing
        the parametrization corresponding to "self.pmz_lst"
        with a birational map P^1xP^1---->S^1xS^1.  
        
    imp_lst : list<OrbRing.R>      
        A list of polynomials in QQ[x0,...,x8] representing 
        the ideal of S. 

    emb : int
        Integer representing the embedding dimension n of S in S^n
        so that S is not contained in a hyperplane section of S^n.
    
    dim : int
        Integer representing the dimension of S.
            
    deg: int
        Integer representing the degree of S.
       
    prj_pol : OrbRing.R
        A polynomial in QQ[x0,x1,x2,x3] representing the
        implicit equation of a projection of S into projective 3-space. 
        The projection is defined by "input.pmat".
        
    xyz_pol : sage_SR
        A polynomial in QQ[x,y,z], which is "prj_pol" 
        dehomogenized w.r.t. x0
        
    fct_lst : list
        A list of strings of polynomial factors of "self.prj_pol":
            [ (<factor>, <multiplicity>),... ]
            
    gen : int
        The arithmetic genus of a hyperplane section of S.
        Note that this is the geometric genus of a 2-plane section of
        "self.prj_pol". If an error occurs during its computation then
        "self.gen" is set to -2.    
        
    sng_lst : list 
        A list [(<I>, <H>),...]
        where <I> is the ideal of a component
        in singular locus of "self.prj", and
        <H> is the Hilbert polynomial of this ideal.   
        
    pmz_test : boolean        
        True if parametric and implicit surface agree
        and False if they are different. Set to None 
        if test was not performed.             
    '''

    # If True then __repr__ returns a minimal output
    #
    short_str = False

    def __init__( self, input ):
        '''
        Parameters
        ----------
        input : OrbInput        
        '''

        self.input = input  # OrbitInput object
        self.pmz_lst = None
        self.prj_pmz_lst = None
        self.bp_tree = None
        self.imp_lst = None
        self.emb = None
        self.dim = None
        self.deg = None
        self.prj_pol = None
        self.xyz_pol = None  # in QQ[x,y,z] (dehomogenized w.r.t. x0)
        self.fct_lst = None
        self.gen = -1
        self.sng_lst = None
        self.pmz_test = None


    def get_short_str( self ):
        '''
        Returns
        -------
        string
            A string of a list of two elements. 
            The first element is a string representing
            human readable values of "self.dim" and "self.deg".
            The second element corresponds to the dictionary 
            "self.input.info_dct".

        Note
        ----
        See also "OrbInput.set_short_str()".
        '''
        # short string
        s = ''
        s += '"['
        s += '\'@(' + str( self.deg ) + ',' + str( self.emb ) + ')=(deg,emb)\''
        s += ', '
        s += str( self.input.info_dct )
        s += ']"'

        return s


    # human readable string representation of object
    def __str__( self ):

        if OrbOutput.short_str:
            return self.get_short_str()

        s = '\n'
        s += 30 * '-' + '\n'

        s += str( self.input ) + '\n'

        s += 'pmz_lst       = ' + str( self.pmz_lst ) + '\n'
        s += 'prj_pmz_lst   = ' + str( self.prj_pmz_lst ) + '\n'
        s += 'imp_lst       = ' + str( self.imp_lst ) + '\n'
        s += 'emb           = ' + str( self.emb ) + '\n'
        s += 'dim           = ' + str( self.dim ) + '\n'
        s += 'deg           = ' + str( self.deg ) + '\n'
        s += 'gen           = ' + str( self.gen ) + '\n'
        s += 'prj_pol       = ' + str( self.prj_pol ) + '\n'
        if self.prj_pol != None:
            s += 'prj_pol{x0:0} = ' + str( sage_factor( self.prj_pol.subs( {OrbRing.coerce( 'x0' ):0} ) ) ) + '\n'
        s += 'xyz_pol       = ' + str( self.xyz_pol ) + '\n'
        s += 'pmz_test      = ' + str( self.pmz_test ) + '\n'

        if self.fct_lst != None:
            s += 'fct_lst       = ' + str( len( self.fct_lst ) ) + ' factors\n'
            if len( self.fct_lst ) > 1:
                for fct in self.fct_lst:
                    s += '              ~ ' + str( fct ) + '\n'

        if self.sng_lst != None:
            s += 'sng_lst       = ' + str( len( self.sng_lst ) ) + ' components\n'
            for sng in self.sng_lst:
                s += '              ~ ' + str( sng ) + '\n'

        if self.bp_tree != None:
            s += 'bp_tree       = ' + str( self.bp_tree ) + '\n'

        s += 'short_str     = '
        s += self.get_short_str() + '\n'

        s += 30 * '-' + '\n'
        return s











