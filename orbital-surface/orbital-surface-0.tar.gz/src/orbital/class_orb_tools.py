'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Nov 23, 2017
@author: Niels Lubbes
'''

from sage_interface import sage_save
from sage_interface import sage_load

import inspect
import time
import sys
import os

class OrbTools():
    '''
    For accessing static variables in python see for example:
    <http://stackoverflow.com/questions/68645/static-class-variables-in-python>    
    '''

    # Private dictionary object for caching result
    # used by ".get_tool_dct()" and ".save_tool_dct()".
    # If "enable_tool_dct" is false then caching in
    # disabled. This is useful for example in test
    # methods. However, it should be noted that it
    # could take a long time to compute the data.
    #
    __tool_dct = None
    __enable_tool_dct = True

    # private variable for timer
    #
    __start_time = None
    __end_time = None

    # private static variables used by ".p()"
    # If "__filter_fname_lst" equals [] then output is surpressed.
    # If "__filter_fname_lst" equals None the no output is surpressed
    #
    __filter_fname_lst = []
    __prev_filter_fname_lst = None


    @staticmethod
    def filter( filter_fname_lst ):
        '''
        It is adviced to access this method as statically as OrbTools.filter().  
        See OrbTools.p() for more details.
        
        Parameters
        ----------
        filter_fname_lst : list<str> 
            List of file names for Python modules.
            If None, then no output is surpressed by method ".p()". 
        '''
        OrbTools.__filter_fname_lst = filter_fname_lst
        OrbTools.__prev_filter_fname_lst = filter_fname_lst


    @staticmethod
    def filter_unset():
        '''
        Output via ".p()" will not be surpressed.
        '''
        OrbTools.__filter_fname_lst = None


    @staticmethod
    def filter_reset():
        '''
        Resets filter state to before previous ".filter_unset()" call.
        '''
        OrbTools.__filter_fname_lst = OrbTools.__prev_filter_fname_lst


    @staticmethod
    def p( *arg_lst ):
        '''
        Parameters
        ----------
        *arg_lst
            Variable length argument list.
        
        Returns
        -------
        string
            If ".filter_on(<fname>)" has been called and the file name
            of the calling module does not coincide with <fname>
            and <fname>!=None, then the output is surpressed and 
            "None" is returned.
                                                     
            Otherwise, this method prints arguments to "sys.stdout" 
            together with reflection info from "inspect.stack()".
            Additional returns the output string.
              
            Call ".filter_off()" to turn off filter, such that
            all output is send to "sys.stdout".                                     
        '''
        # collect relevant info from stack trace
        sk_lst_lst = inspect.stack()
        file_name = os.path.basename( str( sk_lst_lst[1][1] ) )  # exclude path from file name
        line = str( sk_lst_lst[1][2] )
        method_name = str( sk_lst_lst[1][3] )

        # only output when .p() is called from module whose
        # file name is in OrbTools.__filter_fname_lst
        if OrbTools.__filter_fname_lst != None:
            if not file_name in OrbTools.__filter_fname_lst:
                return

        # construct output string
        s = method_name + '(' + line + ')' + ': '
        for arg in arg_lst:
            s += str( arg ) + ' '

        # print output
        print( s )
        sys.stdout.flush()

        return s


    @staticmethod
    def set_enable_tool_dct( enable_tool_dct ):
        OrbTools.__enable_tool_dct = enable_tool_dct


    @staticmethod
    def get_tool_dct( fname = 'orb_tools' ):
        '''
        Parameters
        ----------
        fname : str
            Name of file without extension.
        
        Returns
        -------
        dct
            Sets static private variable "__tool_dct" 
            in memory from file "<local path>/<fname>.sobj"
            if called for the first time.
              
            Returns ".__tool_dct" if ".__enable_tool_dct==True" 
            and "{}" otherwise.
        '''
        if not OrbTools.__enable_tool_dct:
            OrbTools.filter_unset()
            OrbTools.p( 'Caching is disabled!' )
            OrbTools.filter_reset()
            return {}

        path = os.path.dirname( os.path.abspath( __file__ ) ) + '/'
        file_name = path + fname
        if OrbTools.__tool_dct == None:

            OrbTools.filter_unset()
            try:

                OrbTools.p( 'Loading from:', file_name )
                OrbTools.__tool_dct = sage_load( file_name )

            except Exception as e:

                OrbTools.p( 'Cannot load ".__tool_dct": ', e )
                OrbTools.__tool_dct = {}

            OrbTools.filter_reset()

        return OrbTools.__tool_dct


    @staticmethod
    def save_tool_dct( fname = 'orb_tools' ):
        '''
        Saves ".__tool_dct" to  "fname" if ".enable_tool_dct==True" 
        otherwise do nothing.
        
        Parameters
        ----------
        fname : str
            Name of file without extension.
        '''
        if not OrbTools.__enable_tool_dct:
            return

        path = os.path.dirname( os.path.abspath( __file__ ) ) + '/'
        file_name = path + fname

        OrbTools.filter_unset()
        OrbTools.p( 'Saving to:', file_name )
        OrbTools.filter_reset()

        sage_save( OrbTools.__tool_dct, file_name )


    @staticmethod
    def start_timer():
        '''
        Prints the current time and starts timer.
        '''
        # get time
        OrbTools.__start_time = time.clock()  # set static variable.

        OrbTools.filter_unset()
        OrbTools.p( 'start time =', OrbTools.__start_time )
        OrbTools.filter_reset()


    @staticmethod
    def end_timer():
        '''
        Prints time passed since last call of ".start_timer()".
        '''
        OrbTools.__end_time = time.clock()
        passed_time = OrbTools.__end_time - OrbTools.__start_time

        OrbTools.filter_unset()
        OrbTools.p( 'time passed =', passed_time )
        OrbTools.filter_reset()




