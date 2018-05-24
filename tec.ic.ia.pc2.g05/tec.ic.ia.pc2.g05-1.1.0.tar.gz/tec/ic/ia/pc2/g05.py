import random
import copy
import time
import os
import shutil
import numpy as np
from random import uniform

mejor = []


#Entrada: Archivo con el tablero inicial, rango de vision
#         zanahorias que el conejo va a buscar
#Salida: Imprime cada paso del algoritmo en un archivo txt
#Restricciones: Revisar restriciones de formato del tablero
#               en la documentación, el rango y las zanahorias
#               son números enteros
#Descripción: Dado un escenario del problema del conejo
#             realiza una búsqueda a* para cada una de
#             las zanahorias hasta que no las haya en el
#             tablero o bien haya encontrado la cantidad
#             indicada por parámetro

def a_star_search(archivo, vision, zanahorias):
    tablero = leer_tablero(archivo)
    if(tablero == []):
        return
    i = 1
    while(zanahorias > 0 and zanahorias_restantes(tablero) > 0):
        print_tablero(tablero,"salida_A_Estrella\\" + str(i).zfill(5) + ".txt")
        costos = calculo_costo(tablero, vision, zanahorias)
        movimiento = menor_costo(costos)
        print_paso(i, costos, movimiento, False)
        tablero, zanahorias = mover_conejo(movimiento, tablero, zanahorias)
        i += 1
    print("Paso: ",str(i).zfill(5), "FINAL")
    print_tablero(tablero, "salida_A_Estrella\\" + str(i).zfill(5) + ".txt")

def print_paso(paso, costos, movimiento, final):
    paso = str(paso)
    if(not final):
        print("Paso: ",paso.zfill(5),obtener_costos_string(costos), "Movimiento: ", movimiento[0])
    else:
        print("Paso: ",paso.zfill(5), "FINAL")
        
def obtener_costos_string(costos):
    string = ""
    for costo in costos:
        string += costo[0] +": "+str(costo[1])+" "
    return string

#Entrada: Matriz y string
#Salida: 
#Restricciones: 
#Descripción: Escribe en un txt la matriz "tablero"
    
def zanahorias_restantes(tablero):
    cantidad = 0
    for i in tablero:
        for j in i:
            if(j == 'Z'):
                cantidad += 1
    return cantidad

#Entrada: Matriz y string
#Salida: 
#Restricciones: 
#Descripción: Escribe en un txt la matriz "tablero"
    
def print_tablero(tablero, nombre_archivo):
    try:
        string = ""
        file = open(nombre_archivo,'w+')
        for i in tablero:
            for j in i:
                string += j
        file.write(string)
        file.close()
    except:
        pass

#Entrada: Tablero del problema del conejo(Matriz NxM),
#         Rango de visión del conejo(entero),
#         Cantidad de zanahorias restantes
#Salida: Costos por cada posible movimiento, ejemplo:
#       [["DERECHA",10], ["IZQUIERDA",1000]]
#Restricciones: Revisar restriciones de formato del tablero
#               en la documentación, rango y zanahorias_restantes
#               son enteros
#Descripción: Cálcula el costo de cada movimiento dado por la función
#             de predicción de costo futuro:
#             ********FUNCION DE COSTO************

def calculo_costo(tablero, rango, zanahorias_restantes):
    conejo = posicion_conejo(tablero)
    movimientos = movimientos_conejo(tablero, conejo)
    vision_conejo = rango_vision_conejo(tablero, conejo, rango)
    costos = []
    for casilla_movimiento in movimientos:
        costos_movimientos = []
        for casilla_vision in vision_conejo:
            casilla = tablero[casilla_vision[0]][casilla_vision[1]]
            #Función de costo###
            if(casilla == 'Z'):
                costo = abs(casilla_movimiento[1] - casilla_vision[0]) + abs(casilla_movimiento[2] - casilla_vision[1])
                costo -= (zanahorias_restantes - cantidad_caracter_vecinos_por_casilla('Z', casilla_vision, tablero))
                if(tablero[casilla_movimiento[1]][casilla_movimiento[2]] == 'Z'):
                    costo -= 1
            ####################
                costos_movimientos += [costo]
        costo_minimo = float("inf")
        indice_minimo = 0
        indice = 0
        for i in costos_movimientos:
            if(i < costo_minimo):
                costo_minimo = i
                indice_minimo = indice
            indice += 1
        try:
            costos += [[casilla_movimiento[0], costos_movimientos[indice_minimo]]]
        except:
            costos += [[casilla_movimiento[0], 1000]]           
    return costos

#Entrada: Movimiento a realizar(["Direccion",x, y]),
#         Tablero del problema del conejo(Matriz NxM),
#         Cantidad de zanahorias restantes
#Salida: Matriz con el tablero actual luego del movimiento,
#        Cantidad de zanahorias restantes
#Restricciones: Revisar restriciones de formato del tablero
#               en la documentación
#Descripción: Realiza el movimiento del conejo en el tablero 

def mover_conejo(movimiento, tablero, zanahorias):
    conejo = posicion_conejo(tablero)
    x_conejo = conejo[0]
    y_conejo = conejo[1]
    tablero[x_conejo][y_conejo] = ' '
    if(movimiento[0] == "DERECHA"):
        if(tablero[x_conejo][y_conejo + 1] == 'Z'):
            zanahorias -= 1
        tablero[x_conejo][y_conejo + 1] = 'C'
    elif(movimiento[0] == "IZQUIERDA"):
        if(tablero[x_conejo][y_conejo - 1] == 'Z'):
            zanahorias -= 1
        tablero[x_conejo][y_conejo - 1] = 'C'
    elif(movimiento[0] == "ARRIBA"):
        if(tablero[x_conejo - 1][y_conejo] == 'Z'):
            zanahorias -= 1
        tablero[x_conejo - 1][y_conejo] = 'C'
    elif(movimiento[0] == "ABAJO"):
        if(tablero[x_conejo + 1][y_conejo] == 'Z'):
            zanahorias -= 1
        tablero[x_conejo + 1][y_conejo] = 'C'
    return tablero, zanahorias
        
                
#Entrada: Lista
#Salida: Entero
#Restricciones: La lista tiene el formato
#               [["Direccion",costo], ["Direccion",costo]...]
#Descripción: La dirección con menor costo

def menor_costo(costos):
    menor = float("inf")
    min_costo = []
    lista_min_costos = []
    for costo in costos:
        if(costo[1] == menor):
            lista_min_costos += [costo]
        elif(costo[1] < menor):
            lista_min_costos = []
            menor = costo[1]
            min_costo = costo
    if(lista_min_costos == []):
        return min_costo
    else:
        
        lista_min_costos += [min_costo]
        return direccion_aleatoria(lista_min_costos)

def direccion_aleatoria(lista_min_costo):
    direcciones = len(lista_min_costo)
    probabilidad = 1 / direcciones
    probabilidades = probabilidades_acumuladas(probabilidad, len(lista_min_costo))
    sample_num = uniform(0, 1)
    for i in range(0, len(probabilidades)):
        if (sample_num <= probabilidades[i]):
            return lista_min_costo[i]
    

def probabilidades_acumuladas(probabilidad, cantidad):
    probabilidades = []
    for i in range(0, cantidad):
        probabilidades += [probabilidad * (i + 1)]
    return probabilidades
                
#Entrada: Tablero del problema del conejo(Matriz NxM),
#         Posición [x, y] del conejo
#Salida: Matriz con los posibles movimientos del conejo
#        Cada movimiento es ["Direccion",x, y]
#Restricciones: Revisar restriciones de formato del tablero
#               en la documentación
#Descripción: Retorna una matriz con las direcciones
#             en las que se puede mover el conejo
#             dada su posición actual

def movimientos_conejo(tablero, conejo):
    movimientos = []
    if(conejo[1] - 1 >= 0):
        movimientos += [["IZQUIERDA",conejo[0], conejo[1] - 1]]
    if(conejo[1] + 1 < len(tablero[0]) - 1):
        movimientos += [["DERECHA",conejo[0], conejo[1] + 1]]
    if(conejo[0] - 1 >= 0):
        movimientos += [["ARRIBA",conejo[0] - 1, conejo[1]]]
    if(conejo[0] + 1 < len(tablero)):
        movimientos += [["ABAJO",conejo[0] + 1, conejo[1]]]
    return movimientos
    
            
                
#Entrada: Tablero del problema del conejo(Matriz NxM)
#Salida: Posicion del conejo en el tablero
#Restricciones: Revisar restriciones de formato del tablero
#               en la documentación
#Descripción: Retorna la posición del conejo en el tablero

def posicion_conejo(tablero):
    for i in range(0, len(tablero)):
        for j in range(0, len(tablero[0])):
            if(tablero[i][j] == 'C'):
                return [i, j]
            
#Entradas: Posicion del conejo(Lista = [x, y])
#          Rango de vision(Lista = [x, y]) 
#Salida: Vision del conejo(Matriz [[x1,y1]...[xn, yn]])
#Restricciones:
#Descripción: Retorna una matriz con las casillas visibles
#             por el conejo en el tablero

def rango_vision_conejo(tablero, posicion, rango):
    vision = []
    x_conejo = posicion[0]
    y_conejo = posicion[1]
    for i in range(x_conejo - rango, x_conejo + rango):
        for j in range(y_conejo - rango, y_conejo + rango):
            if(i >= 0 and i < len(tablero) and j >= 0 and j < len(tablero[0]) - 1):
                if(i != x_conejo or j != y_conejo):
                    vision += [[i,j]]

    return vision

#Entrada: Dos listas 
#Salida: Distancia euclideana entre casillas
#Restricciones: Lista = [x, y]
#Descripción: Retorna la distancia entre dos casillas

def distancia_entre_casillas(casilla_1, casilla_2):
    x1 = casilla_1[0]
    y1 = casilla_1[1]
    x2 = casilla_2[0]
    y2= casilla_2[1]
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

#Entradas: Un caracter, lista, matriz
#Salida: Entero
#Restricciones: Lista = [x, y], matriz NxM
#Descripción: Dada una casilla retorna la cantidad de veces
#             que se encuentra el caracter en las casillas vecinas

def cantidad_caracter_vecinos_por_casilla(caracter, casilla, tablero):
    numero_caracteres = 0
    for i in range(casilla[0] - 1, casilla[0]+ 1):
        for j in range(casilla[1] - 1, casilla[1] + 1):
            if(i >= 0 and i < len(tablero) and j >= 0 and j < len(tablero[0])):
                if(tablero[i][j] == caracter):
                    numero_caracteres += 1
    return numero_caracteres

#Entrada: Direccion de un archivo
#Salida: Tablero del problema del conejo(Detalle en la documentación)
#Restricciones: Revisar restriciones de formato en la documentación
#Descripción: Lee un archivo de texto con el formato de tablero
#             y retorna una matriz con la estructura del problema
            
def leer_tablero(archivo):
    try:
        tablero = inicializar_tablero(archivo)
        archivo = open(archivo,'r')
        if(tablero == []):
            return []
        i = 0
        j = 0
        for line in archivo:
            j = 0
            for char in line:
                if(validar_caracter(char)):
                    tablero[i][j] = char
                j += 1
            i += 1
        archivo.close()
        return tablero
    except:
        return []

#Entrada: Direccion de un archivo
#Salida: Matriz de dimensiones N(filas del archivo) x
#        M(Caracteres x fila)
#Restricciones: Revisar restriciones de formato del problema
#               en la documentación
#Descripción: Lee un archivo de texto con el formato de tablero
#             y retorna una matriz N x M

def inicializar_tablero(archivo):
    archivo = open(archivo,'r')
    filas = 0
    columnas = 0
    for line in archivo:
        filas += 1
        columnas = 0
        for char in line:
                columnas += 1        
    tablero = [[0 for i in range(columnas)] for j in range(filas)]
    return tablero
    

            
#Entrada: Caracter
#Salida: True o False
#Restricciones: 
#Descripción: Valida si un caracter es valido en la definición
#             del problema(revisar documentación)

def validar_caracter(char):
    if(char == 'A' or char == 'V'):
        return True
    elif(char == '>' or char == '<'):
        return True
    elif(char == 'Z' or char == 'C'):
        return True
    elif(char == ' ' or char == '\n'):
        return True
    else:
        return False




# Entrada: tablero inicial direccion en la cual se encuentra un archivo .txt
#          direccion inicial del conejo (string), cant_individuos (int),
#          generaciones (int) cantidad de generaciones, magregar valor de
#          mutacion para agregar señales (int), mcambiar(int), mquitar(int),
#          tipo_cruce(int) 0 indica que es por columnas y 1 si es por filas
# Salida: None, se generan un estructura de salida que se especifica en la
#         definición del problema (revisar documentación)
# Restricciones: Que se cumplan los tipos de la entrada, y  que los valores de
#               magregar, mcambiar, mquitar sumados sean menor a 100
# Descripción: Funcion general del algortimo genetico, aqui se unen todas
#              las demas partes. Evalua un tablero inicial y trata de encontrar
#              el camino optimo que el conejo debe seguir para que pueda
#              comer todas las zanahorias


def algortimo_genetico(tablero_inicial, direccion, cant_individuos, generaciones,
                       magregar, mcambiar, mquitar, tipo_cruce):

    mutacion_agregar_signal = magregar
    mutacion_cambiar_direccion = mcambiar
    mutacion_quitar_signal = mquitar
    tablero = leer_tablero(tablero_inicial)

    matriz_tablero = []

    for t in tablero:
        t = t[:-1]
        matriz_tablero.append(t)

    individuos = []
    x = cant_individuos
    while(x > 0):
        individuos.append(copy.deepcopy(matriz_tablero))
        x -= 1

    cant = 1

    try:
        ruta = "salida_genetico/"+direccion
        shutil.rmtree(ruta)
    except:
        pass

    global mejor
    mejor = []

    while(cant <= generaciones):
        print("\n")
        print("GENERACION: "+str(cant).zfill(5))
        for i in individuos:
            i_aux = mutacion(i, mutacion_agregar_signal, mutacion_cambiar_direccion,
                             mutacion_quitar_signal)

        n = len(individuos)

        next_gen = copy.deepcopy(individuos)

        while(n > 0):
            random.seed(time.clock())

            i1 = random.randint(0, len(individuos)-1)
            i2 = random.randint(0, len(individuos)-1)

            hijos = cruce(individuos[i1], individuos[i2], tipo_cruce)

            next_gen.extend(hijos)
            n -= 1

        individuos = elegir_mejores(next_gen, len(individuos), direccion, cant)
        print_tablero_genetico(direccion, cant, individuos)

        cant += 1

    print("\n")
    print("El mejor individuo es: INDIVIDUO " +
          str(mejor[0]).zfill(5) + " GENERACION " + str(mejor[1]).zfill(5))
    print("\n")

# Entrada: gen es la matriz con el tablero, cantidad es el numero de Individuos
#          por generacion, direccion en la que se mueve el conejo(string),
#          generacion es el numero de la generacoin actual
# Salida: Arreglo con individuos
# Restricciones: Que se cumplan los tipos de la entrada, cantidad tiene que
#                menor o igual a la cantidad de individuos
# Descripción: Dado una generacion, con padres e hijos, selecciona a los mejores
#              quienes tengan un fitness mas alto


def elegir_mejores(gen, cantidad, direccion, generacion):
    global mejor
    indiviuos = copy.deepcopy(gen)
    for i in indiviuos:
        puntuacion = fitness(i, direccion)
        i.append(puntuacion)

    gen = sorted(indiviuos, key=lambda point: point[-1])

    gen = gen[-cantidad:]
    next_gen = []
    n = 1

    for i in gen:
        if mejor == []:
            mejor.extend([n, generacion, i[-1]])
        elif mejor[2] < i[-1]:
            mejor = []
            mejor.extend([n, generacion, i[-1]])

        print("INDIVIDUO " + str(n).zfill(5) + " APTITUD: " + str(i[-1]))
        i = i[:-1]
        next_gen.append(i)
        n += 1

    return next_gen

# Entrada: individuo1 y individuo2 son la matrices con un tablero, tipo indica
#          el tipo de cruce 0 indica que es por columnas y 1 si es por filas
# Salida: Devuelve arreglo con dos matrices que son el resultado del cruce
#         de los indiviuos
# Restricciones: Que se cumplan los tipos de la entrada
# Descripción: Apartir de dos individuos (padres) se generan otros dos indiviuos
#              que son los hijos


def cruce(individuo1, individuo2, tipo):
    if tipo == 0:
        n = len(individuo1)
        h1 = individuo1[:n//2]
        h1.extend(individuo2[n//2:])
        h2 = individuo2[:n//2]
        h2.extend(individuo1[n//2:])

        h = []
        h.append(h1)
        h.append(h2)

        return h
    else:
        n = len(individuo1[0])
        h1 = copy.deepcopy(individuo1)
        h2 = copy.deepcopy(individuo2)
        for i in range(0, len(individuo1)):
            h = individuo1[i][:n//2]
            h.extend(individuo2[i][n//2:])
            h1[i] = copy.deepcopy(h)
            h = individuo2[i][:n//2]
            h.extend(individuo1[i][n//2:])
            h2[i] = copy.deepcopy(h)

        h = []
        h.append(h1)
        h.append(h2)

        return h

# Entrada: individuo es la matriz con el tablero, valor de mutacion para agregar
#          una señal (int), cambiar (int), quitar (int)
# Salida: Matriz con indiviuo mutado
# Restricciones: Que se cumplan los tipos de la entrada, y que los valores de
#               m_agregar, m_cambiar, m_quitar sumados sean menor a 100
# Descripción: Dado un indiviuo (tablero), se toma un valor aleatoria
#              y segun ese valor se altera el tablero agregando, cambiando o
#              eliminando una señal


def mutacion(individuo, m_agregar, m_cambiar, m_quitar):
    random.seed(time.clock())
    mutacion = random.randint(0, 100)
    m_cambiar += m_agregar
    m_quitar += m_cambiar
    signals = ['<', '>', 'A', 'V']

    if mutacion < m_agregar:
        add = True
        n = 0
        dimension = len(individuo) * len(individuo[0])
        while(add and n < dimension):
            i = random.randint(0, len(individuo)-1)
            j = random.randint(0, len(individuo[0])-1)
            x = random.randint(0, 3)

            if individuo[i][j] == ' ':
                individuo[i][j] = signals[x]
                add = False
            n += 1

    elif mutacion < m_cambiar:
        signals_position = []
        for i in range(len(individuo)):
            for j in range(len(individuo[0])):
                if (individuo[i][j] == '<' or individuo[i][j] == '>' or
                        individuo[i][j] == 'A' or individuo[i][j] == 'V'):
                    signals_position.append([i, j])

        if(len(signals_position) > 0):
            x = random.randint(0, len(signals_position)-1)
            pos = signals_position[x]
            x = random.randint(0, 3)
            individuo[pos[0]][pos[1]] = signals[x]

    elif mutacion < m_quitar:
        signals_position = []
        for i in range(len(individuo)):
            for j in range(len(individuo[0])):
                if (individuo[i][j] == '<' or individuo[i][j] == '>' or
                        individuo[i][j] == 'A' or individuo[i][j] == 'V'):
                    signals_position.append([i, j])

        if(len(signals_position) > 0):
            x = random.randint(0, len(signals_position)-1)
            pos = signals_position[x]
            individuo[pos[0]][pos[1]] = " "

    return individuo

# Entrada: individuo es la matriz con el tablero, direecion en la que se mueve
#           el conejo(string),
# Salida: Devuelve un entero que indica la puntuacion del inidividuo
# Restricciones: Que se cumplan los tipos de la entrada
# Descripción: Dado un individuo (tablero), determina la puntuacion tomando
#              en cuenta los pasos dados, señales colocadas y cantidad de
#              zanahorias recogidas


def fitness(individuo, direccion):
    total_zanahorias = 0
    cant_signals = 0

    pos_conejo = []

    C1 = 100
    C2 = 5
    C3 = 1
    C4 = 3

    for i in range(len(individuo)):
        for j in range(len(individuo[0])):
            if individuo[i][j] == 'C':
                pos_conejo.extend([i, j])
            elif individuo[i][j] == 'Z':
                total_zanahorias += 1
            elif (individuo[i][j] == '<' or individuo[i][j] == '>' or
                  individuo[i][j] == 'A' or individuo[i][j] == 'V'):
                cant_signals += 1

    if cant_signals == 0:
        return -50

    aux = copy.deepcopy(individuo)

    resultado = recorrer_tablero(
        aux, pos_conejo, direccion, total_zanahorias, 0)

    cant_pasos = resultado[0]
    cant_zanahorias = resultado[1]
    zanahorias_faltantes = total_zanahorias - cant_zanahorias

    fitness = C1*cant_zanahorias - \
        (C2*cant_signals+C3*cant_pasos+C4*zanahorias_faltantes)

    return fitness

# Entrada: individuo es la matriz con el tablero, posicion actual del
#          conejo(arreglo), direecion en la que se mueve el conejo(string),
#          total de zanahorias(int),numero de la recursion actual(int)
# Salida: Arreglo con cantidad de pasos dados y cantidad de zanahorias recogidas
# Restricciones: Que se cumplan los tipos de la entrada
# Descripción: Simula como recorreria el conejo un tablero dado, segun los
#              simbolos y la direccion inicial del conejo


def recorrer_tablero(individuo, pos_conejo, direccion, total_zanahoria, num):
    cant_pasos = 0
    cant_zanahorias = 0

    if total_zanahoria == 0:
        return [0, 0]

    if num >= 100:
        return [150, cant_zanahorias]

    if direccion == 'derecha' or direccion == '>':
        i = pos_conejo[0]
        for j in range(pos_conejo[1], len(individuo[0])):
            if j >= len(individuo[0]):
                break
            elif j == pos_conejo[1]:
                continue

            cant_pasos += 1
            if individuo[i][j] == 'Z':
                cant_zanahorias += 1
                individuo[i][j] = ' '
            elif individuo[i][j] == '<':
                return [100, cant_zanahorias]
            elif (individuo[i][j] == 'A' or individuo[i][j] == 'V'):
                zanahorias = total_zanahoria - cant_zanahorias
                resultado = recorrer_tablero(
                    individuo, [i, j], individuo[i][j], zanahorias, num+1)
                return [resultado[0]+cant_pasos, resultado[1]+cant_zanahorias]

    elif direccion == 'izquierda' or direccion == '<':
        len_individuo = len(individuo[0])
        i = pos_conejo[0]
        for x in range(pos_conejo[1], len_individuo+1):
            j = len_individuo-x
            if j >= len_individuo:
                break
            elif j == pos_conejo[1]:
                continue

            cant_pasos += 1
            if individuo[i][j] == 'Z':
                cant_zanahorias += 1
                individuo[i][j] = ' '
            elif individuo[i][j] == '>':
                return [100, cant_zanahorias]
            elif (individuo[i][j] == 'A' or individuo[i][j] == 'V'):
                zanahorias = total_zanahoria - cant_zanahorias
                resultado = recorrer_tablero(
                    individuo, [i, j], individuo[i][j], zanahorias, num+1)
                return [resultado[0]+cant_pasos, resultado[1]+cant_zanahorias]

    elif direccion == 'arriba' or direccion == 'A':
        j = pos_conejo[1]
        len_individuo = len(individuo)

        for x in range(pos_conejo[0], len_individuo+1):
            i = len_individuo-x
            if i >= len_individuo:
                break
            elif i == pos_conejo[0]:
                continue

            cant_pasos += 1
            if individuo[i][j] == 'Z':
                cant_zanahorias += 1
                individuo[i][j] = ' '
            elif individuo[i][j] == 'V':
                return [100, cant_zanahorias]
            elif (individuo[i][j] == '<' or individuo[i][j] == '>'):
                zanahorias = total_zanahoria - cant_zanahorias
                resultado = recorrer_tablero(
                    individuo, [i, j], individuo[i][j], zanahorias, num+1)
                return [resultado[0]+cant_pasos, resultado[1]+cant_zanahorias]

    elif direccion == 'abajo' or direccion == 'V':
        j = pos_conejo[1]

        for i in range(pos_conejo[0], len(individuo)):
            if i >= len(individuo):
                break
            elif i == pos_conejo[0]:
                continue

            cant_pasos += 1
            if individuo[i][j] == 'Z':
                cant_zanahorias += 1
                individuo[i][j] = ' '
            elif individuo[i][j] == 'A':
                return [100, cant_zanahorias]
            elif (individuo[i][j] == '<' or individuo[i][j] == '>'):
                zanahorias = total_zanahoria - cant_zanahorias
                resultado = recorrer_tablero(
                    individuo, [i, j], individuo[i][j], zanahorias, num+1)
                return [resultado[0]+cant_pasos, resultado[1]+cant_zanahorias]

    return [cant_pasos, cant_zanahorias]


# Entrada: Direccion de un archivo
# Salida: Tablero del problema del conejo(Detalle en la documentación)
# Restricciones: Revisar restriciones de formato en la documentación
# Descripción: Lee un archivo de texto con el formato de tablero
#             y retorna una matriz con la estructura del problema

def leer_tablero(archivo):
    try:
        tablero = inicializar_tablero(archivo)
        archivo = open(archivo, 'r')
        if(tablero == []):
            return []
        i = 0
        j = 0
        for line in archivo:
            j = 0
            for char in line:
                if(validar_caracter(char)):
                    tablero[i][j] = char
                j += 1
            i += 1
        archivo.close()
        return tablero
    except:
        return []

# Entrada: Direccion de un archivo
# Salida: Matriz de dimensiones N(filas del archivo) x
#        M(Caracteres x fila)
# Restricciones: Revisar restriciones de formato del problema
#               en la documentación
# Descripción: Lee un archivo de texto con el formato de tablero
#             y retorna una matriz N x M


def inicializar_tablero(archivo):
    archivo = open(archivo, 'r')
    filas = 0
    columnas = 0
    for line in archivo:
        filas += 1
        columnas = 0
        for char in line:
            columnas += 1
    tablero = [[0 for i in range(columnas)] for j in range(filas)]
    return tablero


# Entrada: Caracter
# Salida: True o False
# Restricciones:
# Descripción: Valida si un caracter es valido en la definición
#             del problema(revisar documentación)

def validar_caracter(char):
    if(char == 'A' or char == 'V'):
        return True
    elif(char == '>' or char == '<'):
        return True
    elif(char == 'Z' or char == 'C'):
        return True
    elif(char == ' ' or char == '\n'):
        return True
    else:
        return False

# Entrada: Direccion (String), generacion (int), Individuos arreglo con todos
#          individuos de la generacion
# Salida: None
# Restricciones: Que se cumplan los tipos de la entrada
# Descripción: Crea la estructura de salida que se especifica en la definición
#               del problema (revisar documentación)


def print_tablero_genetico(direccion, generacion, indiviuos):
    ruta = "salida_genetico/"+direccion+"/"+str(generacion).zfill(5)
    try:
        os.makedirs(ruta)
    except:
        pass

    try:
        n = 1
        for individuo in indiviuos:
            name = ruta + "/" + str(n).zfill(5) + ".txt"
            string = ""
            file = open(name, "w+")
            for fila in individuo:
                for k in fila:
                    string += k
                string += "\n"
            file.write(string)
            file.close()
            n += 1
    except:
        pass
