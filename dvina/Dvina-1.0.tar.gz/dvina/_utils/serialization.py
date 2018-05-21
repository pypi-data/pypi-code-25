from numpy.random import RandomState
from jsonpickle import handlers
import jsonpickle
from .classes import get_class
import jsonpickle.ext.numpy as jsonpickle_numpy

jsonpickle_numpy.register_handlers()


class DvinaSerialization(handlers.BaseHandler):
    """Jsonpickle serialization handler

    To serialize a class, decorate the class with @DvinaSerialization.serializes(["field1", "field2", ...])
    This tells jsonpickle to use this handler's flatten and restore methods to (de)serialize the class' fields.

    Note, the class' __init__ method is not called during deserialization. Instead, the class' optional
    'deserialized_init' method is called after the class' deserialized field values are set. The motivation behind
    separating logic between '__init__' and 'deserialized_init' is that there is a difference between constructing
    an item from scratch and from a saved state.
    """

    # dict mapping a serialized class to its field names which are (de)serialized
    _cls_fields = {}

    # the names of the optional methods invoked before and after an object is serialized
    _pre_serialize_method_name = "pre_serialize"
    _post_serialize_method_name = "post_serialize"

    # the name of the optional initialization method that is invoked after deserialization
    _init_method_name = "deserialized_init"

    @staticmethod
    def serializes(fields):
        """Decorates the class that we want to serialize, and specifies which fields will be de(serialized).

        Parameters
        ----------
        fields: list
            a list of strings, each string represents a class field that is de(serialized)
        """

        def wrapper(cls):
            """This maps cls to fields and tells jsonpickle that this serializer handles objects of type cls.

            :param cls: the class being serialized
            :return:
            """
            DvinaSerialization._cls_fields[cls] = fields
            DvinaSerialization.handles(cls)
            return cls

        return wrapper

    def flatten(self, obj, data):
        """Called by jsonpickle when the class instance is being serialized.

        Flattens obj into a json-friendly form and write the result in the data dict

        Parameters
        ----------
        obj: object
            the instance to serialize
        data: dict
            a dict provided by jsonpickle. flatten adds more keys to the dict mapping to json strings

        Returns
        ----------
        dict
            the data dict
        """
        self._call_method_if_exists(obj, self._pre_serialize_method_name)
        persisted_fields = DvinaSerialization._cls_fields[obj.__class__]
        for persisted_field in persisted_fields:
            instance_value = getattr(obj, persisted_field)
            json = jsonpickle.encode(instance_value)
            data[persisted_field] = json
        self._call_method_if_exists(obj, self._post_serialize_method_name)

        return data

    def restore(self, data):
        """Restore the json-friendly obj to the registered type

        Parameters
        ----------
        data : a dict provided by jsonpickle. It contains a 'py/object' key with the pickled class' fully
        qualified name. The other keys map to previously pickled json that needs deserialized.

        Returns
        -------
        object
            a deserialized instance of the pickled object. note, the object's __init__ method is not called. If
            it exists on the object, a function named 'deserialized_init' is called after the serialized fields are set.
            This allows the object to initialize additional fields that are derived from the serialized fields or
            runtime dependencies (like the global logger).
        """
        # data['py/object'] is string representation of module and class, create a new instance
        class_fqn = data['py/object']
        cls = get_class(class_fqn)
        instance = cls.__new__(cls)
        persisted_fields = DvinaSerialization._cls_fields[cls]
        for persisted_field in persisted_fields:
            instance_value = None
            if persisted_field in data:
                json = data[persisted_field]
                instance_value = jsonpickle.decode(json)
            setattr(instance, persisted_field, instance_value)

        self._call_method_if_exists(instance, self._init_method_name)

        return instance

    def _call_method_if_exists(self, instance, method_name):
        """ Calls the instance's method matching the supplied name (if it exists)

        :param instance: the instance of an object whose method we call
        :param method_name: the name of the method to invoke
        """
        method = getattr(instance, method_name, None)
        if callable(method):
            method()


class NumpyRandomStateSerializer(handlers.BaseHandler):
    """Serializes Numpy's RandomState class"""

    def flatten(self, rand_obj, data):
        """Called by jsonpickler when a RandomState is being serialized

        :param rand_obj: the random state instance to serialize
        :param data: a dict we add serializable data to
        :return: the data dict
        """
        # call numpy's method to get a "tuple representing the internal state of the generator"
        random_state = rand_obj.get_state()
        # call encode on the tuple because it contains an ndarray that needs serialized
        data["random_state"] = jsonpickle.encode(random_state)
        return data

    def restore(self, data):
        """Called by jsonpickler when a RandomState is being serialized

        :param data: a dict with the serialized data
        :return: a new RandomState instance
        """
        rand_obj = RandomState()
        decoded_state = jsonpickle.decode(data["random_state"])
        rand_obj.set_state(decoded_state)
        return rand_obj


jsonpickle.handlers.register(RandomState, NumpyRandomStateSerializer, base=True)
