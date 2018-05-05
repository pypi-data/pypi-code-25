##################DEPENDENCIAS##################
import pandas as pd
from random import uniform
import time
import random
##################GLOBALES CSV##################
RUTA_VOTOS_POR_CANTON = "votosPorCanton.csv"
RUTA_VOTOS_POR_CANTON_2 = "votosPorCanton2.csv"
RUTA_INDICADORES_POR_CANTON = "indicesCantonales.csv"
RUTA_EDADES_HOMBRE = "edadesHombres.csv"
RUTA_EDADES_MUJER = "edadesMujeres.csv"
####################GLOBALES####################

_indices_cantonales = []
_poblacion = 0
_poblacion_por_canton = []
_edades_por_canton = []
_votos = []
_votos_segunda_ronda = []
_partidos = []
_partidos_2 = []
_distribucion_edades_hombres = []
_distribucion_edades_mujeres = []
_edades = []
_probabilidad_votos = []
_probabilidad_votos_2 = []

_cantones_por_provincia = [
    [
        0, 19], [
            20, 34], [
                35, 42], [
                    43, 52], [
                        53, 63], [
                            64, 74], [
                                75, 80]]


def generar_muestra_pais(n):
    if not isinstance(n, int):
        return None

    if n <= 0:
        return None

    return generar_muestra_aux(n, "")


def generar_muestra_provincia(n, nombre_provincia):

    if not isinstance(n, int):
        return None

    if n <= 0:
        return None

    if(get_indices_provincia(nombre_provincia) is None):
        return None
    return generar_muestra_aux(n, nombre_provincia)


def generar_muestra_aux(n, provincia):
    global _indices_cantonales
    global _poblacion
    global _poblacion_por_canton
    global _votos
    global _partidos
    global _partidos_2
    global _distribucion_edades_hombres
    global _distribucion_edades_mujeres
    global _edades
    global _probabilidad_votos
    global _probabilidad_votos_2
    global _votos_segunda_ronda
    return_list = []

    _indices_cantonales = pd.read_csv(RUTA_INDICADORES_POR_CANTON)
    temp = []
    for i in range(0, 31):
        temp += [_indices_cantonales.iloc[i]]
    _indices_cantonales = temp
    _poblacion = set_poblacion(_indices_cantonales)
    _poblacion_por_canton = generar_probabilidad_acumulada(_poblacion)
    _votos = pd.read_csv(RUTA_VOTOS_POR_CANTON)
    _votos_segunda_ronda = pd.read_csv(
        RUTA_VOTOS_POR_CANTON_2,
        encoding="ISO-8859-1")
    temp = []
    temp2 = []
    for i in range(1, 82):
        temp += [_votos.ix[:, i]]
        temp2 += [_votos_segunda_ronda.ix[:, i]]
    _votos = temp
    _votos_segunda_ronda = temp2
    temp = []
    temp2 = []
    _partidos = pd.read_csv(RUTA_VOTOS_POR_CANTON, usecols=[0])
    _partidos_2 = pd.read_csv(
        RUTA_VOTOS_POR_CANTON_2,
        encoding="ISO-8859-1",
        usecols=[0])
    for i in range(0, 15):
        temp += [_partidos.ix[i, 0]]
    for i in range(0, 4):
        temp2 += [_partidos_2.ix[i, 0]]
    _partidos = temp
    _partidos_2 = temp2
    _distribucion_edades_hombres = pd.read_csv(RUTA_EDADES_HOMBRE)
    temp = []
    temp2 = []
    for i in range(0, 15):
        temp += [_distribucion_edades_hombres.iloc[i]]
    _distribucion_edades_hombres = temp
    temp = []
    _distribucion_edades_mujeres = pd.read_csv(RUTA_EDADES_MUJER)
    for i in range(0, 15):
        temp += [_distribucion_edades_mujeres.iloc[i]]
    _distribucion_edades_mujeres = temp
    _edades = pd.read_csv(RUTA_EDADES_HOMBRE, usecols=[0])
    temp = []
    for i in range(0, 15):
        temp += [_edades.ix[i, 0]]
    _edades = temp
    for i in range(0, 81):
        probabilidades = calcular_probabilidad_votos(
            _votos[i], sumar_vector(_votos[i], 15))
        _probabilidad_votos += [probabilidades]
        probabilidades_2 = calcular_probabilidad_votos(
            _votos_segunda_ronda[i], sumar_vector(_votos_segunda_ronda[i], 4))
        _probabilidad_votos_2 += [probabilidades_2]
    #start = time.clock()
    for i in range(0, n):
        return_list += [generar_votante(provincia)]
    #print(time.clock() - start)
    return return_list


def generar_votante(provincia):
    global _indices_cantonales
    votante = [0] * 24
    rand_num = uniform(0, _poblacion_por_canton[-1])
    if(provincia == ""):
        num_canton = 0
        ultimo_indice = 81
    else:
        indices = get_indices_provincia(provincia)
        num_canton = indices[0]
        ultimo_indice = indices[1] + 1

    for i in range(num_canton, ultimo_indice):
        if(rand_num < _poblacion_por_canton[i]):
            num_canton = i
            break

    num_partido = 0
    probabilidad_votos = _probabilidad_votos[num_canton]
    rand_num = uniform(0, 1)

    for probabilidad in probabilidad_votos:
        if(rand_num <= probabilidad):
            break
        else:
            num_partido += 1

    #partido = _partidos[num_partido]
    votante[22] = num_partido + 1

    num_partido = 0
    probabilidad_votos = _probabilidad_votos_2[num_canton]
    rand_num = uniform(0, 1)

    for probabilidad in probabilidad_votos:
        if(rand_num <= probabilidad):
            break
        else:
            num_partido += 1

    #partido = _partidos_2[num_partido]
    votante[23] = num_partido + 1

    num_canton += 1
    sexo = muestra_sexo(num_canton)
    edad = str(generar_edad(num_canton, sexo))
    edad = get_edad(edad)
    votante[21] = edad

    # Indices
    # poblacion
    votante[0] = _indices_cantonales[0][num_canton]
    # superficie
    votante[1] = _indices_cantonales[1][num_canton]
    # Densidad de poblacion
    votante[2] = _indices_cantonales[2][num_canton]
    # Urbano o no
    votante[3] = sample(_indices_cantonales[3][num_canton])
    # Hombre o Mujer
    #votante[4] = _indices_cantonales[4][num_canton]
    votante[4] = sexo
    # Dependencia demografica, mayores a 65
    if(edad < 65):
        votante[5] = 0
    else:
        votante[5] = sample(_indices_cantonales[5][num_canton])
    # Ocupa vivienda
    indice_vivienda = _indices_cantonales[6][num_canton]
    votante[6] = sample(indice_vivienda / votante[0])
    # promedio ocupantes
    votante[7] = _indices_cantonales[7][num_canton]
    # vivienda en buen estado
    if(votante[6] == 1):
        votante[8] = sample(_indices_cantonales[8][num_canton])
    else:
        votante[8] = 2  # "SIN VIVIENDA"
    # vivienda hacinada
    if(votante[6] == 1):
        votante[9] = sample(_indices_cantonales[9][num_canton])
    else:
        votante[9] = 2  # "SIN VIVIENDA"
    # alfabetismo
    if(edad <= 24):
        votante[10] = sample(_indices_cantonales[11][num_canton])
    else:
        votante[10] = sample(_indices_cantonales[12][num_canton])
    # escolaridad promedio
    if(edad <= 24):
        votante[11] = _indices_cantonales[13][num_canton]
    elif(edad < 50):
        votante[11] = sample(_indices_cantonales[14][num_canton])
    else:
        votante[11] = sample(_indices_cantonales[15][num_canton])
    # asistencia a educacion regular
    if(edad <= 24):
        votante[12] = _indices_cantonales[19][num_canton]
    else:
        votante[12] = _indices_cantonales[20][num_canton]

    # participacion en la fuerza de trabajo
    if(sexo == 1):  # Hombre = 1 Mujer = 2
        votante[14] = sample(_indices_cantonales[23][num_canton])
    else:
        votante[14] = sample(_indices_cantonales[24][num_canton])
    # fuera de la fuerza de trabajo
    if(votante[14] == 1):
        votante[13] = 0
    else:
        votante[13] = 1
    # porcentaje de poblacion ocupada no asegurada
    if(votante[14] == 1):
        votante[15] = sample(_indices_cantonales[25][num_canton])
    else:
        votante[15] = 2  # "NFT"
    # Nacido en el extranjero
    votante[16] = sample(_indices_cantonales[26][num_canton])
    # discapacidad
    votante[17] = sample(_indices_cantonales[27][num_canton])
    # poblacion no asegurada
    if(votante[15] == 2):
        votante[18] = sample(_indices_cantonales[28][num_canton])
    elif(votante[15] == 0):
        votante[18] = 1
    else:
        votante[18] = 0
    # porcentaje de hogares con jefatura femenina
    votante[19] = _indices_cantonales[29][num_canton]
    # porcentaje de hogares con jefatura compartida
    votante[20] = _indices_cantonales[30][num_canton]
    return votante


def sample(probabilidad):
    rand_num = uniform(0, 1)
    if(rand_num <= probabilidad):
        return 1
    else:
        return 0


def sumar_vector(vector, max_rango):
    suma = 0
    for indice in range(0, max_rango):
        suma += vector[indice]
    return suma


def muestra_sexo(num_canton):
    cantidad_hombres = _indices_cantonales[4][num_canton]
    indice = cantidad_hombres / (cantidad_hombres + 100)
    rand_num = uniform(0, 1)
    if(rand_num < indice):
        return 1  # "HOMBRE"
    else:
        return 2  # "MUJER"


def generar_edad(num_canton, sexo):
    global _edades
    global _distribucion_edades_hombres
    global _distribucion_edades_mujeres
    if(sexo == 1):
        distribucion = _distribucion_edades_hombres
    else:
        distribucion = _distribucion_edades_mujeres
    probabilidad_acumulada = 0
    probabilidades = []
    for i in range(0, 15):
        if(sexo == 1):
            probabilidad_acumulada += distribucion[i][num_canton] * -1
        else:
            probabilidad_acumulada += distribucion[i][num_canton]
        probabilidades += [probabilidad_acumulada]
    rand_num = uniform(0, probabilidades[-1])
    i = 0
    for prob in probabilidades:
        if(rand_num <= prob):
            return _edades[i]
        i += 1
    return ""


def calcular_probabilidad_votos(votos, total_votos):
    probabilidad = []
    probabilidad_acumulada = 0
    for num_votos in votos:
        probabilidad_acumulada += (num_votos / total_votos)
        if(probabilidad_acumulada > 1.0):
            probabilidad_acumulada = 1.0
        probabilidad += [probabilidad_acumulada]

    return probabilidad


def set_poblacion(indices_cantonales):

    poblacion = indices_cantonales[0]

    return poblacion


def generar_probabilidad_acumulada(poblacion):
    probabilidad = []
    probabilidad_acumulada = 0
    total_poblacion = sumar_vector(poblacion[1:], 81)

    for poblacion_cantonal in poblacion[1:]:
        probabilidad_acumulada += (poblacion_cantonal / total_poblacion)
        probabilidad += [probabilidad_acumulada]
    return probabilidad


def get_edad(edad):
    if(edad == "15 a 19"):
        return 19
    elif(edad == "20 a 24"):
        return 24
    elif(edad == "25 a 29"):
        return 29
    elif(edad == "30 a 34"):
        return 34
    elif(edad == "35 a 39"):
        return 39
    elif(edad == "40 a 44"):
        return 44
    elif(edad == "45 a 49"):
        return 49
    else:
        return 50


def get_indices_provincia(provincia):
    if(provincia == "SAN JOSE"):
        return _cantones_por_provincia[0]
    elif(provincia == "ALAJUELA"):
        return _cantones_por_provincia[1]
    elif(provincia == "CARTAGO"):
        return _cantones_por_provincia[2]
    elif(provincia == "HEREDIA"):
        return _cantones_por_provincia[3]
    elif(provincia == "GUANACASTE"):
        return _cantones_por_provincia[4]
    elif(provincia == "PUNTARENAS"):
        return _cantones_por_provincia[5]
    elif(provincia == "LIMON"):
        return _cantones_por_provincia[6]
    else:
        return None


def cambiar_semilla(semilla):
    random.seed(semilla)
