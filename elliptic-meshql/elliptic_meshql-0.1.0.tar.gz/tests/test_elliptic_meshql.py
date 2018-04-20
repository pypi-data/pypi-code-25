from typing import Type

from elliptic.Kernel.Context import ContextDelegate

from elliptic_meshql.Computer import ComputerImplementationBase
from elliptic_meshql.Manager import ManagerImplementationBase
from elliptic_meshql.MeshQL import MeshQLContract
from elliptic_meshql.Selector import SelectorImplementationBase


class MeshQLImplementationBase(ComputerImplementationBase, ManagerImplementationBase, SelectorImplementationBase):
    def map_delegate(self, fun) -> Type[ContextDelegate]:
        pass

    def reduce_delegate(self, fun) -> Type[ContextDelegate]:
        pass

    def solve_delegate(self) -> Type[ContextDelegate]:
        pass

    def store_delegate(self) -> Type[ContextDelegate]:
        pass

    def by_ent_delegate(self, dim: int) -> Type[ContextDelegate]:
        pass

    def by_adj_delegate(self, bridge_dim: int, to_dim: int) -> Type[ContextDelegate]:
        pass

    def base_delegate(self) -> Type[ContextDelegate]:
        pass


def test_meshql_interface():
    root = MeshQLContract(MeshQLImplementationBase())

    root.Base().ByEnt(3).ByAdj(2, 3).Map(None).Reduce(None).Solve().Store()
