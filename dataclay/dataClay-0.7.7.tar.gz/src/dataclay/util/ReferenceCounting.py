'''
Created on 19 abr. 2018

@author: dgasull
'''
from dataclay.serialization.python.lang.IntegerWrapper import IntegerWrapper
from dataclay.serialization.python.lang.BooleanWrapper import BooleanWrapper
from dataclay.serialization.python.lang.StringWrapper import StringWrapper
import logging 

logger = logging.getLogger("ReferenceCounting")


class ReferenceCounting(object):
    '''
    classdocs+
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.reference_counting = dict()
        self.has_alias = False

    def increment_reference_counting(self, oid, hint):
        
        if not self.reference_counting.has_key(hint): 
            references_per_hint = dict()
            self.reference_counting[hint] = references_per_hint
        else:
            references_per_hint = self.reference_counting.get(hint)
        
        if references_per_hint.has_key(oid):
            num_refs = references_per_hint.get(oid) + 1
        else:
            num_refs = 1
        references_per_hint[oid] = num_refs  
        
    def serialize_reference_counting(self, referrer_oid, io_file):
        """ TODO: IMPORTANT: this should be removed in new serialization by using paddings to directly access reference counters inside
         metadata. """
        """
        @postcondition: Serialize reference counting (garbage collector information)
        @param referrer_oid: ID of referrer object
        @param io_file: Buffer in which to serialize
        @param reference_counting: Reference counting to serialize
        """
                
        BooleanWrapper().write(io_file, self.has_alias)
        IntegerWrapper().write(io_file, len(self.reference_counting))
        for location, ref_counting_in_loc in self.reference_counting.iteritems():
            if location is None:
                BooleanWrapper().write(io_file, True)
            else:
                BooleanWrapper().write(io_file, False)
                StringWrapper().write(io_file, str(location))
            
            IntegerWrapper().write(io_file, len(ref_counting_in_loc))
            for oid, counter in ref_counting_in_loc.iteritems():
                StringWrapper().write(io_file, str(oid))
                IntegerWrapper().write(io_file, counter)
