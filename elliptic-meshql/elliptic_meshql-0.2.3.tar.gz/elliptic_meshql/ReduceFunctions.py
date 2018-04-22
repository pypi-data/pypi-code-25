from .Computer import MeshQLFunction


class Sum(MeshQLFunction):

    def __init__(self, initial_value):
        super().__init__('initial_value', builtin=True, initial_value=initial_value)
