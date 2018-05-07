'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Apr 4, 2017
@author: Niels Lubbes
'''

from moebius_aut.sage_interface import sage_matrix
from moebius_aut.sage_interface import sage_vector
from moebius_aut.sage_interface import sage_invariant_theory

from moebius_aut.class_ma_tools import MATools
from moebius_aut.class_ma_ring import ring
from moebius_aut.class_ma_ring import MARing


class Veronese( object ):
    '''
    This class represents the Veronese embedding of the
    projective plane P^2 in projective 5-space P^5.
    '''

    @staticmethod
    def get_ideal_lst():
        '''
        Returns
        -------
        list<MARing.R>
            A list of generators for the ideal of the Veronese surface.
            The ideal lives in a subring 
                QQ[x0,...,x8] 
            of the ring represented by "MARing.R".
            The generators for the ideal are all quadratic forms
            and also form a vector space over CC of all quadratic 
            forms that contain the Veronese surface.  
              
        Notes
        -----
        We consider a toric parametrization of the Veronese surface:
        
        (s,t)
        |-->
        (1  : s*t : s  : t  : s^2 : t^2 )
        =
        (x0 : x1  : x2 : x3 : x4  : x5  )
                            
        We can put the exponents of the monomials in a lattice
        where x0 corresponds to coordinate (0,0), x4 to (2,0)
        and x5 to (0,2):  
                
              x5 x7 x8      
              x3 x1 x6
              x0 x2 x4  
        
        The monomial parametrization of the Veronese corresponds to the 
        following lattice polygon:
        
              *
              * *
              * * *                           
        '''

        s_lst = []
        s_lst += ['x1*x1 - x4*x5']
        s_lst += ['x0*x1 - x2*x3']
        s_lst += ['x2*x2 - x0*x4']
        s_lst += ['x3*x3 - x0*x5']
        s_lst += ['x1*x2 - x3*x4']
        s_lst += ['x1*x3 - x2*x5']

        return [ ring( s ) for s in s_lst ]


    @staticmethod
    def get_pmz_lst():
        '''
        Returns
        -------
        list<MARing.R>
            A list of polynomials of degree 2 in the subring QQ[s,t,u] 
            of the ring "MARing.R". These polynomials represent a 
            parametrization of the Veronese surface.
        '''
        s_lst = [ 'u^2', 's*t', 's*u', 't*u', 's^2', 't^2']

        return [ ring( s ) for s in s_lst ]


    @staticmethod
    def change_basis( iqf_lst ):
        '''
        Parameters
        ----------
        iqf_lst : list     
            A list of elements in the subring NF[x0,...,x5] 
            of "MARing.R" where NF denotes the Gaussian 
            rationals QQ(I) with I^2=-1.
                                                                       
        Returns
        -------
        list 
            The input "iqf_lst" where we make the following substitution            
            for each polynomial  
                x0 |--> x0,
                x1 |--> x1, 
                x2 |--> x2 + I*x3, 
                x3 |--> x2 - I*x3,  
                x4 |--> x4 + I*x5,
                x5 |--> x4 - I*x5.               
                                     
        Notes
        -----
        We consider a toric parametrization of the Veronese surface:
        
        (s,t)
        |-->
        (1  : s*t : s  : t  : s^2 : t^2 )
        =
        (x0 : x1  : x2 : x3 : x4  : x5  )
                            
        We can put the exponents of the monomials in a lattice
        where x0 corresponds to coordinate (0,0), x4 to (2,0)
        and x5 to (0,2):  
                
              x5 x7 x8      
              x3 x1 x6
              x0 x2 x4  
        
        The monomial parametrization of the Veronese corresponds to the 
        following lattice polygon:
        
              *
              * *
              * * * 
              
        An antiholomorphic involution acts on the above lattice polygon 
        as a unimodular involution:
              
                ( a, b ) |--> ( b, a)
        
        This unimodular lattice involutions induce an involution on P^5: 

                x0 |--> x0,
                x1 |--> x1, 
                x2 |--> x2 + I*x3, 
                x3 |--> x2 - I*x3,  
                x4 |--> x4 + I*x5,
                x5 |--> x4 - I*x5,                                  
        '''

        I = ring( 'I' )
        x = x0, x1, x2, x3, x4, x5 = MARing.x()[:6]
        z = z0, z1, z2, z3, z4, z5 = MARing.z()[:6]

        dct = { x0:  z0,
                x1:  z1,
                x2:  z2 + I * z3,
                x3:  z2 - I * z3,
                x4:  z4 + I * z5,
                x5:  z4 - I * z5 }

        zx_dct = { z[i]:x[i] for i in range( 6 ) }
        new_lst = [ iqf.subs( dct ).subs( zx_dct ) for iqf in iqf_lst ]

        return new_lst



    @staticmethod
    def get_aut_P5( c_lst ):
        '''
        Parameters
        ----------
        c_lst : list   
            A list of length 9 with elements c0,...,c8 in "MARing.FF". 
            The matrix                             
                [ c0 c1 c2 ]
            M = [ c3 c4 c5 ]
                [ c6 c7 c8 ]
            represents an automorphism of P^2.
                                                             
        Returns
        -------
        sage_matrix
            This method returns a 6x6 matrix defined over "MARing.FF",
            which represents a (parametrized) automorphism of P^5
            that preserves the Veronese surface V. 
                                                  
        Notes
        -----
        The Veronese surface V is isomorphic to P^2.
        The automorphism M of P^2 is via the parametrization 
        ".get_pmz_lst" represented as an automorphism of P^5. 
        Algebraically this is the symmetric tensor Sym^2(M).
        '''
        # obtain parametrization in order to compute Sym^2(M)
        #
        pmz_lst = Veronese.get_pmz_lst()

        # compute automorphisms double Segre surface
        #
        c0, c1, c2, c3, c4, c5, c6, c7, c8 = c_lst
        x0, x1, x2 = ring( 'x0,x1,x2' )
        s, t, u = ring( 's,t,u' )  # coordinates of P^2
        dct1 = {}
        dct1.update( {s: c0 * x0 + c1 * x1 + c2 * x2} )
        dct1.update( {t: c3 * x0 + c4 * x1 + c5 * x2} )
        dct1.update( {u: c6 * x0 + c7 * x1 + c8 * x2} )
        dct2 = {x0:s, x1:t, x2:u}
        spmz_lst = [ pmz.subs( dct1 ).subs( dct2 ) for pmz in pmz_lst]

        # compute matrix from reparametrization "spmz_lst"
        # this is a representation of element in Aut(P^1xP^1)
        #
        mat = []
        for spmz in spmz_lst:
            row = []
            for pmz in pmz_lst:
                row += [spmz.coefficient( pmz )]
            mat += [row]
        mat = sage_matrix( MARing.FF, mat )

        MATools.p( 'c_lst =', c_lst )
        MATools.p( 'mat =\n' + str( mat ) )

        return mat


    @staticmethod
    def get_qmat():
        '''
        Returns
        -------
        sage_matrix
            A symmetric 5x5 matrix with entries in the 
            ring QQ[q0,...,q5] which is a subring 
            of "MARing.R". It represents the Gramm matrix 
            of a quadratic form in the ideal of the              
            Veronese with ideal defined by ".get_ideal_lst()".                        
        '''
        x = MARing.x()[:6]
        q = MARing.q()[:6]

        g_lst = Veronese.get_ideal_lst()
        qpol = 0
        for i in range( len( g_lst ) ):
            qpol += q[i] * g_lst[i]

        qmat = sage_invariant_theory.quadratic_form( qpol, x ).as_QuadraticForm().matrix()
        qmat = sage_matrix( MARing.R, qmat )

        return qmat


    @staticmethod
    def get_invariant_q_lst( c_lst ):
        '''                        
        Parameters
        ---------- 
        c_lst : list 
            A list of length 9 with elements c0,...,c8 
            in the subring in QQ(k)  of "MARing.FF". 
            The matrix                             
                [ c0 c1 c2 ]
            M = [ c3 c4 c5 ]
                [ c6 c7 c8 ]                                                       
            represents---for each value of k---an 
            automorphism of P^2. If we set k:=0 then 
            "c_lst" must correspond to the identity matrix: 
            [ 1,0,0, 0,1,0, 0,0,1 ]. If M is not normalized
            to have determinant 1 then the method should be 
            taken with care (see doc. ".get_c_lst_lst_dct"). 
                                                                                     
        Returns
        -------
        list<MARing.R>
            A list of generators of an ideal J in the subring 
            QQ[q0,...,q6] of "MARing.R". 
               
            Each point p in the zeroset V(J), when substituted in the matrix 
                ".get_qmat()",
            defines a quadratic form in the ideal 
                ".get_ideal_lst()"
            that is preserved by a 1-parameter subgroup H,                                         
            where H is the representation of M in P^5 (see ".get_aut_P5()"). 
            Thus H corresponds to a 1-parameter subgroup of Aut(P^5), 
            such that each automorphism preserves the Veronese surface 
            in projective 5-space P^5.
               
        '''
        # get representation of 1-parameter subgroup in Aut(P^5)
        #
        H = Veronese.get_aut_P5( c_lst )

        # consider the tangent vector of the curve H at the identity
        #
        k = ring( 'k' )
        D = MARing.diff_mat( H, k ).subs( {k:0} )
        MATools.p( 'D =\n' + str( D ) )

        # Note that if we differentiate the condition
        # A=H.T*A*H on both sides, evaluate k=0, then
        # we obtain the condition D.T * A + A * D=0.
        # Here A denotes the matrix of a quadratic form
        # in the ideal of the double Segre surface S.
        #
        A = Veronese.get_qmat()
        Z = D.T * A + A * D
        iq_lst = [iq for iq in Z.list() if iq != 0 ]
        MATools.p( 'qi_lst =', iq_lst )

        return iq_lst


    @staticmethod
    def get_invariant_qf( c_lst_lst ):
        '''
        Parameters
        ----------    
        c_lst_lst : list 
            A list of "c_lst"-lists.
            A c_lst is a list of length 9 with elements 
            c0,...,c8 in the subring in QQ(k)  of "MARing.FF". 
            The matrix                         
                [ c0 c1 c2 ]
            M = [ c3 c4 c5 ]
                [ c6 c7 c8 ]                                                         
            represents---for each value of k---an 
            automorphism of P^2. If we set k:=0 then 
            "c_lst" must correspond to the identity matrix: 
            [ 1,0,0, 0,1,0, 0,0,1 ]. If M is not normalized
            to have determinant 1 then the method should be 
            taken with care (see doc. ".get_c_lst_lst_dct").         
        
        Returns
        -------
        list<MARing.R>
            A list of quadratic forms in the ideal of the Veronese surface V
            (see ".get_ideal_lst()"), such that the quadratic forms are 
            invariant under the automorphisms of V as defined by "c_lst_lst"
            and such that the quadratic forms generate the module of  
            all invariant quadratic forms. Note that Aut(V)=Aut(P^2).   
        '''

        # for verbose output
        #
        mt = MATools()

        # initialize vectors for indeterminates of "MARing.R"
        #
        x = MARing.x()[:6]
        q = MARing.q()[:6]
        r = MARing.r()[:6]

        # obtain algebraic conditions on q0,...,q19
        # so that the associated quadratic form is invariant
        # wrt. the automorphism defined by input "c_lst_lst"
        #
        iq_lst = []
        for c_lst in c_lst_lst:
            iq_lst += Veronese.get_invariant_q_lst( c_lst )
        iq_lst = list( MARing.R.ideal( iq_lst ).groebner_basis() )

        # solve the ideal defined by "iq_lst"
        #
        sol_dct = MARing.solve( iq_lst, q )

        # substitute the solution in the quadratic form
        # associated to the symmetric matrix qmat.
        #
        qmat = Veronese.get_qmat()
        qpol = list( sage_vector( x ).row() * qmat * sage_vector( x ).column() )[0][0]
        sqpol = qpol.subs( sol_dct )
        mt.p( 'sqpol   =', sqpol )
        mt.p( 'r       =', r )
        assert sqpol.subs( {ri:0 for ri in r} ) == 0
        iqf_lst = []  # iqf=invariant quadratic form
        for i in range( len( r ) ):
            coef = sqpol.coefficient( r[i] )
            if coef != 0:
                iqf_lst += [ coef ]
        mt.p( 'iqf_lst =', iqf_lst )

        return iqf_lst


    @staticmethod
    def get_c_lst_lst_dct():
        '''
        Returns
        -------
        dict
            A dictionary "dct" whose keys are one of the following:            
              
              dct['SL3(C)'] : @ complex sl3
              dct['SO3(R)'] : @ real so3 
              
            where the symbol @ is shorthand for the sentence:
                
                @=" A list of 1-parameter subgroups, such that the tangent vectors 
                    of the corresponding curves at the identity generate the Lie 
                    algebra: "
              
            Thus the values of "dct" are lists of 8 "c_lst" lists, so that each 
            "c_lst" represents a 1-parameter subgroup of SL3 and the tangent
            vectors of these 1-parameter subgroups at the identity generate 
            a Lie algebra. More concretely: a "c_lst" is a list of 
            length 9 with elements c0,...,c8 in the subring in QQ(k) of 
            "MARing.FF". The matrix 
            
                  [ c0 c1 c2 ]
              M = [ c3 c4 c5 ]
                  [ c6 c7 c8 ]
              
            is (if possible) normalized to have determinant one and represents
            ---for each value of k---an automorphism of P^2. If we 
            set k:=0 then "c_lst" corresponds to the identity matrix: 
                [ 1,0,0, 0,1,0, 0,0,1 ].  
                                
            For rotations
            
            [ cos(k) -sin(k) 0 ]
            [-sin(k)  cos(k) 0 ]
            [      0       0 1 ]
            
            the tangent vector at the identity is
            
            [ 0 -1 0 ]
            [ 1  0 0 ]
            [ 0  0 0 ]
            
            We can not find a 1-parameter subgroup in terms
            of polynomials in k such that its tangent vector at
            the identity is the same as the rotation matrix
            above. However, we can---in this case--- use
            the matrix:
            
            [  1  k  0 ]
            [ -k  1  0 ]
            [  0  0  1 ]
            
            although it does not have determinant 1. The reason 
            is because ".get_aut_P^5()" followed by differentation 
            wrt k and setting k=0, gives the same result.                                        
        '''

        k = ring( 'k' )
        K = k + 1
        L = 1 / K

        h1 = [K, 0, 0,
              0, L, 0,
              0, 0, 1]

        h2 = [1, 0, 0,
              0, K, 0,
              0, 0, L]

        a1 = [1, k, 0,
              0, 1, 0,
              0, 0, 1]

        a2 = [1, 0, 0,
              0, 1, k,
              0, 0, 1]

        a3 = [1, 0, k,
              0, 1, 0,
              0, 0, 1]

        b1 = [1, 0, 0,
              k, 1, 0,
              0, 0, 1]

        b2 = [1, 0, 0,
              0, 1, 0,
              0, k, 1]

        b3 = [1, 0, 0,
              0, 1, 0,
              k, 0, 1]


        r1 = [  1, k, 0,
              - k, 1, 0,
                0, 0, 1]

        r2 = [1, 0, -k,
              0, 1, 0,
              k, 0, 1]

        r3 = [1, 0, 0,
              0, 1, -k,
              0, k, 1]

        dct = {}
        dct['SL3(C)'] = [h1, h2, a1, a2, a3, b1, b2, b3]
        dct['SO3(R)'] = [r1, r2, r3 ]

        return dct


