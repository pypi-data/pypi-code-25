class Cache(object):
    """Cache system, storing data for later retrieval.
    """
    # TODO: Figure out actual interface for this
    def has_key(self, key):
        """Indicates whether a value is in the cache.
        """
        raise NotImplementedError

    def get(self, key):
        """Gets a value from the cache.
        """
        raise NotImplementedError

    def store(self, key, value):
        """Stores a new value to the cache.
        """
        raise NotImplementedError


class NullCache(Cache):
    """Dumb cache that doesn't store anything.
    """
    def has_key(self, key):
        return False

    def get(self, key):
        raise KeyError(key)

    def store(self, key, value):
        pass


class MemoryCache(Cache):
    """In-memory cache that simply stores everything in a dict.
    """
    def __init__(self):
        self.store = {}

    def has_key(self, key):
        return key in self.store

    def get(self, key):
        return self.store[key]

    def store(self, key, value):
        self.store[key] = value


class Module(object):
    """A module, as provided by a `ModuleLoader`.
    """
    def __call__(self, inputs, output_names, **kwargs):
        """Run on the inputs to provide outputs.
        """
        raise NotImplementedError


class ModuleLoader(object):
    """Module loader, capable of providing modules used by workflow steps.
    """
    def get_module(self, module):
        """Returns a module or None.
        """
        raise NotImplementedError


class Workflow(object):
    # TODO: Add more indexes in here (connection from step, ...)
    # TODO: Provide an abstract base for this too (for SQL backend)
    def __init__(self, steps, connections, meta):
        self.steps = steps
        self.connections = connections
        self.meta = meta

    def __repr__(self):
        return '<Workflow\n  steps:{}\n  connections:{}\n  meta={!r}>'.format(
            ''.join('\n    {!r}'.format(s) for s in self.steps.values()),
            ''.join('\n    {!r}'.format(c) for c in self.connections.values()),
            self.meta,
        )


class Step(object):
    def __init__(self, id, module_def, inputs, outputs, parameters):
        self.id = id
        self.module_def = module_def
        self.inputs = inputs
        self.outputs = outputs
        self.parameters = parameters

    def __repr__(self):
        return '<Step {!r} inputs={!r} outputs={!r} parameters={!r}>'.format(
            self.id,
            sorted(self.inputs),
            sorted(self.outputs),
            list(self.parameters),
        )


class Connection(object):
    def __init__(self, id,
                 from_step_id, from_output_name, to_step_id, to_input_name):
        self.id = id
        self.from_step_id = from_step_id
        self.from_output_name = from_output_name
        self.to_step_id = to_step_id
        self.to_input_name = to_input_name

    def __repr__(self):
        return '<Connection {!r} {!r}.{!r} --> {!r}.{!r}>'.format(
            self.id,
            self.from_step_id,
            self.from_output_name,
            self.to_step_id,
            self.to_input_name,
        )
