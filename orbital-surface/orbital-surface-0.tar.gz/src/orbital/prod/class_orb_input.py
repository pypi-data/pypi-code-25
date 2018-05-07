'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Aug 7, 2016
@author: Niels Lubbes
'''

from orbital.class_orb_tools import OrbTools

from orbital.class_orb_ring import OrbRing

from orbital.prod.orb_matrices import get_mat

from orbital.sage_interface import sage__eval
from orbital.sage_interface import sage_Permutation
from orbital.sage_interface import sage_Permutations



class OrbInput:
    '''
    OrbInput represents a 1-parameter subgroup in Aut(S^7) and 
    a circle in S^7, where S^7 is the projective 7-sphere.
        
    This object is input to: 
        "orb_product.orb_product(input)"
    and the result is a surface S, that is obtained by applying
    the 1-parameter subgroup to the circle.
        
    Additional attributes indicate which aspects should be computed from the
    orbital product.
    
    Attributes
    ----------
    omat : sage_matrix
        Matrix representing a 1-parameter subgroup in Aut(S^7).
    
    vmat : sage_matrix
        Matrix over "OrbRing.R" representing a circle C in S^7.
        The circle C is obtained by applying "self.vmat" to the circle:
        ZeroSet(<-x0^2+x1^2+x2^2, x3, x4, x5, x6, x7, x8>).    
    
    pmat : sage_matrix
        Matrix representing a projection from P^8 to P^3.

    info_dct : dict<string:tuple>
        A dictionary containing info how the matrices were constructed.
        {
            'pmat' : A 3-tuple whose elements are arguments for 
                     the method "orb_matrices.get_mat()"

            'omat' : A 3-tuple whose elements are arguments for 
                     the method "orb_matrices.get_mat()"

            'vmat' : A 3-tuple whose elements are arguments for 
                     the method "orb_matrices.get_mat()"
        }        
    
    do : dict<string:boolean>
        A dictionary with booleans, which indicate what attributes of the
        surface S should be computed. Here S is the surface which is the  
        union of orbits of points on a circle w.r.t. a 1-parameter subgroup.        
        {
            'pmz' : If True, compute parametrization of S.
            'bpt' : If True, compute base points of parametrization of S.
            'imp' : If True, compute implicit equation of S.            
            'dde' : If True, compute degree, dimension and embedding dimension n of S in S^n.
            'prj' : If True, compute projection of S.
            'fct' : If True, compute components of projection of S (uses Maple).
            'gen' : If True, compute geometric genus of S (uses Maple).
            'sng' : If True, compute singular locus of projection of S (uses Magma).
            'tst' : If True, test parametrization/implicitization.   
        }
    '''


    def __init__( self ):
        self.omat = None
        self.vmat = None
        self.pmat = None
        self.info_dct = {}

        self.do = {}
        self.do['pmz'] = True  # compute parametrization of S
        self.do['bpt'] = True  # compute base points of parametrization of S
        self.do['imp'] = True  # compute implicit equation of S
        self.do['dde'] = True  # compute degree, dimension and embedding dimension n of S in S^n.
        self.do['prj'] = True  # compute projection of S
        self.do['fct'] = True  # compute components of projection of S
        self.do['gen'] = True  # compute geometric genus of S
        self.do['sng'] = True  # compute singular locus of projection of S
        self.do['tst'] = True  # test parametrization/implicitization


    def set_short_str( self, short_str ):
        '''
        Parameters
        ----------
        short_str : string 
            A string of a list of length two.
            The first element is a string and the second element a dictionary 
            with specifications as "self.info_dct".
            See also "OrbOutput.get_short_str()".
        
        Returns
        -------
        self
            The attributes "self.info_dct", "self.omat", "self.vmat" and "self.pmat" 
            are set according to parameter "short_str". 
        '''
        dct = sage__eval( short_str )[1]
        self.set( dct['pmat'], dct['omat'], dct['vmat'] )

        return self


    def set( self, p_tup, o_tup, v_tup ):
        '''
        Parameters
        ----------
        p_tup : tuple<string> 
            A 3-tuple of strings with format as in the docs of "orb_matrices.get_mat()".
            
        o_tup : tuple<string> 
            Same specs as "p_tup".
            
        v_tup : tuple<string> 
            Same specs as "p_tup".

        Returns
        -------
        self
            Sets "self.pmat", "self.omat" and "self.vmat"
            according "p_tup", "o_tup" and "v_tup" respectively. 
            The matrices are obtained with "orb_matrices.get_mat()". 
            Set "self.info_dct" with info about the decomposition
            of the matrices:              
                      "self.info_dct['pmat'] = p_tup"
                      "self.info_dct['omat'] = o_tup"
                      "self.info_dct['vmat'] = v_tup"                        
        '''

        self.pmat = get_mat( p_tup[0], p_tup[1], p_tup[2] )
        self.omat = get_mat( o_tup[0], o_tup[1], o_tup[2] )
        self.vmat = get_mat( v_tup[0], v_tup[1], v_tup[2] )

        self.info_dct['pmat'] = p_tup
        self.info_dct['omat'] = o_tup
        self.info_dct['vmat'] = v_tup

        return self


    def random( self, coef_bnd = 3, random_pmat = True ):
        '''
        Sets (restricted) random values for "self.omat", 
        "self.vmat" and "self.pmat". 
                
        Parameters
        ----------
        coef_bnd : int    
            Positive integer.
        
        random_pmat : boolean 
                     
        Returns
        -------
        self
                
        Notes
        -----
        The translation coefficients of "self.vmat" 
        are in the interval: [-coef_bnd, +coef_bnd].              
        If "random_pmat== True", then "self.pmat" 
        is set to a random value (P1), and 
        otherwise "self.pmat" is set to a standard 
        projection (P0).          
        '''

        ch_lst = ['r', 's', 'p', 'm', 'a']

        #
        # random self.pmat
        #
        Pn = {True:'P1', False:'P0'}[random_pmat]
        self.pmat = get_mat( Pn, 'I', 'I' )
        self.info_dct['pmat'] = ( Pn, 'I', 'I' )

        #
        # random self.omat
        #
        rnd = OrbRing.random_elt( [0, 1] )
        if rnd == 0:
            ch_str = ''.join( [OrbRing.random_elt( ch_lst ) for i in range( 4 ) ] )
            B_str = 'O' + ch_str

            rnd2 = OrbRing.random_elt( [0, 1] )
            if rnd2 == 0:
                A_str = 'I'
                C_str = 'I'
            else:
                p = sage_Permutations( range( 1, 8 + 1 ) )
                rp = p.random_element()
                rpI = sage_Permutation( rp ).inverse()
                A_str = 'E' + str( list( rpI ) )
                C_str = 'E' + str( list( rp ) )

        elif rnd == 1:
            A_str = 'I'
            B_str = 'tT'
            C_str = 'I'

        self.omat = get_mat( A_str, B_str, C_str )
        self.info_dct['omat'] = ( A_str, B_str, C_str )

        #
        # random self.vmat
        #

        #     All the coefficients are bound by coef_size-n for some integer n.
        coef_size = OrbRing.random_elt( range( 1, coef_bnd + 1 ) )

        #     A -- self.vmat
        t_lst = [OrbRing.random_int( coef_size ) for i in range( 7 )]
        A_str = 'T' + str( t_lst )

        #     B -- self.vmat"
        #          note that small angles means small coefficients
        angle_lst = [ OrbRing.random_elt( range( 0, 360 ) ) for i in range( 4 ) ]
        ch_str = ''.join( [OrbRing.random_elt( ch_lst ) for i in range( 4 ) ] )
        B_str = 'R' + ch_str + str( angle_lst )

        #     C -- self.vmat
        rnd = OrbRing.random_elt( [0, 1, 2] )
        if rnd == 0:
            C_str = 'T' + str( [-t_lst[i] for i in range( 7 )] )  # inverse
        elif rnd == 1:
            C_str = 'T' + str( [OrbRing.random_int( coef_size ) for i in range( 7 )] )
        elif rnd == 2:
            C_str = 'I'

        #     A*B*C -- self.vmat
        self.vmat = get_mat( A_str, B_str, C_str )
        self.info_dct['vmat'] = ( A_str, B_str, C_str )

        return self


    # human readable string representation of object
    def __str__( self ):

        s = ''
        s += 15 * '.' + '\n'
        for key in self.info_dct.keys():
            s += key + '          = ' + str( self.info_dct[key][0] )
            s += ' ~~~ ' + str( self.info_dct[key][1] )
            s += ' ~~~ ' + str( self.info_dct[key][2] )
            s += '\n'

        s += 'do            = ' + str( self.do ) + '\n'
        s += 15 * '.'

        return s






