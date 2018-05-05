from .Node import Node
from .Register import Register
from .BitField import BitField
from .BitFieldRef import BitFieldRef
from .Enumeration import Enumeration
from .RegisterMap import RegisterMap

class RMapFactory:
    Node        = Node
    RegisterMap = RegisterMap
    Register    = Register
    BitFieldRef = BitFieldRef
    BitField    = BitField
    Enumeration = Enumeration


