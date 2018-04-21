from abc import abstractmethod
from typing import Type

from elliptic.Kernel.Context import ContextDelegate
from elliptic.Kernel.Contract import DSLContract, DSLImplementation
from elliptic.Kernel.Expression import Expression


class ManagerImplementationBase(DSLImplementation):

    @abstractmethod
    def solve_delegate(self) -> Type[ContextDelegate]:
        raise NotImplementedError

    @abstractmethod
    def store_delegate(self) -> Type[ContextDelegate]:
        raise NotImplementedError


class ManagerContract(DSLContract[ManagerImplementationBase]):

    def Solve(self) -> 'ManagerContract':
        return self.append_tree(Expression(self.dsl_impl.solve_delegate(), "Solve"))

    def Store(self) -> 'ManagerContract':
        return self.append_tree(Expression(self.dsl_impl.store_delegate(), "Store"))
