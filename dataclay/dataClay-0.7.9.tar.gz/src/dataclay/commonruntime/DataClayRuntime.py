import lru
from dataclay.heap.LockerPool import LockerPool
from abc import ABCMeta, abstractmethod
import logging
from dataclay.communication.grpc.messages.common.common_messages_pb2 import LANG_PYTHON


class DataClayRuntime(object):
    
    """ Make this class abstract """
    __metaclass__ = ABCMeta
    
    """ Logger """ 
    logger = logging.getLogger('dataclay.api')
    
    def __init__(self):
        """ Cache of alias """
        # FIXME un-hardcode this
        self.alias_cache = lru.LRU(50)
        
        """ GRPC clients """
        self.ready_clients = dict()
        
        """ Cache of classes. TODO: is it used?"""
        self.local_available_classes = dict()
        
        """  Heap manager. Since it is abstract it must be initialized by sub-classes. 
        DataClay-Java uses abstract functions to get the field in the proper type (EE or client) 
        due to type-check. Not needed here. """
        self.dataclay_heap_manager = None
        
        """ Object loader. """
        self.dataclay_object_loader = None
        
        """  Locker Pool in runtime. This pool is used to provide thread-safe implementations in dataClay. """
        self.locker_pool = LockerPool() 
        """ Metadata cache """
        self.metadata_cache = None
        """ Indicates if runtime was initialized. TODO: check if same in dataclay.api """
        self.is_initialized = False

    @abstractmethod
    def initialize_runtime_aux(self): pass
    
    def initialize_runtime(self):
        """ 
        IMPORTANT: getRuntime can be called from decorators, during imports, and therefore a runtime might be created. 
        In that case we do NOT want to create threads to start. Only if "init" was called (client side) or 
        server was started. This function is for that.
        """
        self.logger.debug("INITIALIZING RUNTIME")
        self.initialize_runtime_aux()
        self.dataclay_heap_manager.start()

    def is_initialized(self):
        """
        @return: TRUE if runtime is initialized (Client 'init', EE should be always TRUE). False otherwise.
        """
        return self.__initialized
        
    @abstractmethod
    def is_exec_env(self):
        """
        @return: TRUE if runtime is for EE. False otherwise.
        """
        pass
    
    def add_to_heap(self, dc_object):
        """
        @postcondition: the object is added to dataClay's heap
        @param dc_object: object to add to the heap 
        """
        self.dataclay_heap_manager.add_to_heap(dc_object)
        
    def remove_from_heap(self, object_id):
        """
        @postcondition: Remove reference from Heap. Even if we remove it from the heap, 
        the object won't be Garbage collected till HeapManager flushes the object and releases it.
        @param object_id: id of object to remove from heap
        """
        self.dataclay_heap_manager.remove_from_heap(object_id)
        
    def get_from_heap(self, object_id):
        """
        @postcondition: Get from heap. 
        @param object_id: id of object to get from heap
        @return Object with id provided in heap or None if not found.
        """
        return self.dataclay_heap_manager.get_from_heap(object_id)
    
    def lock(self, object_id):
        """
        @postcondition: Lock object with ID provided
        @param object_id: ID of object to lock 
        """
        self.locker_pool.lock(object_id)
        
    def unlock(self, object_id):
        """
        @postcondition: Unlock object with ID provided
        @param object_id: ID of object to unlock 
        """
        self.locker_pool.unlock(object_id)    
        
    def get_metadata_backup_address(self):
        """
        @postcondition: Get backup info
        @return: LM Backup address
        """
        backup_info = self.ready_clients["@LM"].get_backup_info()
        return str(backup_info[0]) + ":" + str(backup_info[1])
    
    def get_backendids_in_location(self, address):
        """
        @postcondition: Get backend ids in address provided in python language
        @param: address
        @return: backend ids in address 
        """
        return self.ready_clients["@LM"].get_backendids_in_location(address, LANG_PYTHON)
    
    def get_executionenvironmentid_for_ds(self, srvname):
        """
        @postcondition: Get Backend ID in host with name provided in python language
        @param: hostname
        @return: backend id in host 
        """
        return self.ready_clients["@LM"].get_executionenvironmentid_for_ds(srvname, LANG_PYTHON)
   
    def stop_gc(self):
        """
        @postcondition: stop GC. useful for shutdown. 
        """ 
        # Stop HeapManager
        self.logger.debug("Stopping GC. Sending shutdown event.")
        self.dataclay_heap_manager.shutdown()
        self.logger.debug("Waiting for GC.")
        self.dataclay_heap_manager.join()
        self.logger.debug("GC stopped.")

    def stop_runtime(self):
        """ 
        @postcondition: Stop connections and daemon threads. 
        """ 
        self.logger.verbose("** Stopping runtime **")
        for name, client in self.ready_clients.iteritems():
            self.logger.verbose("Closing client connection to %s", name)
            client.close()
        
        # Stop HeapManager
        self.stop_gc()
        