# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.conf import settings

try: 
    import visa
    driver_ok = True
except ImportError:
    driver_ok = False


class GenericDevice:
    def __init__(self, pyscada_device):
        self._device = pyscada_device
        self.inst = None
        self.connect()
    
    def connect(self):
        """
        establish a connection to the Instrument
        """
        if not driver_ok:
            # todo add to log
            return False
        visa_backend = '@py'  # use PyVISA-py as backend
        if hasattr(settings, 'VISA_BACKEND'):
            visa_backend = settings.VISA_BACKEND
        
        try:
            self.rm = visa.ResourceManager(visa_backend)
        except:
            # todo log
            return False
        try:
            resource_prefix = self._device.visadevice.resource_name.split('::')[0]
            extras = {}
            if hasattr(settings, 'VISA_DEVICE_SETTINGS'):
                if resource_prefix in settings.VISA_DEVICE_SETTINGS:
                    extras = settings.VISA_DEVICE_SETTINGS[resource_prefix]
            
            self.inst = self.rm.open_resource(self._device.visadevice.resource_name, **extras)
        except:
            # todo log
            return False
        return True
    
    def disconnect(self):
        if self.inst is not None:
            self.inst.close()
            self.inst = None
            return True
        return False

    def read_data(self, variable_instance):
        """
        read values from the device
        """
        
        return None
    
    def write_data(self, variable_id, value):
        """
        write values to the device
        """
        return False
