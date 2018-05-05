import math
from arbol import Nodo, Hoja, Atributo
from g05 import datos_r1_normalizados, datos_r2_normalizados, datos_r2_con_r1_normalizados
from pc1 import generar_muestra_pais, generar_muestra_provincia, cambiar_semilla
import numpy as np
import pandas as pd


# guarda los atributos utilizados, de manera que no se repitan al armar el
# árbol de decisión
atributos_utilizados = []

# son los encabezados del conjunto de entrenamiento que se utilizará
encabezados = []

# es una variación para armar el árbol de decisión, en la cual los atributos con más de ocho valores se tomarán
# en cuenta de diferente medida para armar los caminos del árbol
columnas_mayor_ocho = []


# esta función devuelve una lista, que consiste en los valores para la
# columna que se le pase como parámetro
def obtener_conjunto_columna(filas, columna):
    valores_columna = []
    numero_filas = len(filas)
    for i in range(numero_filas):
        valor_tomar = filas[i][columna]
        valores_columna.append(valor_tomar)
    return valores_columna


# esta función recibe como parámetro el conjunto de entranamiento y una columna, de manera que se obtenga un conjunto con
# los valores únicos para esa columna
def valores_unicos_por_columna(entrenamiento, columna):
    valores_columna = obtener_conjunto_columna(entrenamiento, columna)
    conjunto_valores_columna = set(valores_columna)
    return conjunto_valores_columna


# función que dada una lista con valores, retorna el índice en el que se
# encuentra el valor como segundo parámetro
def retornar_indice_valores(valores, valor):
    return valores.index(valor)

# función que recibe como parámetro el conjunto de entrenamiento, retorna
# la cantidad que hay de cada valor (última columna)


def contar_valores_conjunto_entrenamiento(conjunto_entrenamiento):
    valores = []
    cantidad_por_valor = []

    for i in range(len(conjunto_entrenamiento)):
        # tomando el último valor del encabezado
        valor = conjunto_entrenamiento[i][-1]
        if valor in valores:
            indice_valores = retornar_indice_valores(valores, valor)
            cantidad_por_valor[indice_valores] += 1
        else:
            valores.append(valor)
            cantidad_por_valor.append(1)
    return valores, cantidad_por_valor


# función que recibe como parámetro un valor, retornará si dicho valor es
# numérico o no
def es_numerico(valor):
    # isinstance es una función que puede evaluar el tipo de dato de una
    # variable
    return isinstance(valor, int) or isinstance(valor, float)

# función encargada de obtener el tamaño de las columnas de los datos de
# entrenamiento


def obtener_tamano_columna_datos_entrenamiento(datos_entrenamiento):
    numero_columnas_retorno = len(datos_entrenamiento[0])
    for fila in datos_entrenamiento:
        if len(fila) != numero_columnas_retorno:
            return "error en el formato de los datos de entrenamiento, todas las filas deben tener la misma cantidad de columnas"
        else:
            numero_columnas_retorno = len(fila)
    return numero_columnas_retorno

# función encargada de obtener el tamaño de las filas de los datos de
# entrenamiento


def obtener_tamano_filas_datos_entrenamiento(datos_entrenamiento):
    return len(datos_entrenamiento)

# función que dado el valor de una columna, retorna todas las filas que
# contengan ese valor


def obtener_filas_por_valor_columna(
        datos_entrenamiento,
        valor_columna,
        columna):
    valor_retorno = []
    for fila in datos_entrenamiento:
        if valor_columna == fila[columna]:
            valor_retorno.append(fila)
    return valor_retorno

# función que, dado un conjunto, obtendrá las filas por categorías, dados
# los valores del conjunto


def obtener_filas_para_conjunto(datos_entrenamiento, conjunto, columna):
    filas = []
    for elemento in conjunto:
        lista = obtener_filas_por_valor_columna(
            datos_entrenamiento, elemento, columna)
        filas.append(lista)
    return filas


# función que determina si toda una columna es numérica o no
def es_columna_numerica(datos_entrenamiento, columna):
    for fila in datos_entrenamiento:
        if not es_numerico(fila[columna]):
            return False
    return True


# función encargada de obtener el valor de entropía, mediante la fórmula
def obtener_entropia_conjunto_entrenamiento_formula(probabilidades):
    resultado_entropia = 0
    for probabilidad in probabilidades:
        resultado_entropia -= probabilidad * math.log2(probabilidad)
    return resultado_entropia


# función encargada de obtener la entropía del conjunto de entrenamiento,
# tomando en cuenta los valores de la última columa
def obtener_entropia_conjunto_entrenamiento(entrenamiento):

    # obtiene la cantidad de votos para cada partido
    valores_etiquetas, votos_etiqueta = contar_valores_conjunto_entrenamiento(
        entrenamiento)
    # obtiene la cantidad de filas que tiene el conjunto de entrenamiento
    cantidad_filas = obtener_tamano_filas_datos_entrenamiento(entrenamiento)

    # se obtienen las probabilidades de voto para cada partido
    probabilidades_etiquetas = []
    tamano_votos_etiqueta = len(votos_etiqueta)
    for i in range(tamano_votos_etiqueta):
        probabilidad = votos_etiqueta[i] / cantidad_filas
        probabilidades_etiquetas.append(probabilidad)

    entropia = obtener_entropia_conjunto_entrenamiento_formula(
        probabilidades_etiquetas)
    return entropia


# función que obtiene las probabilidades de que suceda un voto para un partido en específico
# esto se hace dividiendo la cantidad de votos para un partido entre la
# cantidad total de votos dados
def obtener_probabilidades_fila(fila, largo_fila):
    resultado = []
    valores_etiquetas, votos_etiqueta = contar_valores_conjunto_entrenamiento(
        fila)
    for i in votos_etiqueta:
        resultado.append(i / largo_fila)
    return resultado

# función que obtiene el resultado de aplicar la operación que consiste en aplicar los logaritmos a las probabilidades
# tomadas de la función anterior


def resultado_logaritmo_probabilidad(probabilidades):
    resultado = 0
    for i in probabilidades:
        resultado -= i * math.log2(i)
    return resultado

# función encargada de obtener la ganancia para una columna, para esto, hace uso de las probabilidades y las operaciones
# con logaritmos


def obtener_ganancia_columna(filas_conjunto, datos_entrenamiento, entropia):
    # se obtiene el número total de filas del conjunto de entrenamiento
    numero_filas = obtener_tamano_filas_datos_entrenamiento(
        datos_entrenamiento)
    resultado = 0
    for i in filas_conjunto:
        numero_filas_fila = len(i)
        probabilidad_fila = numero_filas_fila / numero_filas

        probabilidades = obtener_probabilidades_fila(i, numero_filas_fila)
        resultado_logaritmo = resultado_logaritmo_probabilidad(probabilidades)

        resultado += probabilidad_fila * resultado_logaritmo

    ganancia = entropia - resultado
    return ganancia


# función encargada de recorrer las columnas de los datos de entrenamiento, de manera que se puedan obtener
# las ganancias por columna
def recorrer_columnas_datos_entrenamiento(datos_entrenamiento):
    # primero, se obtiene la entropía
    entropia = obtener_entropia_conjunto_entrenamiento(datos_entrenamiento)
    # luego, se obtiene el número de columnas del conjunto de entrenamiento
    # para recorrerlas
    numero_columnas = obtener_tamano_columna_datos_entrenamiento(
        datos_entrenamiento)
    # recorriendo las columnas del conjunto de entramiento

    ganancia_por_columna = []
    for i in range(numero_columnas - 1):
        conjunto_fila_valores_diferentes = {}
        # se obtienen los valores diferentes que se pueden categorizar para la
        # columna actual
        conjunto_fila_valores_diferentes = valores_unicos_por_columna(
            datos_entrenamiento, i)
        # se obtienen todas las filas que se relacionan con los valores
        # categóricos obtenidos anteriormente
        filas_conjunto = obtener_filas_para_conjunto(
            datos_entrenamiento, conjunto_fila_valores_diferentes, i)
        # se obtiene la ganancia para la columna actual
        ganancia = obtener_ganancia_columna(
            filas_conjunto, datos_entrenamiento, entropia)
        ganancia_por_columna.append(ganancia)
    return ganancia_por_columna


# función encargada de obtener el índice de la columna que genera más ganancia
def obtener_indice_maximo(ganancias):
    indice = 0
    maximo = ganancias[0]
    tamano_ganancias = len(ganancias)
    # se recorren las ganancias para obtener la máxima
    for i in range(1, tamano_ganancias):
        if ganancias[i] > maximo:
            maximo = ganancias[i]
            indice = i
    return indice

# función encargada de definir si un nodo es o no una hoja, de acuerdo a
# los target que obtiene


def es_nodo_hoja(valores, cantidad_por_valor):
    if len(valores) == 1 and len(cantidad_por_valor) == 1:
        return True
    else:
        return False

# función que indica si una lista de ganancias no aporta
# para esto, evalúa si todos los valores de la lista son igual a cero


def es_ganancia_cero(ganancias):
    for i in ganancias:
        if i != 0.0:
            return False
    return True

# función encargada de retornar el valor de un target
# esta función se utiliza cuando todos los target de un conjunto de datos son iguales, por lo que se toma el primer valor
# como referencia


def retornar_target(filas):
    fila_actual = filas[0][-1]
    return fila_actual


# función encargada de obtener el partido con más votos
def obtener_max_lista(valores, cantidad_por_valor):
    tamano = len(valores)
    maximo = cantidad_por_valor[0]
    indice_devolver = 0
    # se recorren las cantidades por valor (partido) de manera que se pueda
    # obtener el máximo
    for i in range(1, tamano):
        if cantidad_por_valor[i] > maximo:
            maximo = cantidad_por_valor[i]
            indice_devolver = i
    return valores[indice_devolver]

# función encargada de obtener la pluralidad del conjunto de datos de entrada
# es decir, la mayoría de votos


def obtener_pluralidad(filas):
    valores = []
    cantidad_por_valor = []

    for i in range(len(filas)):
        # tomando el último valor del encabezado
        valor = filas[i][-1]
        # se llenan las listas de valores y cantidad_por_valor con datos
        # correspondientes al partido y la cantidad de votos
        if valor in valores:
            indice_valores = retornar_indice_valores(valores, valor)
            cantidad_por_valor[indice_valores] += 1
        else:
            valores.append(valor)
            cantidad_por_valor.append(1)
    return obtener_max_lista(valores, cantidad_por_valor)


# función encargada de determinar si todos los target de un conjunto de datos son iguales o no
# gracias a esto, se puede cumplir una de las condiciones del árbol de decisión, la cual indica que
# se retorna el target, en caso de que todos sean iguales
def son_todos_target_iguales(filas):
    largo = len(filas)
    target = filas[0][-1]
    for i in range(1, largo):
        if filas[i][-1] != target:
            return False
    return True

# función encargada de obtener una lista con los nombres de los atributos
# utilizados a la hora de armar el árbol de decisión


def obtener_lista_atributos_utilizados():
    lista_retorno = []
    for i in atributos_utilizados:
        lista_retorno.append(i.nombre)
    return lista_retorno

# función encargada de devolver las ganancias que aún no se han utilizado
# para armar el árbol de decisión


def reducir_ganancias_por_atributos_utilizados(ganancias):
    respuesta_ganancias = []
    respuesta_encabezados = []
    atributos = obtener_lista_atributos_utilizados()
    tamano = len(ganancias)
    for i in range(tamano):
        # se pregunta si los encabezados asociados a las ganancias se
        # encuentran utilizados o no
        if encabezados[i] not in atributos:
            respuesta_ganancias.append(ganancias[i])
            respuesta_encabezados.append(encabezados[i])
    return respuesta_ganancias, respuesta_encabezados


# función que obtiene el índice de un encabezado, dado su nombre
def obtener_indice_encabezado(nombre):
    return encabezados.index(nombre)

# función que ayuda a hacer una partición de caminos, en los cuales se
# tomen dos, los valores mayores y valores menores que cero


def obtener_filas_mayores_menores_cero(conjunto, columna):
    mayores = []
    menores = []
    for i in conjunto:
        # partición de caminos que cumplen con valores mayores o menores que
        # cero
        if i[columna] > 0:
            mayores.append(i)
        elif i[columna] < 0:
            menores.append(i)
    return mayores, menores


# función encargada de armar el árbol de decisión
# toma como parámetro el conjunto de entrenamiento actual y el conjunto de
# entrenamiento del padre
def armar_arbol(conjunto_entrenamiento, filas_padre):
    tipo_nodo = 0
    # caso 1, se pregunta si quedan ejemplos disponibles para este camino
    if conjunto_entrenamiento == []:
        target = obtener_pluralidad(filas_padre)
        hoja = Hoja(target)
        return hoja
    else:
        # caso 2, todos los target son iguales para el conjunto de
        # entrenamiento
        if(son_todos_target_iguales(conjunto_entrenamiento)):
            target = retornar_target(conjunto_entrenamiento)
            hoja = Hoja(target)
            return hoja

        else:

            # hacer split
            # 1.obtener las ganancias para cada columna
            ganancias_por_columna = recorrer_columnas_datos_entrenamiento(
                conjunto_entrenamiento)
            ganancias_permitidas, encabezados_permitidos = reducir_ganancias_por_atributos_utilizados(
                ganancias_por_columna)
            # 2.ver si quedan atributos disponibles para hacer split
            if ganancias_permitidas == []:
                #print("ya no hay atributos, pluralidad ejemplos")
                target = obtener_pluralidad(conjunto_entrenamiento)
                hoja = Hoja(target)
                return hoja
                # crear una hoja aquí
            elif es_ganancia_cero(ganancias_permitidas):
                target = obtener_pluralidad(conjunto_entrenamiento)
                hoja = Hoja(target)
                return hoja

            else:
                hijos = []
                indice_maximo = obtener_indice_maximo(ganancias_permitidas)

                encabezado_nodo = encabezados_permitidos[indice_maximo]
                ganancia_nodo = ganancias_permitidas[indice_maximo]

                atributo = Atributo(ganancia_nodo, encabezado_nodo)

                indice_nodo = obtener_indice_encabezado(encabezado_nodo)

                atributos_utilizados.append(atributo)
                conjunto_fila_valores_diferentes = valores_unicos_por_columna(
                    conjunto_entrenamiento, indice_nodo)

                # si se aporta gran cantidad de valores para un atributo, se
                # evaluará si es mayor o menor a 0
                if indice_nodo in columnas_mayor_ocho:
                    mayores, menores = obtener_filas_mayores_menores_cero(
                        conjunto_entrenamiento, indice_nodo)
                    nodo_mayores = armar_arbol(mayores, conjunto_entrenamiento)
                    nodo_menores = armar_arbol(menores, conjunto_entrenamiento)
                    hijos.append(nodo_mayores)
                    hijos.append(nodo_menores)

                else:
                    tipo_nodo = 1
                    for i in conjunto_fila_valores_diferentes:
                        # para cada valor, se obtienen las filas que cumplen
                        # con esta característica en la columna especificada
                        filas_elemento = obtener_filas_por_valor_columna(
                            conjunto_entrenamiento, i, indice_nodo)
                        # se llama de nuevo a la función, con los elementos del
                        # nuevo camino y los elementos del padre
                        nodo = armar_arbol(
                            filas_elemento, conjunto_entrenamiento)
                        hijos.append(nodo)
                nodo = Nodo(
                    hijos,
                    indice_nodo,
                    conjunto_fila_valores_diferentes,
                    ganancias_permitidas[indice_maximo],
                    tipo_nodo,
                    conjunto_entrenamiento)
                return nodo

# función encargada de recorrer las columnas del conjunto de entrenamiento, para asignar un valor a los encabezados
# de estos


def generar_header_conjunto_entrenamiento(conjunto_entrenamiento):
    tamano = len(conjunto_entrenamiento[0])
    for i in range(tamano - 1):
        # se asigna como valor un atributo basado en un contador
        encabezado = "Atributo: " + str(i)
        encabezados.append(encabezado)
    return encabezados

# función encargada de recorrer el árbol de decisión


def recorrer_arbol(arbol):
    if(isinstance(arbol, Nodo)):
        for i in arbol.hijos:
            recorrer_arbol(i)
    elif(isinstance(arbol, Hoja)):
        print(arbol.target)

# función encargada de obtener una lista de los valores de una columna en
# específico del conjunto de datos


def imprimir_columna(datos, columna):
    lista = []
    for i in datos:
        lista.append(i[columna])
    return lista

# función encargada de obtener la cantidad de datos que se van a utilizar
# para una prueba


def obtener_valor_porcentaje_pruebas(n, porcentaje):
    return int(round(n * (porcentaje / 100)))

# función encargada de tomar las muestras generadas y dividirlas en datos
# de entrenamiento y datos de pruebas


def partir_datos_entrenamiento_prueba(
        datos,
        cantidad_entrenamiento,
        cantidad_prueba):
    datos_entrenamiento = []
    datos_prueba = []
    # se toman los datos de entrenamiento
    for i in range(cantidad_entrenamiento):
        datos_entrenamiento.append(datos[i])
    # se toman los datos de pruebas
    for i in range(
            cantidad_entrenamiento,
            cantidad_entrenamiento +
            cantidad_prueba):
        datos_prueba.append(datos[i])
    return datos_entrenamiento, datos_prueba

# función encargada de llamar a las funciones para partir los datos de entrenamiento y generar el árbol, dado un
# porcentaje de pruebas y los datos de entrenamiento


def generar_arbol(n, porcentaje_pruebas, data):

    # se obtienen las cantidades de los datos de entrenamiento y los datos de
    # prueba
    cantidad_datos_prueba = obtener_valor_porcentaje_pruebas(
        n, porcentaje_pruebas)
    cantidad_datos_entrenamiento = n - cantidad_datos_prueba
    print(cantidad_datos_entrenamiento)
    print(cantidad_datos_prueba)
    data = np.array(data).tolist()

    # se obtienen los datos de entrenamiento y los datos de prueba
    datos_entrenamiento, datos_prueba = partir_datos_entrenamiento_prueba(
        data, cantidad_datos_entrenamiento, cantidad_datos_prueba)
    c_entrenamiento = datos_entrenamiento
    c_pruebas = datos_prueba

    # se agregan los índices de los a tributos que aportan más de 8 opciones
    tamano = len(data[0])

    for i in range(tamano - 1):
        datos = imprimir_columna(data, i)
        datos_conjunto = set(datos)
        if len(datos_conjunto) >= 8:
            columnas_mayor_ocho.append(i)

    generar_header_conjunto_entrenamiento(c_entrenamiento)
    arbol = armar_arbol(c_entrenamiento, c_entrenamiento)
    return arbol, c_pruebas, c_entrenamiento

# función encargada de retornar el índice, dado el valor de un conjunto


def obtener_indice_conjunto(conjunto, valor):
    retorno = 0
    for i in conjunto:
        if i == valor:
            return retorno
        else:
            retorno += 1

# función encargada de hacer la predicción, dado un árbol de decisión


def predecir(c_pruebas, arbol):
    predicciones = []
    valores_reales = []
    for i in c_pruebas:
        prediccion = predecir_aux(i, arbol)
        valores_reales.append(i[-1])
        predicciones.append(prediccion)
    return predicciones, valores_reales

# función auxiliar, encargada de recorrer el árbol de decisión para
# realizar una predicción


def predecir_aux(fila, arbol):
    # caso 1, si la instancia de un nodo
    if isinstance(arbol, Nodo):
        columna = arbol.columna
        valor = fila[columna]
        conjunto = arbol.valores_columna
        # si es un nodo tipo 0, entonces se hacer la partición por medio de
        # rangos
        if arbol.tipo == 0:
            if valor > 0:
                return predecir_aux(fila, arbol.hijos[0])
            elif valor < 0:
                return predecir_aux(fila, arbol.hijos[1])
        # en caso contrario, se hace por medio de coincidencia con el valor del
        # conjunto
        elif arbol.tipo == 1:
            indice = obtener_indice_conjunto(conjunto, valor)
            return predecir_aux(fila, arbol.hijos[indice])
    # caso 2, si es una hoja, se retorna la predicción
    elif isinstance(arbol, Hoja):
        return arbol.target

# función encargada de obtener la precisión, dados los verdaderos
# positivos y los falsos positivos


def obtener_precision(verdaderos_positivos, falsos_positivos):
    return (verdaderos_positivos / (verdaderos_positivos + falsos_positivos))

# función encargada de partir los verdaderos y los falsos positivos, dadas las predicciones y los valores reales que
# se querían predecir


def obtener_verdaderos_falsos_positivos(predicciones, reales):
    tamano = len(predicciones)
    verdaderos_positivos = 0
    falsos_positivos = 0
    for i in range(tamano):
        if predicciones[i] == reales[i]:
            verdaderos_positivos += 1
        else:
            falsos_positivos += 1
    return verdaderos_positivos, falsos_positivos

# función encargada de determinar si un nodo posee solo hojas como hijos,
# esto se utiliza para saber cuándo podar el árbol


def es_nodo_con_hojas(arbol):
    for i in arbol.hijos:
        # verifica que las instancias de los hijos sean hojas
        if not isinstance(i, Hoja):
            return False
    return True

# función encargada de obtener los nodos con solo hojas, de manera que luego se pueda visualizar sus ganancias y saber
# dónde hacer la poda


def obtener_nodos_con_solo_hojas(arbol):
    lista = []
    # debe tener instancia de nodo
    if isinstance(arbol, Nodo):
        # si el nodo solo posee hojas, se retorna
        if es_nodo_con_hojas(arbol):
            lista.append(arbol)
            return lista
        # en caso contrario, se suma a la lista lo que se retorne de la llamada
        # a la función por cada hijo
        else:
            for i in arbol.hijos:
                lista += (obtener_nodos_con_solo_hojas(i))
            return lista
    # en caso contrario, se retorna la lista vacía
    elif isinstance(arbol, Hoja):
        return lista

# función encargada de podar el árbol, dado un umbral


def podar_arbol(arbol, umbral):
    # debe ser instancia de un nodo
    if isinstance(arbol, Nodo):
        # además, debe se un nodo con hojas como hijos
        if es_nodo_con_hojas(arbol):
            # seguidamente, la ganancia debe ser menor que el umbral
            if arbol.ganancia < umbral:
                # se retorna una hoja con la pluralidad del conjunto de datos
                # del nodo
                target = obtener_pluralidad(arbol.filas)
                hoja = Hoja(target)
                return hoja
            else:
                return arbol
        # si no es un nodo con las hojas como hijos
        else:
            tamano = len(arbol.hijos)
            hijos = []
            # se evalúa si los hijos se pueden podar o no
            for i in range(tamano):
                hijo = podar_arbol(arbol.hijos[i], umbral)
                hijos.append(hijo)
            arbol.hijos = hijos
            return arbol
    # si es instancia de una hoja, solamente se retorna
    elif isinstance(arbol, Hoja):
        return arbol

# función encargada de evaluar si los nodos con hojas como hijos del arbol
# actual, son menores que el umbral mínimo


def hay_ganancia_menor_umbral(nodos, umbral):
    for i in nodos:
        if i.ganancia < umbral:
            return True
    return False

# función encargada de servir como delimitante de cuántas veces se debe hacer poda a un arbol
# en este caso, hasta que todas las ganancias sean mayores que le umbral


def podar_arbol_aux_aux(arbol, umbral):
    # se obtiene los nodos que tienen únicamente hojas como hijos
    ganancias_nodos_solo_hojas = obtener_nodos_con_solo_hojas(arbol)
    # mientras los nodos obtenidos tengan una ganancia menor al umbral, se poda el árbol y se vuelven a obtener los
    # nodos con hojas como hijos
    while hay_ganancia_menor_umbral(ganancias_nodos_solo_hojas, umbral):
        recorrer_arbol(arbol)
        arbol = podar_arbol(arbol, umbral)
        ganancias_nodos_solo_hojas = obtener_nodos_con_solo_hojas(arbol)
    return arbol

# función encargada de imprimir las hojas de un árbol


def imprimir_hojas(arbol):
    if isinstance(arbol, Hoja):
        print(arbol.target)
    else:
        for i in arbol.hijos:
            imprimir_hojas(i)


# función encargada de limpiar las variables globales que se utilizan para
# armar el árbol de decisión
def limpiar_variables_globales():
    global encabezados
    global columnas_mayor_ocho
    global atributos_utilizados

    encabezados = []
    columnas_mayor_ocho = []
    atributos_utilizados = []


# función principal, en esta función se recibe el número de la muestra y el porcentaje para el conjunto de pruebas
# además, se generan las muestras y árboles para las rondas 1,2 y ronda 2 + ronda 1
# se realizan las predicciones, cálculo de precisión y errores de prueba y entrenamiento
# finalmente, se realizan podas en el árbol


def funcion_principal_arbol(
        numero_muestra,
        porcentaje_pruebas,
        umbral_poda,
        prefijo):

    # generación de la muestra y adaptación para los datos de primera ronda,
    # segunda ronda y primera + segunda ronda
    muestra = generar_muestra_pais(numero_muestra)
    data_r1 = datos_r1_normalizados(muestra)
    data_r2 = datos_r2_normalizados(muestra)
    data_r2_r1 = datos_r2_con_r1_normalizados(muestra)

    # se hace el cálculo de los árboles
    arbol_r1, c_pruebas_r1, c_entrenamiento_r1 = generar_arbol(
        numero_muestra, porcentaje_pruebas, data_r1)
    limpiar_variables_globales()
    arbol_r2, c_pruebas_r2, c_entrenamiento_r2 = generar_arbol(
        numero_muestra, porcentaje_pruebas, data_r2)
    limpiar_variables_globales()
    arbol_r2_r1, c_pruebas_r2_r1, c_entrenamiento_r2_r1 = generar_arbol(
        numero_muestra, porcentaje_pruebas, data_r2_r1)
    limpiar_variables_globales()
    # predicciones para los datos de la primera ronda, con conjunto de pruebas
    predicciones_r1_prueba, valores_reales_r1_prueba = predecir(
        c_pruebas_r1, arbol_r1)
    verdaderos_positivos_r1_prueba, falsos_positivos_r1_prueba = obtener_verdaderos_falsos_positivos(
        predicciones_r1_prueba, valores_reales_r1_prueba)
    print("Verdaderos y falsos positivos para la primera ronda, pruebas")
    print("------------------------------------------------------")
    print("Verdaderos positivos:")
    print(verdaderos_positivos_r1_prueba)
    print("Falsos positivos:")
    print(falsos_positivos_r1_prueba)
    precision_r1_prueba = obtener_precision(
        verdaderos_positivos_r1_prueba,
        falsos_positivos_r1_prueba)
    print("Precisión:")
    print(precision_r1_prueba)
    print("Error de pruebas:")
    print(falsos_positivos_r1_prueba)
    print("------------------------------------------------------")

    # predicciones para los datos de la primera ronda, con conjunto de
    # entrenamiento
    predicciones_r1_entrenamiento, valores_reales_r1_entrenamiento = predecir(
        c_entrenamiento_r1, arbol_r1)
    verdaderos_positivos_r1_entrenamiento, falsos_positivos_r1_entrenamiento = obtener_verdaderos_falsos_positivos(
        predicciones_r1_entrenamiento, valores_reales_r1_entrenamiento)
    print("Verdaderos y falsos positivos para la primera ronda, entrenamiento")
    print("------------------------------------------------------")
    print("Verdaderos positivos:")
    print(verdaderos_positivos_r1_entrenamiento)
    print("Falsos positivos:")
    print(falsos_positivos_r1_entrenamiento)
    precision_r1_entrenamiento = obtener_precision(
        verdaderos_positivos_r1_entrenamiento,
        falsos_positivos_r1_entrenamiento)
    print("Precisión:")
    print(precision_r1_entrenamiento)
    print("Error de entrenamiento:")
    print(falsos_positivos_r1_entrenamiento)
    print("------------------------------------------------------")

    # predicciones para los datos de la segunda ronda, con conjunto de pruebas
    predicciones_r2_prueba, valores_reales_r2_prueba = predecir(
        c_pruebas_r2, arbol_r2)
    verdaderos_positivos_r2_prueba, falsos_positivos_r2_prueba = obtener_verdaderos_falsos_positivos(
        predicciones_r2_prueba, valores_reales_r2_prueba)
    print("Verdaderos y falsos positivos para la segunda ronda, pruebas")
    print("------------------------------------------------------")
    print("Verdaderos positivos:")
    print(verdaderos_positivos_r2_prueba)
    print("Falsos positivos:")
    print(falsos_positivos_r2_prueba)
    precision_r2_prueba = obtener_precision(
        verdaderos_positivos_r2_prueba,
        falsos_positivos_r2_prueba)
    print("Precisión:")
    print(precision_r2_prueba)
    print("Error de pruebas:")
    print(falsos_positivos_r2_prueba)
    print("------------------------------------------------------")

    # predicciones para los datos de la segunda ronda, con conjunto de
    # entrenamiento
    predicciones_r2_entrenamiento, valores_reales_r2_entrenamiento = predecir(
        c_entrenamiento_r2, arbol_r2)
    verdaderos_positivos_r2_entrenamiento, falsos_positivos_r2_entrenamiento = obtener_verdaderos_falsos_positivos(
        predicciones_r2_entrenamiento, valores_reales_r2_entrenamiento)
    print("Verdaderos y falsos positivos para la segunda ronda, entrenamiento")
    print("------------------------------------------------------")
    print("Verdaderos positivos:")
    print(verdaderos_positivos_r2_entrenamiento)
    print("Falsos positivos:")
    print(falsos_positivos_r2_entrenamiento)
    precision_r2_entrenamiento = obtener_precision(
        verdaderos_positivos_r2_entrenamiento,
        falsos_positivos_r2_entrenamiento)
    print("Precisión:")
    print(precision_r2_entrenamiento)
    print("Error de entrenamiento:")
    print(falsos_positivos_r2_entrenamiento)
    print("------------------------------------------------------")

    # predicciones para los datos de la segunda ronda + primera ronda, con
    # conjunto de pruebas
    predicciones_r2_r1_prueba, valores_reales_r2_r1_prueba = predecir(
        c_pruebas_r2_r1, arbol_r2_r1)
    verdaderos_positivos_r2_r1_prueba, falsos_positivos_r2_r1_prueba = obtener_verdaderos_falsos_positivos(
        predicciones_r2_r1_prueba, valores_reales_r2_r1_prueba)
    print("Verdaderos y falsos positivos para la segunda ronda + primera ronda, pruebas")
    print("------------------------------------------------------")
    print("Verdaderos positivos:")
    print(verdaderos_positivos_r2_r1_prueba)
    print("Falsos positivos:")
    print(falsos_positivos_r2_r1_prueba)
    precision_r2_r1_prueba = obtener_precision(
        verdaderos_positivos_r2_r1_prueba,
        falsos_positivos_r2_r1_prueba)
    print("Precisión:")
    print(precision_r2_r1_prueba)
    print("Error de pruebas:")
    print(falsos_positivos_r2_r1_prueba)
    print("------------------------------------------------------")

    # predicciones para los datos de la segunda ronda + primera ronda, con
    # conjunto de entrenamiento
    predicciones_r2_r1_entrenamiento, valores_reales_r2_r1_entrenamiento = predecir(
        c_entrenamiento_r2_r1, arbol_r2_r1)
    verdaderos_positivos_r2_r1_entrenamiento, falsos_positivos_r2_r1_entrenamiento = obtener_verdaderos_falsos_positivos(
        predicciones_r2_r1_entrenamiento, valores_reales_r2_r1_entrenamiento)
    print("Verdaderos y falsos positivos para la segunda ronda + primera ronda, entrenamiento")
    print("------------------------------------------------------")
    print("Verdaderos positivos:")
    print(verdaderos_positivos_r2_r1_entrenamiento)
    print("Falsos positivos:")
    print(falsos_positivos_r2_r1_entrenamiento)
    precision_r2_r1_entrenamiento = obtener_precision(
        verdaderos_positivos_r2_r1_entrenamiento,
        falsos_positivos_r2_r1_entrenamiento)
    print("Precisión:")
    print(precision_r2_r1_entrenamiento)
    print("Error de entrenamiento:")
    print(falsos_positivos_r2_r1_entrenamiento)
    print("------------------------------------------------------")

    # creación del archivo csv que posee la información relacionada con las
    # muestras y las predicciones
    tamano_recorrer_entrenamiento = len(predicciones_r1_entrenamiento)
    # para los datos de entrenamiento, el parámetro es_entrenamiento es True
    for i in range(tamano_recorrer_entrenamiento):
        muestra[i] += [True,
                       predicciones_r1_entrenamiento[i],
                       predicciones_r2_entrenamiento[i],
                       predicciones_r2_r1_entrenamiento[i]]
    tamano_recorrer_prueba = len(predicciones_r1_prueba)
    # para los datos de prueba, el parámetro es_entrenamiento es False
    for i in range(tamano_recorrer_prueba):
        muestra[i + tamano_recorrer_entrenamiento] += [False,
                                                       predicciones_r1_prueba[i],
                                                       predicciones_r2_prueba[i],
                                                       predicciones_r2_r1_prueba[i]]
    dataframe = pd.DataFrame(
        muestra,
        columns=[
            'poblacion_canton',
            'superficie_canton',
            'densidad_poblacion',
            'urbano',
            'sexo',
            'dependencia_demografica',
            'ocupa_vivienda',
            'promedio_ocupantes',
            'vivienda_buen_estado',
            'vivienda_hacinada',
            'alfabetismo',
            'escolaridad_promedio',
            'educacion_regular',
            'fuera_fuerza_trabajo',
            'participacion_fuerza_trabajo',
            'asegurado',
            'extranjero',
            'discapacidad',
            'no_asegurado',
            'porcentaje_jefatura_femenina',
            'porcentaje_jefatura_compartida',
            'edad',
            'voto_primera_ronda',
            'voto_segunda_ronda',
            'es_entrenamiento',
            'prediccion_r1',
            'prediccion_r2',
            'prediccion_r2_con_r1'])
    nombre = prefijo + "resultados_arbol_decision.csv"
    print(nombre)
    dataframe.to_csv(nombre, index=False)


#funcion_principal_arbol(10000, 25, 0.08, "p1")
