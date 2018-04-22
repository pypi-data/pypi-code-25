from .Computer import MeshQLFunction


class SetScalar(MeshQLFunction):

    def __init__(self, scalar):
        super().__init__('set_scalar', builtin=True, scalar=scalar)


class GetField(MeshQLFunction):

    def __init__(self, field_name):
        super().__init__('get_field', builtin=True, field_name=field_name)
