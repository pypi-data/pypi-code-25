'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.

Created on Aug 7, 2016
@author: Niels Lubbes
'''

from sage_interface import sage_QQ
from sage_interface import sage_ZZ
from sage_interface import sage_PolynomialRing
from sage_interface import sage__eval
from sage_interface import sage_var


class OrbRing:

    num_field = sage_QQ

    vstr = ''
    vstr += 'x0,x1,x2,x3,x4,x5,x6,x7,x8,'
    vstr += 'v0,v1,v2,v3,v4,v5,v6,v7,v8,'
    vstr += 'c0,s0,c1,s1,'
    vstr += 't0,t1,t2,t3,t4,t5,t6,t7'

    R = sage_PolynomialRing( num_field, sage_var( vstr ), order = 'degrevlex' )


    @staticmethod
    def coerce( expr ):
        return sage__eval( str( expr ), OrbRing.R.gens_dict() )


    @staticmethod
    def random_int( val ):
        '''
        INPUT:
            - "val" -- An integer.
        OUTPUT:
            - A random element in the interval [-val,val]
        '''
        return int( sage_ZZ.random_element( -val, val + 1 ) )

    @staticmethod
    def random_elt( lst ):
        '''
        INPUT:
            - "lst" -- A list.
        OUTPUT:
            - A random element in "lst".
        '''
        idx = int( sage_ZZ.random_element( 0, len( lst ) ) )
        return lst[idx]


    @staticmethod
    def approx_QQ_coef( cf, ci_idx = 0 ):
        '''
        Parameters
        ----------
        cf : sage_NUMBERFIELD 
            Element of a number field. For example a coefficient of a 
            polynomial in linear_series.PolyRing.
            
        ci_idx : int
            An integer specifying the complex embedding of the 
            numberfield into the complex numbers. 
            
        Returns
        -------
        sage_QQ    
            A rational approximation of this coefficient.
        
        '''
        if cf in sage_QQ:
            return cf

        if type( cf ) == int:
            return sage_QQ( cf )

        ncf = cf.complex_embeddings()[ci_idx].real_part().exact_rational()

        return ncf


    @staticmethod
    def approx_QQ_pol_lst( pol_lst, ci_idx = 0 ):
        '''
        Parameters
        ----------
        pol_lst : list<sage_POLY> 
            A list of polynomials with coefficients defined over a 
            number field with a norm (thus the elements have an 
            absolute value).
            
        ci_idx : int
            An integer specifying the complex embedding of the 
            numberfield into the complex numbers.             
            
        Returns
        -------
        list<sage_POLY>    
            An approximation of the polynomial with coefficients defined
            over sage_QQ. 
        
        '''
        out_lst = []
        for pol in pol_lst:
            if pol in sage_QQ:
                out_lst += [ pol ]
            elif type( pol ) == int:
                out_lst += [ sage_QQ( pol ) ]
            elif 'NumberFieldElement' in str( type( pol ) ):
                out_lst += [ OrbRing.approx_QQ_coef( pol, ci_idx ) ]
            else:
                out_lst += [pol.map_coefficients( lambda cf: OrbRing.approx_QQ_coef( cf, ci_idx ) )]
        return out_lst
