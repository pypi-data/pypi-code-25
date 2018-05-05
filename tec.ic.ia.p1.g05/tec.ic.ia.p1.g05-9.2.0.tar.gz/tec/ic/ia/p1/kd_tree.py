import math
import numpy as np
import csv

from g05 import datos_r1_normalizados
from g05 import datos_r2_normalizados
from g05 import datos_r2_con_r1_normalizados
from pc1 import generar_muestra_pais
from pc1 import generar_muestra_provincia

"""
Estructura de los nodos que conforman el arbol
"""


class Node:

    def __init__(self, dimension, data):
<<<<<<< HEAD
        if(not isinstance(data, list) or not isinstance(dimension, int)):
            raise TypeError('El primer argumento debe ser una lista de' +
                            'y el segundo un numero entero')
=======
        if(type(data) is not list or type(dimension) is not int):
            raise TypeError('El primer argumento debe ser un numero entero '+
                            'y el segundo una lista')
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838

        self.left = None
        self.right = None
        self.dimension = dimension
        self.data = data

    def insert_node(self, data, dimension):
        if(not isinstance(data, list) or not isinstance(dimension, int)):
            raise TypeError('El primer argumento debe ser una lista de' +
                            'y el segundo un numero entero')

        if data:
            if data[self.dimension] < self.data[self.dimension]:
                self.left = Node(dimension, data)
                return self.left
            if data[self.dimension] >= self.data[self.dimension]:
                self.right = Node(dimension, data)
                return self.right

    def insert_leaf(self, data, isMinor):
        if(not isinstance(data, list) or not isinstance(isMinor, bool)):
            raise TypeError('El primer argumento debe ser una lista de' +
                            'y el segundo un boolean')
        if isMinor:
            self.left = Node(-1, data)
        else:
            self.right = Node(-1, data)

    def print_tree(self):
        print(self.data)

# ----------------------------------------------------------------------------


"""
Entradas: data corresponde a los datos que se utilzaran para entrenar el
          modelo, k se asocia con el numero de vecinos
Salidas: Retorna la raiz del arbol("Node")
Descripcion: Funcion que crea la estructura del arbol
Restricciones: data debe ser una matriz y k un numero entero
"""


def create_kd_tree(data, k):
    print_level = True
    dimension_len = len(data[0]) - 1
    return create_kd_tree_aux(data, dimension_len, k, None, 0)

# ----------------------------------------------------------------------------


"""
Entradas: data corresponde a los datos que se utilzaran para entrenar el
          modelo, dimension_len es la cantidad de dimensiones que se toman en
          cuenta para contruir el arbol, k la cantidad de vecinos, root es
          el nodo donde se insertaran nuevos nodos y level es el nivel en
          cual se encuentra actualmente
Salidas: Retorna la raiz del arbol("Node")
Descripcion: Funcion que crea la estructura del arbol recursivamente
Restricciones: data debe ser una matriz y k un numero entero, dimension_len
          un entero, root debe ser de la clase "Node", level un entero
"""


def create_kd_tree_aux(data, dimension_len, k, root, level):
    n = len(data)
    random_dimension = level % dimension_len
    sorted_data = sorted(data, key=lambda point: point[random_dimension])
    median = sorted_data[n // 2]

    if root is None:
        new_root = Node(random_dimension, median)
        create_kd_tree_aux(sorted_data[:n // 2], dimension_len,
                           k, new_root, level + 1)
        create_kd_tree_aux(sorted_data[n // 2:], dimension_len,
                           k, new_root, level + 1)
        return new_root
    elif len(data) <= k:
        if len(data) != 0:
            if data[-1][root.dimension] > root.data[root.dimension]:
                root.insert_leaf(data, False)
            else:
                root.insert_leaf(data, True)
    else:
        new_root = root.insert_node(median, random_dimension)
        create_kd_tree_aux(sorted_data[:n // 2], dimension_len,
                           k, new_root, level + 1)
        create_kd_tree_aux(sorted_data[n // 2:], dimension_len,
                           k, new_root, level + 1)

# ----------------------------------------------------------------------------


"""
Entradas: data corresponde a un elemento del set de datos de prueba, left es
          la rama izquierda del arbol, y right es la rama derecha
Salidas: Retorna un elemento de la clase "Node"
Descripcion: Funcion que dada un elemento del set de datos de prueba, verifica
            si el punto mas cercano es la rama izquierda o derecha
Restricciones: data debe ser una lista, y left y right elementos de la clase
              "Node"
"""


def closer_distance(data, left, right):
    if left is None:
        return right
    if right is None:
        return left

    data_left = left.data
    data_right = right.data

    if isinstance(data_left[0], list):
        data_left = closest_point(data_left, data)
    if isinstance(data_right[0], list):
        data_right = closest_point(data_right, data)

    d1 = distance(data, data_left)
    d2 = distance(data, data_right)

    if d1 < d2:
        return left
    else:
        return right

# ----------------------------------------------------------------------------


"""
Entradas: root es el nodo que se evaluando actualmente data corresponde a un
          elemento del set de datos de prueba, y level el nivle en que se
          encuentra la recursion
Salidas: Retorna el valor(float) del partido porque quien votara
Descripcion: Funcion que dado un elemento del set de datos de prueba, recorre
          el arbol hasta encontrar los vecionos mas cercanos(hojas del arbol)
          y devuelve el valor del partido porque quien votara
Restricciones: data debe ser una lista, root un elemento de la clase "Node" y
               level un entero
"""


def kd_tree_find_neighbors(root, data, level=0):
    if root is None:
        return None

    value = root.data
    dimension = root.dimension
    next_branch = None
    opposite_branch = None

    if dimension == -1:
        return get_nearest_neighbors(value)
    else:
        if data[dimension] < value[dimension]:
            next_branch = root.left
            opposite_branch = root.right
        else:
            next_branch = root.right
            opposite_branch = root.left

    best_branch = closer_distance(data, next_branch, opposite_branch)
    return kd_tree_find_neighbors(best_branch, data, level + 1)

# ----------------------------------------------------------------------------


"""
Entradas: data corresponda a las hojas encontradas en la funcion
          "kd_tree_find_neighbors" que representa los vecinos mas cercanos
Salidas: Retorna el valor(float) del partido porque quien votara
Descripcion: Funcion que dado un conjunto de datos del set de entrenamiento
            crea un diccionario que tiene como llave el valor del partido
            por quien voto y el valor es la cantidad de veces que aparece
            ese partido en los demas vecinos
Restricciones: data debe ser tipo list
"""


def get_nearest_neighbors(data):
    results = {}

    if (len(data) > 1):
        for neighbors in data:
            y = neighbors[-1]
            if y not in results:
                y_appearances = 0
                for neighbors_appearance in data:
                    if neighbors_appearance[-1] == y:
                        y_appearances += 1
                results.setdefault(y, y_appearances)
        return get_nearest_neighbors_aux(results)
    elif (len(data) > 0):
        return data[-1]

# ----------------------------------------------------------------------------


"""
Entradas: results corresponde a un diccionario que se genera en la funcion
         "get_nearest_neighbors"
Salidas: Retorna el valor(float) del partido con mas apariciones
Descripcion: Funcion que dado un diccionario en la forma
            {"valor partido":cantidad de apariciones} devuelve el partido
            con mas apariciones
Restricciones: results debe ser un diccionario
"""


def get_nearest_neighbors_aux(results):
    elements = results.items()
    cant_appearances = 0
    result = 0

    for y, value in elements:
        if value > cant_appearances:
            cant_appearances = value
            result = y

    return result

# ----------------------------------------------------------------------------


"""
Entradas: n cantidad de datos a simular, k cantidad de vecinos a considerar,
        percentage es el porcentaje de datos de prueba
Salidas: Imprima los resultados de las prediciones
Descripcion: Funcion controladora se encarga llamar a la funcion de
        "generar_muestra_pais", funciones de normalizacion de datos,
        la funcion "kd_tree_aux" y la funcion "create_csv"
Restricciones: n y k deben ser enteros y percentage un valor entre 0-100
"""


def kd_tree(n, k, percentage):
    myData = [['poblacion_canton', 'superficie_canton', 'densidad_poblacion',
               'urbano', 'sexo', 'dependencia_demografica', 'ocupa_vivienda',
               'promedio_ocupantes', 'vivienda_buen_estado',
               'vivienda_hacinada', 'alfabetismo', 'escolaridad_promedio',
               'educacion_regular', 'fuera_fuerza_trabajo',
               'participacion_fuerza_trabajo', 'asegurado', 'extranjero',
               'discapacidad', 'no_asegurado', 'porcentaje_jefatura_femenina',
               'porcentaje_jefatura_compartida', 'edad', 'voto_primera_ronda',
               'voto_segunda_ronda', 'es_entrenamiento', 'prediccion_r1',
               'prediccion_r2', 'prediccion_r2_con_r1']]

    if(percentage <= 100 and percentage > 0):
        muestra = generar_muestra_pais(n)

        data_r1 = datos_r1_normalizados(muestra)
        data_r2 = datos_r2_normalizados(muestra)
        data_r2_r1 = datos_r2_con_r1_normalizados(muestra)

        data_r1 = np.array(data_r1).tolist()
        data_r2 = np.array(data_r2).tolist()
        data_r2_r1 = np.array(data_r2_r1).tolist()

        percentage = n * (percentage / 100)
        percentage = int(round(percentage, 0))

        print("\nPrediccin_r1")
        myData = kd_tree_aux(data_r1, k, percentage, myData, 0)
        print("\nPrediccin_r2")
        myData = kd_tree_aux(data_r2, k, percentage, myData, 1)
        print("\nPrediccin_r1_r2")
        myData = kd_tree_aux(data_r2_r1, k, percentage, myData, 2)

        create_csv(myData)
        print("\nVer archivo 'resultados_kd_tree' para mas información\n")

        return
    else:
        print("El valor del porcentaje es incorrecto utilizar un valor " +
              "entre 1 - 100")


# ----------------------------------------------------------------------------
"""
Entradas: data son los datos ya normalizados, k cantidad de vecinos a
          considerar,myData es un arreglo con estructura para escribir en
          csv, type_data es el tipo de dato 0 = datos_r1_normalizados,
          1 = datos_r2_normalizados, 2=datos_r2_con_r1_normalizados
Salidas: Imprima los resultados de las preddciones y retorna el arreglo
         myData actualizado
Descripcion: Se encarga de llamar a la funcion de "create_kd_tree" y
            "kd_tree_find_neighbors", ademas es la encargada de obtener
            los valores de error y tambien actualiza myData con lo valores
            obtenidos
Restricciones: type_data y k deben ser enteros y percentage un valor entre
              0-100 myData una matriz, data debe ser una matriz
"""


def kd_tree_aux(data, k, percentage, myData, type_data):
    correct_test = 0
    incorrect_test = 0
    correct_train = 0
    incorrect_train = 0

    data_training = data[percentage:]
    data_testing = data[:percentage]

    tree = create_kd_tree(data_training, k)
    i = 1

    for data_train in data_training:
        y = kd_tree_find_neighbors(tree, data_train)
        data_train.append(y)

        if(data_train[-1] == data_train[-2]):
            correct_train += 1
        else:
            incorrect_train += 1

        if(type_data == 0):
            item = []
            item.extend([data_train[:-1], True, y])
            myData.append(item)
        elif (type_data == 1):
            myData[i][0].append(data_train[-1])
            myData[i].append(y)
        else:
            myData[i].append(y)
        i += 1

    for data_test in data_testing:
        y = kd_tree_find_neighbors(tree, data_test)
        data_test.append(y)

        if(data_test[-1] == data_test[-2]):
            correct_test += 1
        else:
            incorrect_test += 1

        if(type_data == 0):
            item = []
            item.extend([data_test[:-1], False, y])
            myData.append(item)
        elif (type_data == 1):
            myData[i][0].append(data_test[-1])
            myData[i].append(y)
        else:
            myData[i].append(y)
        i += 1

    print("\nEl error de training es de {}".format(
        incorrect_train / len(data_training)))
    print("El error de testing es de {}".format(
        incorrect_test / len(data_testing)))
    print("La precision de training es de {}%".format((
        correct_train / len(data_training)) * 100))
    print("La precision de testing es de {}%".format((
        correct_test / len(data_testing)) * 100))
    return myData

# ----------------------------------------------------------------------------


"""
Entradas: myData representa estrucutra del CSV
Salidas: None
Descripcion: Crea el archivo csv con los resultados
Restricciones: myData debe un arreglo
"""


def create_csv(myData):
    if(not isinstance(myData, list)):
        raise TypeError('El argumento debe ser una lista de listas')
    for i in range(len(myData)):
        if(not isinstance(myData[i], list)):
            raise TypeError('El parametro debe ser una lista de listas')
        if(i != 0):
            if(not isinstance(myData[i][0], list)):
                raise TypeError('El primer elemento de cada elemento'
                                'de la lista debe ser una lista')
<<<<<<< HEAD
            if(len(myData[i][0]) < 5):
                raise AttributeError(
                    'El primer elemento de cada elemento de la lista' +
                    'debe ser una lista de un tamaño mayor a 4')
=======
            if(len(myData[i][0]) <5):
                raise AttributeError('El primer elemento de cada elemento de la lista'+
                                'debe ser una lista de un tamaño mayor a 4')

>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838

    file = open('resultados_kd_tree.csv', 'w', newline='')
    salida = csv.writer(file)
    salida.writerow(myData[0])
    for item in myData[1:]:
        item_aux = item[0]
        item_aux.extend(item[-4:])
        salida.writerow(item_aux)
    del salida
    file.close()

# ----------------------------------------------------------------------------


"""
Entradas: point1 y point2 son arreglos representa elementos del set de datos
Salidas: Float que represnta la distancia
Descripcion: Se encarga de determinar la distancia entre dos puntos
Restricciones: point1 y point2 debe ser arreglos de tamaño>1
"""


def distance(point1, point2):
    if(not isinstance(point1, list) or not isinstance(point2, list)):
        raise TypeError('Los puntos tiene que ser listas')

    result = 0
    for i in range(len(point1) - 1):
        dx = point1[i] - point2[i]
        result += dx * dx
    return math.sqrt(result)



# ----------------------------------------------------------------------------
"""
Entradas: all_points arreglo con un conjuntos de diferentes puntos, new_point
         arreglo que representa solo un punto
Salidas: best_point arreglo de un solo punto
Descripcion: Devuelve le punto mas cercanos entre all_points y new_point
Restricciones: all_points debe estar en forma de matrix y new_point ser un
               arreglo
"""


def closest_point(all_points, new_point):
    if(not isinstance(all_points, list) or not isinstance(new_point, list)):
        raise TypeError('El primer argumento debe ser una lista de listas' +
                        'y el segundo una lista')
    if(not isinstance(all_points[0], list)):
        raise TypeError('El primer argumento debe ser una lista de listas' +
                        'y el segundo una lista')

    best_point = None
    best_distance = None

    for current_point in all_points:
        current_distance = distance(new_point, current_point)
        if best_distance is None or current_distance < best_distance:
            best_point = current_point
            best_distance = current_distance

    return best_point
