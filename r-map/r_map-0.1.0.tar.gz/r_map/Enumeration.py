from .Node import Node
import r_map.BitField
class Enumeration(Node):
    _nb_attrs = ('value',)

    __hash__ = Node.__hash__

    def __str__(self):
        return super().__str__() + ' value: {}'.format(self.value)

    def __eq__(self, other):
        if isinstance(other, (Enumeration,  r_map.BitField.BitField)):
            return self.value == other.value
        elif isinstance(other, int):
            return self.value == other
        else:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, (Enumeration,  r_map.BitField.BitField)):
            return self.value < other.value
        elif isinstance(other, int):
            return self.value < other
        else:
            return NotImplemented

    def __le__(self, other):
        if isinstance(other, (Enumeration, r_map.BitField.BitField)):
            return self.value <= other.value
        elif isinstance(other, int):
            return self.value <= other
        else:
            return NotImplemented

    def __gt__(self, other):
        if isinstance(other, (Enumeration, r_map.BitField.BitField)):
            return self.value > other.value
        elif isinstance(other, int):
            return self.value > other
        else:
            return NotImplemented

    def __ge__(self, other):
        if isinstance(other, (Enumeration, r_map.BitField.BitField)):
            return self.value >= other.value
        elif isinstance(other, int):
            return self.value >= other
        else:
            return NotImplemented




