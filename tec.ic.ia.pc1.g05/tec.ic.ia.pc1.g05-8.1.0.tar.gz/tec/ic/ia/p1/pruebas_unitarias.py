from arboldecision import *


# prueba 1: comprobar que una columna específica del conjunto de datos de
# la lista correcta
def test_arbol_decision_1():
    cambiar_semilla(9000)
    muestra = generar_muestra_pais(30)
    muestra_normalizada = datos_r1_normalizados(muestra)
    lista_normalizada = np.array(muestra_normalizada).tolist()
    lista = obtener_conjunto_columna(lista_normalizada, 2)
    assert lista == [-0.45665091310382117, -0.6661347359083404, -0.7305015372731146, -0.7183989887442243, -0.7421626485865295, -0.7350498620771594, -0.7320886887068256, -0.7305015372731146, 2.173748098118062, 0.1477507991904072, -0.7441476523871889, 0.04503328945905693, 0.05327984692143104, 0.25136935552591594, -
                     0.45665091310382117, 0.9027724574117136, -0.6308073851872582, -0.7320886887068256, -0.7310434192983564, -0.7463492395293673, 2.854242838946475, -0.011159848947009469, 0.04503328945905693, -0.7355966579010542, 1.0999282138467341, 1.0999282138467341, 2.173748098118062, 0.9083266227830806, -0.7236999545137945, -0.732128452378926]

# comprobar que el árbol de decisión sea una referencia al nodo raiz, para
# la primera ronda


def test_arbol_decision_2():
    muestra = generar_muestra_pais(1000)
    data_r1 = datos_r1_normalizados(muestra)
    arbol_r1, c_pruebas_r1, c_entrenamiento_r1 = generar_arbol(
        1000, 25, data_r1)
    assert isinstance(arbol_r1, Nodo)

# comprobar que el árbol de decisión sea una referencia al nodo raiz, para
# la segunda ronda


def test_arbol_decision_3():
    limpiar_variables_globales()
    muestra = generar_muestra_pais(1000)
    data_r2 = datos_r2_normalizados(muestra)
    arbol_r2, c_pruebas_r2, c_entrenamiento_r2 = generar_arbol(
        1000, 25, data_r2)
    assert isinstance(arbol_r2, Nodo)

# comprobar que el árbol de decisión sea una referencia al nodo raiz, para
# la segunda + primera ronda


def test_arbol_decision_4():
    limpiar_variables_globales()
    muestra = generar_muestra_pais(1000)
    data_r2_r1 = datos_r2_con_r1_normalizados(muestra)
    arbol_r2_r1, c_pruebas_r2_r1, c_entrenamiento_r2_r1 = generar_arbol(
        1000, 25, data_r2_r1)
    assert isinstance(arbol_r2_r1, Nodo)

# comprobar que para el conjunto de datos dado, la cantidad de votos sea
# la correcta para cada partido


def test_arbol_decision_5():
    cambiar_semilla(9000)
    muestra = generar_muestra_pais(30)
    muestra_normalizada = datos_r1_normalizados(muestra)
    lista_normalizada = np.array(muestra_normalizada).tolist()
    partidos, votos_por_partido = contar_valores_conjunto_entrenamiento(
        lista_normalizada)
    assert partidos == [12.0, 7.0, 11.0, 2.0, 13.0, 8.0, 6.0]
    assert votos_por_partido == [7, 2, 1, 9, 7, 3, 1]

# comprobar que la pluraridad sea la correcta


def test_arbol_decision_6():
    cambiar_semilla(9000)
    muestra = generar_muestra_pais(30)
    muestra_normalizada = datos_r1_normalizados(muestra)
    lista_normalizada = np.array(muestra_normalizada).tolist()
    partido = obtener_pluralidad(lista_normalizada)
    assert partido == 2.0

# comprobar que la poda de un arbol retorna un nodo para la primera ronda


def test_arbol_decision_7():
    limpiar_variables_globales()
    muestra = generar_muestra_pais(1000)
    data_r1 = datos_r1_normalizados(muestra)
    arbol_r1, c_pruebas_r1, c_entrenamiento_r1 = generar_arbol(
        1000, 25, data_r1)
    arbol_podado = podar_arbol_aux_aux(arbol_r1, 0.08)
    assert isinstance(arbol_r1, Nodo)

# comprobar que la poda de un arbol retorna un nodo para la segunda ronda


def test_arbol_decision_8():
    limpiar_variables_globales()
    muestra = generar_muestra_pais(1000)
    data_r2 = datos_r2_normalizados(muestra)
    arbol_r2, c_pruebas_r2, c_entrenamiento_r2 = generar_arbol(
        1000, 25, data_r2)
    arbol_podado = podar_arbol_aux_aux(arbol_r2, 0.08)
    assert isinstance(arbol_r2, Nodo)

# comprobar que la poda de un arbol retorna un nodo para la segunda +
# primera ronda


def test_arbol_decision_9():
    limpiar_variables_globales()
    muestra = generar_muestra_pais(1000)
    data_r2_r1 = datos_r2_con_r1_normalizados(muestra)
    arbol_r2_r1, c_pruebas_r2_r1, c_entrenamiento_r2_r1 = generar_arbol(
        1000, 25, data_r2_r1)
    arbol_podado = podar_arbol_aux_aux(arbol_r2_r1, 0.08)
    assert isinstance(arbol_r2_r1, Nodo)

# comprobar que un árbol contenga solo hojas


def test_arbol_decision_10():
    hoja = Hoja("1.0")
    hoja_2 = Hoja("2.0")
    lista_hijos = [hoja, hoja_2]
    nodo = Nodo(lista_hijos, 2, {0.2, 0.3}, 0.09, 1, [])
    assert es_nodo_con_hojas(nodo)

# comprobar que un árbol no contenga solo hojas


def test_arbol_decision_11():
    hoja = Hoja("1.0")
    hoja_2 = Hoja("2.0")
    hoja_3 = Hoja("3.0")
    nodo_hijo = Nodo([hoja_3], 3, {0.1, 0.12}, 0.1, 2, [])
    lista_hijos = [hoja, hoja_2, nodo_hijo]

    nodo = Nodo(lista_hijos, 2, {0.2, 0.3}, 0.09, 1, [])
    assert not es_nodo_con_hojas(nodo)

# comprobar que la entropía de el valor correcto


def test_arbol_decision_12():
    cambiar_semilla(9000)
    muestra = generar_muestra_pais(30)
    muestra_normalizada = datos_r1_normalizados(muestra)
    lista_normalizada = np.array(muestra_normalizada).tolist()
    entropia = obtener_entropia_conjunto_entrenamiento(lista_normalizada)
    assert entropia == 2.4206512148101607

# comprobar que la ganancia que se de para un conjunto de entrenamiento
# sea el correcto


def test_arbol_decision_13():
    cambiar_semilla(9000)
    muestra = generar_muestra_pais(30)
    muestra_normalizada = datos_r1_normalizados(muestra)
    lista_normalizada = np.array(muestra_normalizada).tolist()
    ganancias = recorrer_columnas_datos_entrenamiento(lista_normalizada)
    assert ganancias == [
        2.087317881476827,
        2.087317881476827,
        2.087317881476827,
        0.0,
        0.26818744962329744,
        0.0,
        0.11636728702215882,
        2.087317881476827,
        0.11636728702215882,
        0.11636728702215882,
        0.0,
        0.5233283968586939,
        2.153984548143494,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        2.087317881476827,
        0.9199995478550316]

# comprobar que los verdaderos positivos, falsos positivos y precisión de entrenamiento y prueba sea
# el correcto para la ronda 1


def test_arbol_decision_14():
    cambiar_semilla(9000)
    muestra = generar_muestra_pais(30)
    muestra_normalizada = datos_r1_normalizados(muestra)
    lista_normalizada = np.array(muestra_normalizada).tolist()
    arbol_r1, c_pruebas_r1, c_entrenamiento_r1 = generar_arbol(
        30, 10, lista_normalizada)

    predicciones_r1_prueba, valores_reales_r1_prueba = predecir(
        c_pruebas_r1, arbol_r1)
    verdaderos_positivos_r1_prueba, falsos_positivos_r1_prueba = obtener_verdaderos_falsos_positivos(
        predicciones_r1_prueba, valores_reales_r1_prueba)

    predicciones_r1_entrenamiento, valores_reales_r1_entrenamiento = predecir(
        c_entrenamiento_r1, arbol_r1)
    verdaderos_positivos_r1_entrenamiento, falsos_positivos_r1_entrenamiento = obtener_verdaderos_falsos_positivos(
        predicciones_r1_entrenamiento, valores_reales_r1_entrenamiento)

    precision_r1_prueba = obtener_precision(
        verdaderos_positivos_r1_prueba,
        falsos_positivos_r1_prueba)

    precision_r1_entrenamiento = obtener_precision(
        verdaderos_positivos_r1_entrenamiento,
        falsos_positivos_r1_entrenamiento)

    assert falsos_positivos_r1_entrenamiento == 18
    assert falsos_positivos_r1_prueba == 3
    assert precision_r1_prueba == 0
    assert precision_r1_entrenamiento == 0.3333333333333333


# comprobar que los verdaderos positivos, falsos positivos y precisión de entrenamiento y prueba sea
# el correcto para la ronda 2
def test_arbol_decision_15():
    cambiar_semilla(9000)
    muestra = generar_muestra_pais(30)
    muestra_normalizada = datos_r2_normalizados(muestra)
    lista_normalizada = np.array(muestra_normalizada).tolist()
    arbol_r2, c_pruebas_r2, c_entrenamiento_r2 = generar_arbol(
        30, 10, lista_normalizada)

    predicciones_r2_prueba, valores_reales_r2_prueba = predecir(
        c_pruebas_r2, arbol_r2)
    verdaderos_positivos_r2_prueba, falsos_positivos_r2_prueba = obtener_verdaderos_falsos_positivos(
        predicciones_r2_prueba, valores_reales_r2_prueba)

    predicciones_r2_entrenamiento, valores_reales_r2_entrenamiento = predecir(
        c_entrenamiento_r2, arbol_r2)
    verdaderos_positivos_r2_entrenamiento, falsos_positivos_r2_entrenamiento = obtener_verdaderos_falsos_positivos(
        predicciones_r2_entrenamiento, valores_reales_r2_entrenamiento)

    precision_r2_prueba = obtener_precision(
        verdaderos_positivos_r2_prueba,
        falsos_positivos_r2_prueba)

    precision_r2_entrenamiento = obtener_precision(
        verdaderos_positivos_r2_entrenamiento,
        falsos_positivos_r2_entrenamiento)

    assert falsos_positivos_r2_entrenamiento == 13
    assert falsos_positivos_r2_prueba == 2
    assert precision_r2_prueba == 0.3333333333333333
    assert precision_r2_entrenamiento == 0.5185185185185185


# comprobar que los verdaderos positivos, falsos positivos y precisión de entrenamiento y prueba sea
# el correcto para la ronda 2 + ronda 1
def test_arbol_decision_16():
    cambiar_semilla(9000)
    muestra = generar_muestra_pais(30)
    muestra_normalizada = datos_r2_con_r1_normalizados(muestra)
    lista_normalizada = np.array(muestra_normalizada).tolist()
    arbol_r2_r1, c_pruebas_r2_r1, c_entrenamiento_r2_r1 = generar_arbol(
        30, 10, lista_normalizada)

    predicciones_r2_r1_prueba, valores_reales_r2_r1_prueba = predecir(
        c_pruebas_r2_r1, arbol_r2_r1)
    verdaderos_positivos_r2_r1_prueba, falsos_positivos_r2_r1_prueba = obtener_verdaderos_falsos_positivos(
        predicciones_r2_r1_prueba, valores_reales_r2_r1_prueba)

    predicciones_r2_r1_entrenamiento, valores_reales_r2_r1_entrenamiento = predecir(
        c_entrenamiento_r2_r1, arbol_r2_r1)
    verdaderos_positivos_r2_r1_entrenamiento, falsos_positivos_r2_r1_entrenamiento = obtener_verdaderos_falsos_positivos(
        predicciones_r2_r1_entrenamiento, valores_reales_r2_r1_entrenamiento)

    precision_r2_r1_prueba = obtener_precision(
        verdaderos_positivos_r2_r1_prueba,
        falsos_positivos_r2_r1_prueba)

    precision_r2_r1_entrenamiento = obtener_precision(
        verdaderos_positivos_r2_r1_entrenamiento,
        falsos_positivos_r2_r1_entrenamiento)

    assert falsos_positivos_r2_r1_entrenamiento == 13
    assert falsos_positivos_r2_r1_prueba == 2
    assert precision_r2_r1_prueba == 0.3333333333333333
    assert precision_r2_r1_entrenamiento == 0.5185185185185185
