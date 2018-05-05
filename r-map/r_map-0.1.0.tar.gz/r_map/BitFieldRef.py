from .Node import Node
class BitFieldRef(Node):
    _nb_attrs = ('slice_width', 'reg_offset', 'field_offset')
    """Class to represent a represent a reference to a bitfield. This is useful
    as a register may only have access to a portion of bitfield. The "portion"
    is modelled with this class"""

    def __init__(self, slice_width=1, reg_offset=0, field_offset=0, **kwargs):
        """Initializer for BitFieldRef class
        Definition here merely to define default arguments"""

        super().__init__(slice_width=slice_width, reg_offset=reg_offset,
                field_offset=field_offset, **kwargs)

        self.mask = (1 << slice_width) - 1

    @property
    def bf(self):
        return next(iter(self._children.values()))

    @bf.setter
    def bf(self, bitfield):
        self._children.clear()
        self._children[bitfield.name] = bitfield
        bitfield.references.add(self)

    def _add(self, bitfield):
        super()._add(bitfield)
        bitfield.references.add(self)

    @property
    def value(self):
        return ((self.bf.value >> self.field_offset) & self.mask) << self.reg_offset

    @value.setter
    def value(self, new_value):
        bf = self.bf

        old_bf_value = bf.value & ~(self.mask << self.field_offset)
        new_value = (new_value >> self.reg_offset) & self.mask

        bf.value = old_bf_value | (new_value << self.field_offset)




