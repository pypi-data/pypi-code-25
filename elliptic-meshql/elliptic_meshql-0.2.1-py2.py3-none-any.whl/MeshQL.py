from .Computer import ComputerContract, ComputerImplementationBase
from .Manager import ManagerContract, ManagerImplementationBase
from .Selector import SelectorContract, SelectorImplementationBase


class MeshQLContract(ComputerContract, ManagerContract, SelectorContract):
    pass
