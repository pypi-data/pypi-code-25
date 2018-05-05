from tec.ic.ia.pc1.g05 import generar_muestra_pais, generar_muestra_provincia
#from arboldecision import *
#from kd_tree import *
#from pc1 import generar_muestra_pais, generar_muestra_provincia
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn import svm
from sklearn.metrics import mean_squared_error, accuracy_score
from keras.models import Sequential
from keras.layers import Dense
import keras
from keras.optimizers import SGD
import tensorflow as tf
import pandas as pd
import sys
import math
from arbol import Nodo, Hoja, Atributo
import csv


prefijo_csv = ""


def split_muestra(muestra, porcentaje):
    cantidad_test = int(len(muestra) * (porcentaje / 100))
    cantidad_training = len(muestra) - cantidad_test
    test_set = []
    training_set = []
    for i in range(0, len(muestra)):
        if(i < cantidad_training):
            training_set += [muestra[i]]
        else:
            test_set += [muestra[i]]
    return training_set, test_set


def support_vector_machines(n_muestra, porcentaje_test, p_kernel):
    global prefijo_csv
    muestra = generar_muestra_pais(n_muestra)
    muestra_r1 = datos_r1_normalizados(muestra)
    muestra_r2 = datos_r2_normalizados(muestra)
    muestra_r2_r1 = datos_r2_con_r1_normalizados(muestra)
    train_r1, test_r1 = split_muestra(muestra_r1, porcentaje_test)
    train_r2, test_r2 = split_muestra(muestra_r2, porcentaje_test)
    train_r2_r1, test_r2_r1 = split_muestra(muestra_r2_r1, porcentaje_test)
    model_r1 = svm.SVC(kernel=p_kernel)
    model_r2 = svm.SVC(kernel=p_kernel)
    model_r2_r1 = svm.SVC(kernel=p_kernel)
    predicciones_train_r1, predicciones_test_r1 = predicciones_svm(
        train_r1, test_r1, model_r1, "1")
    predicciones_train_r2, predicciones_test_r2 = predicciones_svm(
        train_r2, test_r2, model_r2, "2")
    predicciones_train_r2_r1, predicciones_test_r2_r1 = predicciones_svm(
        train_r2_r1, test_r2_r1, model_r2_r1, "2_1")
    for i in range(0, len(train_r1)):
<<<<<<< HEAD
        muestra[i] += [True,
                       predicciones_train_r1[i] + 1,
                       predicciones_train_r2[i] + 1,
                       predicciones_train_r2_r1[i] + 1]
    for i in range(0, len(test_r1)):
        muestra[i + len(train_r1)] += [False,
                                       predicciones_test_r1[i] + 1,
                                       predicciones_test_r2[i] + 1,
                                       predicciones_test_r2_r1[i] + 1]
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
    dataframe.to_csv('resultados_svm.csv', index=False)
=======
        muestra[i] += [True, predicciones_train_r1[i]+1,
                       predicciones_train_r2[i]+1, predicciones_train_r2_r1[i]+1]
    for i in range(0, len(test_r1)):
        muestra[i+len(train_r1)] += [False, predicciones_test_r1[i]+1,
                                     predicciones_test_r2[i]+1, predicciones_test_r2_r1[i]+1]
    dataframe = pd.DataFrame(muestra, columns=['poblacion_canton', 'superficie_canton', 'densidad_poblacion', 'urbano', 'sexo', 'dependencia_demografica', 'ocupa_vivienda', 'promedio_ocupantes', 'vivienda_buen_estado', 'vivienda_hacinada', 'alfabetismo', 'escolaridad_promedio', 'educacion_regular', 'fuera_fuerza_trabajo',
                                               'participacion_fuerza_trabajo', 'asegurado', 'extranjero', 'discapacidad', 'no_asegurado', 'porcentaje_jefatura_femenina', 'porcentaje_jefatura_compartida', 'edad', 'voto_primera_ronda', 'voto_segunda_ronda', 'es_entrenamiento', 'prediccion_r1', 'prediccion_r2', 'prediccion_r2_con_r1'])
    dataframe.to_csv(prefijo_csv + 'resultados_svm.csv', index=False)
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838


def predicciones_svm(train_set, test_set, model, ronda):
    x_train = []
    x_test = []
    y_test = get_column(test_set, -1)
    y_train = get_column(train_set, -1)
# for i in range(0,len(y_train)):
##        y_train[i] -= 1
# for i in range(0,len(y_test)):
##        y_test[i] -= 1
##    y_train = keras.utils.to_categorical(y_train,num_classes = 15)
##    y_test = keras.utils.to_categorical(y_test,num_classes = 15)
    for i in range(0, len(train_set)):
        x_train += [train_set[i][:-1]]
    for i in range(0, len(test_set)):
        x_test += [test_set[i][:-1]]
    model.fit(x_train, y_train)

    prediccion_train = model.predict(x_train)
    prediccion_test = model.predict(x_test)
    squared_error = mean_squared_error(y_train, prediccion_train)
    accuracy = accuracy_score(y_train, prediccion_train)
    squared_error_test = mean_squared_error(y_test, prediccion_test)
    accuracy_test = accuracy_score(y_test, prediccion_test)
    if(ronda == "1"):
        print("[============================]")
        print("Ronda 1 - Error en entrenamiento: ", squared_error)
        print("Ronda 1- Precision en entrenamiento: ", accuracy)
        print("[============================]")
        print("Ronda 1 - Error en pruebas: ", squared_error_test)
        print("Ronda 1 - Precision en pruebas: ", accuracy_test)
    elif(ronda == "2"):
        print("[============================]")
        print("Ronda 2 - Error en entrenamiento: ", squared_error)
        print("Ronda 2- Precision en entrenamiento: ", accuracy)
        print("[============================]")
        print("Ronda 2 - Error en pruebas: ", squared_error_test)
        print("Ronda 2 - Precision en pruebas: ", accuracy_test)
    else:
        print("[============================]")
        print("Ronda 2 con Ronda 1 - Error en entrenamiento: ", squared_error)
        print("Ronda 2 con Ronda 1- Precision en entrenamiento: ", accuracy)
        print("[============================]")
        print("Ronda 2 con Ronda 1 - Error en pruebas: ", squared_error_test)
        print("Ronda 2 con Ronda 1 - Precision en pruebas: ", accuracy_test)
    return prediccion_train, prediccion_test


def regresiones_logisticas(n_muestra, porcentaje_test, regularizacion):
    global prefijo_csv
    muestra = generar_muestra_pais(n_muestra)
    muestra_r1 = datos_r1_normalizados(muestra)
    muestra_r2 = datos_r2_normalizados(muestra)
    muestra_r2_r1 = datos_r2_con_r1_normalizados(muestra)
    train_r1, test_r1 = split_muestra(muestra_r1, porcentaje_test)
    train_r2, test_r2 = split_muestra(muestra_r2, porcentaje_test)
    train_r2_r1, test_r2_r1 = split_muestra(muestra_r2_r1, porcentaje_test)
    predicciones_train_r1, predicciones_test_r1 = regresion_logistica_r1(
<<<<<<< HEAD
        train_r1, test_r1, 5000 / n_muestra, regularizacion)
    predicciones_train_r2, predicciones_test_r2 = regresion_logistica(
        train_r2, test_r2, 5000 / n_muestra, regularizacion)
    predicciones_train_r2_r1, predicciones_test_r2_r1 = regresion_logistica(
        train_r2_r1, test_r2_r1, 5000 / n_muestra, regularizacion, True)
    for i in range(0, len(train_r1)):
        muestra[i] += [True,
                       predicciones_train_r1[i] + 1,
                       predicciones_train_r2[i] + 1,
                       predicciones_train_r2_r1[i] + 1]
    for i in range(0, len(test_r1)):
        muestra[i + len(train_r1)] += [False,
                                       predicciones_test_r1[i] + 1,
                                       predicciones_test_r2[i] + 1,
                                       predicciones_test_r2_r1[i] + 1]
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
    dataframe.to_csv('resultados_regresion_logisitica.csv', index=False)
=======
        train_r1, test_r1, 5000/n_muestra, regularizacion)
    predicciones_train_r2, predicciones_test_r2 = regresion_logistica(
        train_r2, test_r2, 5000/n_muestra, regularizacion)
    predicciones_train_r2_r1, predicciones_test_r2_r1 = regresion_logistica(
        train_r2_r1, test_r2_r1, 5000/n_muestra, regularizacion, True)
    for i in range(0, len(train_r1)):
        muestra[i] += [True, predicciones_train_r1[i]+1,
                       predicciones_train_r2[i]+1, predicciones_train_r2_r1[i]+1]
    for i in range(0, len(test_r1)):
        muestra[i+len(train_r1)] += [False, predicciones_test_r1[i]+1,
                                     predicciones_test_r2[i]+1, predicciones_test_r2_r1[i]+1]
    dataframe = pd.DataFrame(muestra, columns=['poblacion_canton', 'superficie_canton', 'densidad_poblacion', 'urbano', 'sexo', 'dependencia_demografica', 'ocupa_vivienda', 'promedio_ocupantes', 'vivienda_buen_estado', 'vivienda_hacinada', 'alfabetismo', 'escolaridad_promedio', 'educacion_regular', 'fuera_fuerza_trabajo',
                                               'participacion_fuerza_trabajo', 'asegurado', 'extranjero', 'discapacidad', 'no_asegurado', 'porcentaje_jefatura_femenina', 'porcentaje_jefatura_compartida', 'edad', 'voto_primera_ronda', 'voto_segunda_ronda', 'es_entrenamiento', 'prediccion_r1', 'prediccion_r2', 'prediccion_r2_con_r1'])
    dataframe.to_csv(
        prefijo_csv+'resultados_regresion_logisitica.csv', index=False)
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838


def regresion_logistica_r1(train_set, test_set, learning_rate, regularizacion):
    num_epochs = 1500
    display_step = 1
    x_train = []
    x_test = []
    y_test = get_column(test_set, -1)
    y_train = get_column(train_set, -1)
    for i in range(0, len(y_train)):
        y_train[i] -= 1
    for i in range(0, len(y_test)):
        y_test[i] -= 1
    y_train = keras.utils.to_categorical(y_train, num_classes=15)
    y_test = keras.utils.to_categorical(y_test, num_classes=15)
    for i in range(0, len(train_set)):
        x_train += [train_set[i][:-1]]
    for i in range(0, len(test_set)):
        x_test += [test_set[i][:-1]]

    sess = tf.InteractiveSession()

    x = tf.placeholder("float", [None, 22])
    y = tf.placeholder("float", [None, 15])
    W = tf.Variable(tf.zeros([22, 15]))
    b = tf.Variable(tf.zeros([15]))

    sess.run(tf.initialize_all_variables())
<<<<<<< HEAD
    y_ = tf.nn.softmax(tf.matmul(x, W) + b)

    cost = tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=y_)
    if(regularizacion == "l1"):
        optimizer = tf.train.FtrlOptimizer(
            learning_rate=learning_rate,
            l1_regularization_strength=0.5).minimize(cost)
    else:
        optimizer = tf.train.FtrlOptimizer(
            learning_rate=learning_rate,
            l2_regularization_strength=0.5).minimize(cost)
=======
    y_ = tf.nn.softmax(tf.matmul(x, W)+b)

    cost = tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=y_)
    if(regularizacion == "l1"):
        optimizer = tf.train.FtrlOptimizer(learning_rate=learning_rate,
                                           l1_regularization_strength=0.5).minimize(cost)
    else:
        optimizer = tf.train.FtrlOptimizer(learning_rate=learning_rate,
                                           l2_regularization_strength=0.5).minimize(cost)
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838

    with tf.Session() as sess:

        sess.run(tf.global_variables_initializer())
        cost_in_each_epoch = 0
        for epoch in range(num_epochs):

            _, c = sess.run([optimizer, cost], feed_dict={
                            x: x_train, y: y_train})
            cost_in_each_epoch += c
        cost_in_each_epoch_2 = 0
        for epoch in range(num_epochs):

            _, c2 = sess.run([optimizer, cost], feed_dict={
                             x: x_test, y: y_test})
            cost_in_each_epoch_2 += c2
        correct_prediction = tf.equal(tf.argmax(y_, 1), tf.argmax(y, 1))
        cost_train = 0
        cost_test = 0
        for i in cost_in_each_epoch:
            cost_train += i
        for i in cost_in_each_epoch_2:
            cost_test += i
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        print("[============================]")
        print("Ronda 1 - Error en entrenamiento: ", cost_train)
        print("Ronda 1- Precision en entrenamiento: ",
              accuracy.eval({x: x_train, y: y_train}))
        print("[============================]")
        print("Ronda 1 - Error en pruebas: ", cost_test)
        print("Ronda 1 - Precision en pruebas: ",
              accuracy.eval({x: x_test, y: y_test}))
        predicciones_train = y_.eval({x: x_train})
        predicciones_test = y_.eval({x: x_test})
        sess.close()
    predicciones_train = convert_from_one_hot(predicciones_train)
    predicciones_test = convert_from_one_hot(predicciones_test)
    return predicciones_train, predicciones_test


<<<<<<< HEAD
def regresion_logistica(
        train_set,
        test_set,
        learning_rate,
        regularizacion,
        r2_con_r1=False):
=======
def regresion_logistica(train_set, test_set, learning_rate, regularizacion, r2_con_r1=False):
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838
    num_epochs = 1500
    display_step = 1
    x_train = []
    x_test = []
    y_test = get_column(test_set, -1)
    y_train = get_column(train_set, -1)
    for i in range(0, len(y_train)):
        y_train[i] -= 1
    for i in range(0, len(y_test)):
        y_test[i] -= 1
    y_train = keras.utils.to_categorical(y_train, num_classes=4)
    y_test = keras.utils.to_categorical(y_test, num_classes=4)
    for i in range(0, len(train_set)):
        x_train += [train_set[i][:-1]]
    for i in range(0, len(test_set)):
        x_test += [test_set[i][:-1]]

    sess = tf.InteractiveSession()
    if(r2_con_r1):
        x = tf.placeholder("float", [None, 23])
    else:
        x = tf.placeholder("float", [None, 22])
    y = tf.placeholder("float", [None, 4])
    if(r2_con_r1):
        W = tf.Variable(tf.zeros([23, 4]))
    else:
        W = tf.Variable(tf.zeros([22, 4]))
    b = tf.Variable(tf.zeros([4]))

    sess.run(tf.initialize_all_variables())
<<<<<<< HEAD
    y_ = tf.nn.softmax(tf.matmul(x, W) + b)

    cost = tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=y_)
    if(regularizacion == "l1"):
        optimizer = tf.train.FtrlOptimizer(
            learning_rate=learning_rate,
            l1_regularization_strength=1.0).minimize(cost)
    else:
        optimizer = tf.train.FtrlOptimizer(
            learning_rate=learning_rate,
            l1_regularization_strength=1.0).minimize(cost)
=======
    y_ = tf.nn.softmax(tf.matmul(x, W)+b)

    cost = tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=y_)
    if(regularizacion == "l1"):
        optimizer = tf.train.FtrlOptimizer(learning_rate=learning_rate,
                                           l1_regularization_strength=1.0).minimize(cost)
    else:
        optimizer = tf.train.FtrlOptimizer(learning_rate=learning_rate,
                                           l1_regularization_strength=1.0).minimize(cost)
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838
    with tf.Session() as sess:

        sess.run(tf.global_variables_initializer())
        for epoch in range(num_epochs):
            cost_in_each_epoch = 0

            _, c = sess.run([optimizer, cost], feed_dict={
                            x: x_train, y: y_train})
            cost_in_each_epoch += c
        cost_in_each_epoch_2 = 0
        for epoch in range(num_epochs):

            _, c2 = sess.run([optimizer, cost], feed_dict={
                             x: x_test, y: y_test})
            cost_in_each_epoch_2 += c2
        correct_prediction = tf.equal(tf.argmax(y_, 1), tf.argmax(y, 1))
        cost_train = 0
        cost_test = 0
        for i in cost_in_each_epoch:
            cost_train += i
        for i in cost_in_each_epoch_2:
            cost_test += i
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        print("[============================]")
        if(r2_con_r1):
            print("Ronda 2 con Ronda 1 - Error en entrenamiento: ", cost_train)
            print("Ronda 2 con Ronda 1 -Precision en entrenamiento: ",
                  accuracy.eval({x: x_train, y: y_train}))
            print("[============================]")
            print("Ronda 2 con Ronda 1 - Error en pruebas: ", cost_test)
            print("Ronda 2 con Ronda 1 - Precision en pruebas: ",
                  accuracy.eval({x: x_test, y: y_test}))
        else:
            print("Ronda 2 - Error en entrenamiento: ", cost_train)
            print("Ronda 2 -Precision en entrenamiento: ",
                  accuracy.eval({x: x_train, y: y_train}))
            print("[============================]")
            print("Ronda 2 - Error en pruebas: ", cost_test)
            print("Ronda 2 - Precision en pruebas: ",
                  accuracy.eval({x: x_test, y: y_test}))

        predicciones_train = y_.eval({x: x_train})
        predicciones_test = y_.eval({x: x_test})
        sess.close()
    predicciones_train = convert_from_one_hot(predicciones_train)
    predicciones_test = convert_from_one_hot(predicciones_test)
    return predicciones_train, predicciones_test


<<<<<<< HEAD
def redes_neuronales(
        n_muestra,
        porcentaje_test,
        num_capas,
        unidades_por_capa,
        activacion):
=======
def redes_neuronales(n_muestra, porcentaje_test, num_capas, unidades_por_capa, activacion):
    global prefijo_csv
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838
    muestra = generar_muestra_pais(n_muestra)
    muestra_r1 = datos_r1_normalizados(muestra)
    muestra_r2 = datos_r2_normalizados(muestra)
    muestra_r2_r1 = datos_r2_con_r1_normalizados(muestra)
    train_r1, test_r1 = split_muestra(muestra_r1, porcentaje_test)
    train_r2, test_r2 = split_muestra(muestra_r2, porcentaje_test)
    train_r2_r1, test_r2_r1 = split_muestra(muestra_r2_r1, porcentaje_test)
    predicciones_train_r1, predicciones_test_r1 = red_neuronal_r1(
        train_r1, test_r1, num_capas, unidades_por_capa, activacion)
    predicciones_train_r2, predicciones_test_r2 = red_neuronal_r2(
        train_r2, test_r2, num_capas, unidades_por_capa, activacion)
    predicciones_train_r2_r1, predicciones_test_r2_r1 = red_neuronal_r1_r2(
        train_r2_r1, test_r2_r1, num_capas, unidades_por_capa, activacion)
    for i in range(0, len(train_r1)):
<<<<<<< HEAD
        muestra[i] += [True,
                       predicciones_train_r1[i] + 1,
                       predicciones_train_r2[i] + 1,
                       predicciones_train_r2_r1[i] + 1]
    for i in range(0, len(test_r1)):
        muestra[i + len(train_r1)] += [False,
                                       predicciones_test_r1[i] + 1,
                                       predicciones_test_r2[i] + 1,
                                       predicciones_test_r2_r1[i] + 1]
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
    dataframe.to_csv('resultados_redes_neuronales.csv', index=False)
=======
        muestra[i] += [True, predicciones_train_r1[i]+1,
                       predicciones_train_r2[i]+1, predicciones_train_r2_r1[i]+1]
    for i in range(0, len(test_r1)):
        muestra[i+len(train_r1)] += [False, predicciones_test_r1[i]+1,
                                     predicciones_test_r2[i]+1, predicciones_test_r2_r1[i]+1]
    dataframe = pd.DataFrame(muestra, columns=['poblacion_canton', 'superficie_canton', 'densidad_poblacion', 'urbano', 'sexo', 'dependencia_demografica', 'ocupa_vivienda', 'promedio_ocupantes', 'vivienda_buen_estado', 'vivienda_hacinada', 'alfabetismo', 'escolaridad_promedio', 'educacion_regular', 'fuera_fuerza_trabajo',
                                               'participacion_fuerza_trabajo', 'asegurado', 'extranjero', 'discapacidad', 'no_asegurado', 'porcentaje_jefatura_femenina', 'porcentaje_jefatura_compartida', 'edad', 'voto_primera_ronda', 'voto_segunda_ronda', 'es_entrenamiento', 'prediccion_r1', 'prediccion_r2', 'prediccion_r2_con_r1'])
    dataframe.to_csv(
        prefijo_csv+'resultados_redes_neuronales.csv', index=False)
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838


def red_neuronal_r1_r2(
        muestra,
        test,
        num_capas,
        unidades_por_capa,
        activacion):
    x_train = []
    x_test = []
    y_test = get_column(test, -1)
    y_train = get_column(muestra, -1)
    for i in range(0, len(y_train)):
        y_train[i] -= 1
    for i in range(0, len(y_test)):
        y_test[i] -= 1
    y_train = keras.utils.to_categorical(y_train, num_classes=4)
    y_test = keras.utils.to_categorical(y_test, num_classes=4)
    for i in range(0, len(muestra)):
        x_train += [muestra[i][:-1]]
    for i in range(0, len(test)):
        x_test += [test[i][:-1]]
    modelo = Sequential()
    modelo.add(
<<<<<<< HEAD
        Dense(
            units=unidades_por_capa[0],
            activation='relu',
            input_dim=23))
=======
        Dense(units=unidades_por_capa[0], activation='relu', input_dim=23))
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838
    for i in range(1, num_capas):
        modelo.add(Dense(units=unidades_por_capa[i], activation=activacion))
    modelo.add(Dense(4, activation='softmax'))
    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    modelo.compile(loss='categorical_crossentropy',
                   optimizer=sgd,
                   metrics=['accuracy'])
    x_train = np.array(x_train)
    y_train = np.array(y_train)
    x_test = np.array(x_test)
    y_test = np.array(y_test)
    modelo.fit(x_train, y_train,
               epochs=20,
               batch_size=128,
               validation_data=(x_test, y_test),
               shuffle=True,
               verbose=0)
    predicciones_train = modelo.predict(x_train,
                                        batch_size=128,
                                        verbose=0)
    predicciones_test = modelo.predict(x_test,
                                       batch_size=128,
                                       verbose=0)
    loss_acc_train = modelo.evaluate(x_train, y_train,
                                     batch_size=128,
                                     verbose=0)
    print("[============================]")
    print("Ronda 2 con Ronda 1 - Error en training: ", loss_acc_train[0])
    print("Ronda 2 con Ronda 1 - Precision en training: ", loss_acc_train[1])
    loss_acc_test = modelo.evaluate(x_test, y_test,
                                    batch_size=128,
                                    verbose=0)
    print("[============================]")
    print("Ronda 2 con Ronda 1 - Error en test: ", loss_acc_test[0])
    print("Ronda 2 con Ronda 1 - Precision en test: ", loss_acc_test[1])
    predicciones_train = convert_from_one_hot(predicciones_train)
    predicciones_test = convert_from_one_hot(predicciones_test)
    return predicciones_train, predicciones_test


def red_neuronal_r2(muestra, test, num_capas, unidades_por_capa, activacion):

    x_train = []
    y_train = get_column(muestra, -1)
    x_test = []
    y_test = get_column(test, -1)

    for i in range(0, len(y_train)):
        y_train[i] -= 1
    for i in range(0, len(y_test)):
        y_test[i] -= 1
    y_test = keras.utils.to_categorical(y_test, num_classes=4)
    y_train = keras.utils.to_categorical(y_train, num_classes=4)
    for i in range(0, len(muestra)):
        x_train += [muestra[i][:-1]]
    for i in range(0, len(test)):
        x_test += [test[i][:-1]]
    modelo = Sequential()
    modelo.add(
<<<<<<< HEAD
        Dense(
            units=unidades_por_capa[0],
            activation='relu',
            input_dim=22))
=======
        Dense(units=unidades_por_capa[0], activation='relu', input_dim=22))
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838
    for i in range(1, num_capas):
        modelo.add(Dense(units=unidades_por_capa[i], activation=activacion))
    modelo.add(Dense(4, activation='softmax'))
    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    modelo.compile(loss='categorical_crossentropy',
                   optimizer=sgd,
                   metrics=['accuracy'])
    x_train = np.array(x_train)
    y_train = np.array(y_train)
    x_test = np.array(x_test)
    y_test = np.array(y_test)
    modelo.fit(x_train, y_train,
               epochs=20,
               batch_size=128,
               validation_data=(x_test, y_test),
               verbose=0,
               shuffle=True
               )
    predicciones_train = modelo.predict(x_train, batch_size=128)
    predicciones_test = modelo.predict(x_test, batch_size=128)
    loss_acc_train = modelo.evaluate(x_train, y_train,
                                     batch_size=128,
                                     verbose=0)
    print("[============================]")
    print("Ronda 2 - Error en training: ", loss_acc_train[0])
    print("Ronda 2 - Precision en training: ", loss_acc_train[1])
    loss_acc_test = modelo.evaluate(x_test, y_test,
                                    batch_size=128,
                                    verbose=0)
    print("[============================]")
    print("Ronda 2 - Error en test: ", loss_acc_test[0])
    print("Ronda 2 - Precision en test: ", loss_acc_test[1])
    predicciones_train = convert_from_one_hot(predicciones_train)
    predicciones_test = convert_from_one_hot(predicciones_test)
    return predicciones_train, predicciones_test

# La longitud de la lista unidades_por_capa tiene que ser num_capas + 1


def red_neuronal_r1(muestra, test, num_capas, unidades_por_capa, activacion):
    x_train = []
    y_train = get_column(muestra, -1)
    x_test = []
    y_test = get_column(test, -1)
    for i in range(0, len(y_train)):
        y_train[i] -= 1
    for i in range(0, len(y_test)):
        y_test[i] -= 1
    y_train = keras.utils.to_categorical(y_train, num_classes=15)
    y_test = keras.utils.to_categorical(y_test, num_classes=15)
    for i in range(0, len(muestra)):
        x_train += [muestra[i][:-1]]
    for i in range(0, len(test)):
        x_test += [test[i][:-1]]
    modelo = Sequential()
    modelo.add(
<<<<<<< HEAD
        Dense(
            units=unidades_por_capa[0],
            activation='relu',
            input_dim=22))
=======
        Dense(units=unidades_por_capa[0], activation='relu', input_dim=22))
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838
    for i in range(0, num_capas):
        modelo.add(Dense(units=unidades_por_capa[i], activation=activacion))
    modelo.add(Dense(15, activation='softmax'))
    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    modelo.compile(loss='categorical_crossentropy',
                   optimizer=sgd,
                   metrics=['accuracy'])
    x_train = np.array(x_train)
    y_train = np.array(y_train)
    x_test = np.array(x_test)
    y_test = np.array(y_test)
    modelo.fit(x_train, y_train,
               epochs=20,
               batch_size=128,
               validation_data=(x_test, y_test),
               shuffle=True,
               verbose=0)
    predicciones_train = modelo.predict(x_train, batch_size=128)
    predicciones_test = modelo.predict(x_test, batch_size=128)
    loss_acc_train = modelo.evaluate(x_train, y_train,
                                     batch_size=128,
                                     verbose=0)
    print("[============================]")
    print("Ronda 1 - Error en training : ", loss_acc_train[0])
    print("Ronda 1 - Precision en training : ", loss_acc_train[1])
    loss_acc_test = modelo.evaluate(x_test, y_test,
                                    batch_size=128,
                                    verbose=0)
    print("[============================]")
    print("Ronda 1 - Error en test : ", loss_acc_test[0])
    print("Ronda 1 - Precision en test : ", loss_acc_test[1])

    predicciones_train = convert_from_one_hot(predicciones_train)
    predicciones_test = convert_from_one_hot(predicciones_test)
    return predicciones_train, predicciones_test


def convert_from_one_hot(one_hot_output):
    num_classes = len(one_hot_output[0])
    outputs = []
    for output in one_hot_output:
        max_output = 0
        max_output_index = 0
        for j in range(0, num_classes):
            if(output[j] >= max_output):
                max_output = output[j]
                max_output_index = j
        outputs += [max_output_index]
    return outputs


<<<<<<< HEAD
# Recibe la muestra generada por la funcion generar_muestra_pais o
# generar_muestra_provincia
=======
# Recibe la muestra generada por la funcion generar_muestra_pais o generar_muestra_provincia
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838
def datos_r1_normalizados(muestra):
    targets = get_column(muestra, -2)
    x_vector = []
    for i in range(0, len(muestra)):
        x_vector += [muestra[i][:-2]]
    standardScaler = StandardScaler()
    standardScaler.fit(x_vector)
    x_normalizado = standardScaler.transform(x_vector)
    return_list = []
    j = 0
    for i in x_normalizado:
        return_list += [np.append(i, targets[j])]
        j += 1
    return return_list


def datos_r2_normalizados(muestra):
    targets = get_column(muestra, -1)
    x_vector = []
    for i in range(0, len(muestra)):
        x_vector += [muestra[i][:-2]]
    standardScaler = StandardScaler()
    standardScaler.fit(x_vector)
    x_normalizado = standardScaler.transform(x_vector)
    return_list = []
    j = 0
    for i in x_normalizado:
        return_list += [np.append(i, targets[j])]
        j += 1
    return return_list


def datos_r2_con_r1_normalizados(muestra):
    targets = get_column(muestra, -1)
    x_vector = []
    for i in range(0, len(muestra)):
        x_vector += [muestra[i][:-1]]
    standardScaler = StandardScaler()
    standardScaler.fit(x_vector)
    x_normalizado = standardScaler.transform(x_vector)
    return_list = []
    j = 0
    for i in x_normalizado:
        return_list += [np.append(i, targets[j])]
        j += 1
    return return_list


def get_column(matrix, i):
    return [row[i] for row in matrix]


# kd_tree

"""
Estructura de los nodos que conforman el arbol
"""


class Node:

    def __init__(self, dimension, data):
<<<<<<< HEAD
        if(not isinstance(data, list) or not isinstance(dimension, int)):
=======
        if(type(data) is not list or type(dimension) is not int):
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838
            raise TypeError('El primer argumento debe ser una lista de' +
                            'y el segundo un numero entero')

        self.left = None
        self.right = None
        self.dimension = dimension
        self.data = data

    def insert_node(self, data, dimension):
<<<<<<< HEAD
        if(not isinstance(data, list) or not isinstance(dimension, int)):
=======
        if(type(data) is not list or type(dimension) is not int):
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838
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
<<<<<<< HEAD
        if(not isinstance(data, list) or not isinstance(isMinor, bool)):
=======
        if(type(data) is not list or type(isMinor) is not bool):
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838
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
<<<<<<< HEAD
            if(not isinstance(myData[i][0], list)):
                raise TypeError('El primer elemento de cada elemento'
                                'de la lista debe ser una lista')
            if(len(myData[i][0]) < 5):
                raise AttributeError(
                    'El primer elemento de cada elemento de la lista' +
                    'debe ser una lista de un tamaño mayor a 4')

    file = open('resultados_kd_tree.csv', 'w', newline='')
=======
            if(type(myData[i][0]) is not list):
                raise TypeError('El primer elemento de cada elemento'
                                'de la lista debe ser una lista')
            if(len(myData[i][0]) < 5):
                raise AttributeError('El primer elemento de cada elemento de la lista' +
                                     'debe ser una lista de un tamaño mayor a 4')

    global prefijo_csv
    file = open(prefijo_csv, 'w', newline='')
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838
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
<<<<<<< HEAD
    if(not isinstance(all_points, list) or not isinstance(new_point, list)):
        raise TypeError('El primer argumento debe ser una lista de listas' +
                        'y el segundo una lista')
    if(not isinstance(all_points[0], list)):
=======
    if(type(all_points) is not list or type(new_point) is not list):
        raise TypeError('El primer argumento debe ser una lista de listas' +
                        'y el segundo una lista')
    if(type(all_points[0]) is not list):
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838
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


# decision tree

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


<<<<<<< HEAD
def funcion_principal_arbol(
        numero_muestra,
        porcentaje_pruebas,
        umbral_poda,
        prefijo):
=======
def funcion_principal_arbol(numero_muestra, porcentaje_pruebas, umbral_poda, prefijo):
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838

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

    arbol_r1 = podar_arbol_aux_aux(arbol_r1, umbral_poda)
    arbol_r2 = podar_arbol_aux_aux(arbol_r2, umbral_poda)
    arbol_r2_r1 = podar_arbol_aux_aux(arbol_r2_r1, umbral_poda)
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


def main(argv):
    global prefijo_csv

    prefijo_csv = argv[1]
    numero_poblacion = int(argv[3])
    porcentaje_pruebas = float(argv[5])

    modelo = str(argv[6])

    if modelo == "--regresion-logistica":
        valor_l1 = float(argv[8])
        valor_l2 = float(argv[10])
        regresion_logistica(
<<<<<<< HEAD
            numero_poblacion,
            porcentaje_pruebas,
            valor_l1,
            valor_l2)
=======
            numero_poblacion, porcentaje_pruebas, valor_l1, valor_l2)
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838
    elif modelo == "--red-neuronal":
        numero_capas = float(argv[8])
        unidades_por_capa = float(argv[10])
        funcion_activacion = float(argv[12])

<<<<<<< HEAD
        redes_neuronales(
            numero_poblacion,
            porcentaje_pruebas,
            numero_capas,
            unidades_por_capa,
            funcion_activacion)
=======
        redes_neuronales(numero_poblacion, porcentaje_pruebas,
                         numero_capas, unidades_por_capa, funcion_activacion)
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838
    elif modelo == "--arbol":
        umbral_poda = float(argv[8])
        print(umbral_poda)
        funcion_principal_arbol(
<<<<<<< HEAD
            numero_poblacion,
            porcentaje_pruebas,
            umbral_poda,
            prefijo_csv)
=======
            numero_poblacion, porcentaje_pruebas, umbral_poda, prefijo_csv)
>>>>>>> 59cf2bab1a9dc74eb7b7df45f5ac848754c53838
    elif modelo == "--knn":
        valor_k = float(argv[8])

        kd_tree(numero_poblacion, valor_k, porcentaje_pruebas)
    elif modelo == "--svm":
        p_kernel = float(argv[8])
        support_vector_machines(numero_poblacion, porcentaje_pruebas, p_kernel)


if __name__ == "__main__":
    main(sys.argv[1:])
