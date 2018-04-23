'''
Created on Nov 26, 2017

@author: Salim
'''
from pylods.deserialize import Parser
from pylods.dict import Dictionary
import ijson
import json
from pylods.mapper import ObjectMapper
from pylods.serialize import DataFormatGenerator
from pylods.backend.pylodsp.mapper import PyObjectMapper


class JSONDictionary(Dictionary):
    
    def __init__(self):
        super(JSONDictionary, self).__init__()
    
    def gen_events(self, instream):
        '''
            generates events from parsing the input stream
        '''
        return ijson.parse(instream)
    
    def is_obj_start(self, event):
        '''
            indicates if the given or a tuple representing an start of object event
            :param event:
        '''
        return event[1] == u'start_map'
    
    def is_obj_end(self, event):
        '''
            indicates if the given or a tuple representing an end of object event
            :param event:
        '''
        return event[1] == u'end_map'
        
    def is_value(self, event):
        '''
            indicates if the given or tuple representing an event that represents a raw value
            :param event:
        '''
        return event[2] is not None or (event[1] == 'null' or event[1] == u'null')
        
    def is_obj_property_name(self, event):
        '''
         indicates if the given event or tuple representing an event is a property name. 
          This library expects to receive the value of the property next. If this value is 
          an object or array, start event for an array or map is expected.
          
        :param event:
        '''
        return event[1] == u'map_key'
         
    def is_array_start(self, event):
        '''
            indicates if the given or tuple representing an event that indicates start of an array
            :param event:
        '''
        return event[1] == u'start_array'
    
    def is_array_end(self, event):
        '''
            indicates if the given or tuple representing an event that indicates end of an array
            :param event:
        '''
        return event[1] == u'end_array'
    
    def read_value(self, event):
        '''
            Returns the value of an ijson event 
        '''
        return event[2]
    
    
    ######################### OBJECT
    
    def write_object_start(self, numfields, outstream):
        outstream.write("{")

    def write_object_end(self, numfields, outstream):
        outstream.write("}")
    
    def write_object_field_separator(self, name, value, outstream):
        outstream.write(", ")
    
    def write_object_field_name(self, name, outstream):
        outstream.write('"' + name + '\"')
    
    def write_object_name_value_separator(self, name, value, outstream):
        outstream.write(': ')

    ######################### ARRAY
    
    def write_array_start(self, length, outstream):
        outstream.write(' [')
    
    def write_array_end(self, length, outstream):
        outstream.write(' ]')
    
    def write_array_field_separator(self, value, outstream):
        outstream.write(', ')
     
    
    ######################### DICT
    
    def write_dict_start(self, numfields, outstream):
        outstream.write('{ ')
    
    def write_dict_end(self, numfields, outstream):
        outstream.write(' }')
    
    def write_dict_field_separator(self, name, value, outstream):
        outstream.write(', ')    
    
    def write_dict_field_name(self, name, outstream):
        outstream.write('"'+name+'"')
    
    def write_dict_name_value_separator(self, name, value, outstream):
        outstream.write(': ')

    
    def write_value(self, val, outstream):
        json.dump(val,outstream)
            
    
    


class JsonParser(Parser):
    '''
        Json Parser extends PylodsParser while using a JsonDictionary
    '''
    
    
    def __init__(self):
        Parser.__init__(self, JSONDictionary())
        


class JsonObjectMapper(ObjectMapper):
    '''
        ObjectMapper for JSON
    '''
    
    
    def __init__(self, backend=None):
        if(backend is None):
            ObjectMapper.__init__(self,PyObjectMapper(JSONDictionary()));
        else:
            ObjectMapper.__init__(self,backend);
        
        

class JsonGenerator(DataFormatGenerator):
    
    
    def __init__(self):
        super(JsonGenerator, self).__init__(JSONDictionary())
        
