import math
import numpy as np
from random import uniform


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
