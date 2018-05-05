from tec.ic.ia.pc1.g07 import generar_muestra_pais, generar_muestra_provincia
import numpy as np
from keras.utils import to_categorical


def generar_muestras(tipo_muestras, poblacion, porcentaje_pruebas, normalization):
    # Removes non-wanted attributes depending on prediction type and creates samples
    samples = create_samples(tipo_muestras, poblacion)
    print("\nNormalizing samples")
    result = []
    for i in range (0,3):
        tipo_prediccion = i
        if normalization == "total_con_one_hot_encoding":
            normalized_samples, gt = normalization_total_con_one_hot_encoding(
                samples[i], i)
        elif normalization == "total_sin_one_hot_encoding":
            normalized_samples, gt = normalization_total_sin_one_hot_encoding(
                samples[i], i)
        elif normalization == "semi":
            normalized_samples, gt = normalization_semi(samples[i], i)
        elif normalization == "svm":
            normalized_samples, gt = normalization_svm(samples[i],i)
        partition = poblacion - int(poblacion * porcentaje_pruebas / 100)
        result.append([normalized_samples[:partition], gt[:partition], normalized_samples[partition:], gt[partition:],samples[i]])
    return result

def create_samples(tipo_muestras, poblacion):
    samples = []
    pre_samples = None
    if tipo_muestras == "PAIS":
        pre_samples = generar_muestra_pais(poblacion)
    elif tipo_muestras == "SAN_JOSE":
        pre_samples = generar_muestra_provincia(poblacion, "SAN JOSE")
    else:
        pre_samples = generar_muestra_provincia(poblacion, tipo_muestras)
    for k in range (0,3):
        samples_set = []
        indexes = [1, 2, 3, 4, 5, 9, 10, 15, 19, 21,
                   24, 25, 27, 30, 31, 32, 37, 38, 40, 44]
        if k == 0:
            indexes.extend([7, 56])
        elif k == 1:
            indexes.extend([6, 55])
        for i in range(0, poblacion):
            sample = []
            for j in range(0, 57):
                if j not in indexes:
                    sample.append(pre_samples[i][j])
            samples_set.append(sample)
        samples.append(samples_set)
    return samples


def normalization_total_con_one_hot_encoding(samples, tipo_prediccion):
    num_classes = 4
    es_r2 = False
    discrete_indexes = [0, 4, 6, 7, 10, 11, 12, 13, 18, 19, 20,
                        21, 23, 26, 27, 28, 29, 30, 31, 32, 33, 34]  # 34 es el GT
    if tipo_prediccion == 2:
        discrete_indexes = [0, 5, 7, 8, 11, 12, 13, 14, 19, 20, 21, 22,
                            24, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]  # 36 es el GT
    elif tipo_prediccion == 0:
        num_classes = 15
    elif tipo_prediccion == 1:
        es_r2 = True
    normalized_samples, gt = configure_samples(
        samples, discrete_indexes, es_r2=es_r2)
    encoded = to_categorical(gt, num_classes=num_classes)
    return normalized_samples, encoded


def normalization_total_sin_one_hot_encoding(samples, tipo_prediccion):
    es_r2 = False
    if tipo_prediccion == 2:
        discrete_indexes = [0, 5, 7, 8, 11, 12, 13, 14, 19, 20, 21, 22,
                            24, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]  # 36 es el GT
    else:
        discrete_indexes = [0, 4, 6, 7, 10, 11, 12, 13, 18, 19, 20,
                            21, 23, 26, 27, 28, 29, 30, 31, 32, 33, 34]  # 34 es el GT
        if tipo_prediccion == 1:
            es_r2 = True
    normalized_samples, gt = configure_samples(
        samples, discrete_indexes, es_r2=es_r2)
    return normalized_samples.tolist(), gt.tolist()

# normaliza lo que sea continuo


def normalization_semi(samples, tipo_prediccion):
    if tipo_prediccion == 2:
        discrete_indexes = [0, 5, 7, 8, 11, 12, 13, 14, 19, 20, 21, 22,
                            24, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]  # 36 es el GT
    else:
        discrete_indexes = [0, 4, 6, 7, 10, 11, 12, 13, 18, 19, 20,
                            21, 23, 26, 27, 28, 29, 30, 31, 32, 33, 34]  # 34 es el GT

    normalized_samples, gt = configure_samples(
        samples, discrete_indexes, es_semi=True)
    for i in range(len(normalized_samples)):
        for j in range(len(normalized_samples[i])):
            if normalized_samples[i][j].replace('.', '', 1).isdigit():
                normalized_samples[i][j] = float(normalized_samples[i][j])
    return normalized_samples, gt

def normalization_svm(samples, tipo_prediccion):
    es_r2 = False
    if tipo_prediccion == 2:
        discrete_indexes = [0, 5, 7, 8, 11, 12, 13, 14, 19, 20, 21, 22,
                            24, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]  # 36 es el GT
    else:
        discrete_indexes = [0, 4, 6, 7, 10, 11, 12, 13, 18, 19, 20,
                            21, 23, 26, 27, 28, 29, 30, 31, 32, 33, 34]  # 34 es el GT
        if tipo_prediccion == 1:
            es_r2 = True
    normalized_samples, gt = configure_samples_svm(
        samples, discrete_indexes, es_r2=es_r2)
    return normalized_samples, gt

# Configures sample values (normalizes them and changes them to numbers if they are discrete)


def configure_samples(samples, discrete_indexes, es_semi=False, es_r2=False):
    np_samples_by_attr = np.array(samples).T.tolist()

    discrete = 0
    for i in range(len(np_samples_by_attr)):
        if i in discrete_indexes and not es_semi:
            for j in range(len(np_samples_by_attr[i])):
                np_samples_by_attr[i][j] = convert_discrete_value(
                    discrete, np_samples_by_attr[i][j], es_r2)
            discrete += 1

        if i not in discrete_indexes:
            np_samples_by_attr[i] = [float(i) for i in np_samples_by_attr[i]]
            np_samples_by_attr[i] = normalize_min_max(np_samples_by_attr[i])
    if not es_semi:
        data = np.array(np_samples_by_attr[:-1], dtype=np.float32)
        gt = np.array(np_samples_by_attr[-1])
        return data.T, gt
    else:
        data = np.array(np_samples_by_attr[:-1])
        gt = np.array(np_samples_by_attr[-1])
        return data.T.tolist(), gt.tolist()

def configure_samples_svm(samples, discrete_indexes, es_r2=False):
    np_samples_by_attr = np.array(samples).T.tolist()

    discrete = 0
    for i in range(len(np_samples_by_attr)):
        if i in discrete_indexes:
            for j in range(len(np_samples_by_attr[i])):
                np_samples_by_attr[i][j] = convert_discrete_value(
                    discrete, np_samples_by_attr[i][j], es_r2)
            discrete += 1

    data = np.array(np_samples_by_attr[:-1], dtype=np.float32)
    gt = np.array(np_samples_by_attr[-1])
    return data.T, gt



def normalize_min_max(values):
    min_v = min(values)
    max_v = max(values)
    for v in range(len(values)):
        values[v] = (values[v] - min_v) / (max_v-min_v)
    return values

# Receives a list of values and normalizes them


def normalize_z_score(values):
    np_values = np.array(values)
    standard_deviation = np.std(np_values).tolist()
    mean = np.mean(np_values).tolist()
    for i in range(0, len(values)):
        if standard_deviation == 0:
            values[i] = values[i] - mean
        else:
            values[i] = (values[i] - mean)/standard_deviation
    return values

# Changes a value to int if it is discrete


def convert_discrete_value(index, value, es_r2):
    discrete_all = [['SAN JOSE', 'ALAJUELA', 'CARTAGO', 'HEREDIA', 'GUANACASTE', 'PUNTARENAS', 'LIMON'],
                    ['urbana', 'no urbana'],
                    ['mujer', 'hombre'],
                    ['15 a 19', '20 a 24', '25 a 29', '30 a 34', '35 a 39', '40 a 44', '45 a 49', '50 a 54',
                        '55 a 59', '60 a 64', '65 a 69', '70 a 74', '75 a 79', '80 a 84', '85 y más'],
                    ['vivienda en buen estado', 'vivienda en mal estado'],
                    ['vivienda hacinada', 'vivienda no hacinada'],
                    ['ningun año', 'primaria incompleta', 'primaria completa',
                        'secundaria incompleta', 'secundaria completa', 'superior'],
                    ['alfabeta', 'no alfabeta'],
                    ['dentro de fuerza', 'fuera de fuerza'],
                    ['sector primario', 'sector secundario', 'sector terciario',
                        'pensionado', 'rentista', 'estudia', 'oficios domesticos', 'otros'],
                    ['nacido en extranjero', 'no nacido en extranjero'],
                    ['discapacidad', 'sin discapacidad'],
                    ['asegurado', 'no asegurado'],
                    ['jefatura femenina', 'jefatura masculina', 'jefatura compartida'],
                    ['no telefono celular', 'telefono celular'],
                    ['no telefono residencial', 'telefono residencial'],
                    ['no computadora', 'computadora'],
                    ['no internet', 'internet'],
                    ['no electricidad', 'electricidad'],
                    ['no servicio sanitario', 'servicio sanitario'],
                    ['no agua', 'agua'],
                    ['ACCESIBILIDAD SIN EXCLUSION', 'ACCION CIUDADANA', 'ALIANZA DEMOCRATA CRISTIANA', 'DE LOS TRABAJADORES', 'FRENTE AMPLIO', 'INTEGRACION NACIONAL', 'LIBERACION NACIONAL',
                        'MOVIMIENTO LIBERTARIO', 'NUEVA GENERACION', 'RENOVACION COSTARRICENSE', 'REPUBLICANO SOCIAL CRISTIANO', 'RESTAURACION NACIONAL', 'UNIDAD SOCIAL CRISTIANA', 'NULOS', 'BLANCOS'],
                    ['ACCION CIUDADANA', 'RESTAURACION NACIONAL', 'NULOS', 'BLANCOS']]
    if es_r2 and index == 21:
        return float(discrete_all[index+1].index(value))
    return float(discrete_all[index].index(value))
