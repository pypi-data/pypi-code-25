"""
Module to provide functionality to serialize and deserialize r_map data to JSON.
A custom encoder/decoder is implemented to facilitate this.

TODO: provide support to handle copies or references in the JSON data.
Idea is that a bitfield might be referenced by more than one BitFieldRef object.
This should be represented in the JSON object's dictionary as __ref__:<uuid>
where <uuid> is the uuid of the object being referenced.

Additionally, the ability to provide a deep copy of an object (object tree)
would be very useful and suitably reprented in the JSON dictionary as being
__copy__:<uuid>, <key_override>:<data_override> where additional key-value pairs
can be added to specialize the copy by overriding the values taken from the
original.
"""
import json
from collections import defaultdict
from .RMapFactory import RMapFactory

class RMapJSONParseError(KeyError):
    pass

class RMapJSON(json.JSONEncoder):
    already_encoded = set()
    def default(self, o):
        if o in self.already_encoded:
            return {'__ref__' : o.uuid}
        elif isinstance(o, RMapFactory.Node):
            dct = {n:getattr(o,n) for n in o._nb_attrs}
            dct['__type__'] = type(o).__name__
            if o._children:
                dct['children'] = list(o._children.values())
            self.already_encoded.add(o)
            return dct
        elif isinstance(o, set):
            return list(o)
        else:
            return json.JSONEncoder.default(self, o)

def to_json(node, **kwargs):
    RMapJSON.already_encoded.clear()
    return json.dumps(node, cls=RMapJSON, **kwargs)

def from_json(json_str, **kwargs):
    decoder, decoded, todo = get_decoder()

    root = json.loads(json_str, object_hook=decoder, **kwargs)

    #now finish up the decoding process
    for parent_uuid, ref_list in todo.items():
        try:
            parent = decoded[parent_uuid]
        except KeyError as e:
            raise RMapJSONParseError("Cannot find object with uuid: %s "
                                     "which is referenced by another node".format(
                                         parent_uuid)) from e
        for ref_uuid in ref_list:
            try:
                ref_obj = decoded[ref_uuid]
            except KeyError as e:
                raise RMapJSONParseError("Cannot find object with uuid: %s "
                                "referenced from child %s with parent uuid: %s".format(
                                    ref_uuid, parent_uuid))
            parent._add(ref_obj)
            ref_obj.parent = parent

    return root

def get_decoder():
    """Create a closure to hold a dictionary of already decoded items"""
    decoded = {}
    todo = defaultdict(list)
    def decoder(dct):
        if '__type__' in dct:
            #print("In decoder, dct: ", dct)
            obj_type = getattr(RMapFactory, dct.pop('__type__'))
            obj = obj_type(**{k:dct.get(k) for k in obj_type._nb_attrs})
            decoded[obj.uuid] = obj
            if 'children' in dct:
                for child in dct['children']:
                    if isinstance(child, dict):
                        ref = child.get('__ref__')
                        if ref:
                            parent_uuid = obj.uuid
                            todo[parent_uuid].append(ref)
                    else:
                        obj._add(child)
                        child.parent = obj
            return obj
        else:
            return dct
    return decoder, decoded, todo



