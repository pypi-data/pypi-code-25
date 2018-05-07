import vaex.utils
from traitlets import *

class HasState(HasTraits):

    @classmethod
    def state_from(cls, state):
        obj = cls()
        obj.state_set(state)
        return obj

    def state_get(self):
        return {name: getattr(self, name) for name in self.trait_names()}

    def state_set(self, state):
        for name in self.trait_names():
            if name in state:
                setattr(self, name, state[name])

    def state_write(self, f):
        vaex.utils.write_json_or_yaml(f, self.state_get())

    def state_load(self, f):
        state = vaex.utils.read_json_or_yaml(f)
        self.state_set(state)


