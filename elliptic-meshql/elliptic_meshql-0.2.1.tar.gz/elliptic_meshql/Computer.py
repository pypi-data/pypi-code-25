from abc import abstractmethod
from typing import Type

from elliptic.Kernel.Context import ContextDelegate
from elliptic.Kernel.Contract import DSLContract, DSLImplementation
from elliptic.Kernel.Expression import Expression


class MeshQLFunction:
    """MeshQL function. If builtin is set to True, should be an internal function.
    """

    def __init__(self, fun, builtin=False, **kwargs):
        self.fun = fun
        self.builtin = builtin
        self.fargs = kwargs


class ComputerImplementationBase(DSLImplementation):

    @abstractmethod
    def map_delegate(self, fun: MeshQLFunction) -> Type[ContextDelegate]:
        raise NotImplementedError

    @abstractmethod
    def reduce_delegate(self, fun: MeshQLFunction) -> Type[ContextDelegate]:
        raise NotImplementedError


class ComputerContract(DSLContract[ComputerImplementationBase]):

    def Map(self, fun: MeshQLFunction) -> 'ComputerContract':
        return self.append_tree(Expression(self.dsl_impl.map_delegate(fun), "Map"))

    def Reduce(self, fun: MeshQLFunction) -> 'ComputerContract':
        return self.append_tree(Expression(self.dsl_impl.reduce_delegate(fun), "Reduce"))
