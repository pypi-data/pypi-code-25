class Nodo:
    def __init__(self, hijos, columna, valores_columna, ganancia, tipo, filas):
        self.hijos = hijos
        self.columna = columna
        self.valores_columna = valores_columna
        self.filas = filas
        self.ganancia = ganancia
        self.tipo = tipo

    def agregar_hijo(self, nodo):
        self.hijos.append


# final de los hijos de un nodo
class Hoja:
    def __init__(self, target):
        self.target = target


class Atributo:
    def __init__(self, ganancia, nombre):
        self.ganancia = ganancia
        self.nombre = nombre
