import g05 as _g05
import random as _random


def test_generar_muestra_pais1():
    _g05.cambiar_semilla(9000)
    _a = _g05.generar_muestra_pais(3)
    assert _a == [[254886.0,
                   388.42999267578125,
                   656.19546586545619,
                   'SI',
                   97.413118740947837,
                   'NO',
                   'NO',
                   3.4939262262081603,
                   'SIN VIVIENDA',
                   'SIN VIVIENDA',
                   'SI',
                   8.6859437968981688,
                   43.175358199431436,
                   'NO',
                   'SI',
                   'SI',
                   'SI',
                   'SI',
                   0,
                   0,
                   7.6120000000000001,
                   '20 a 24',
                   'RESTAURACION NACIONAL'],
                  [38453.0,
                   933.90997314453125,
                   41.174204265670745,
                   'SI',
                   98.970299078960991,
                   'NO',
                   'NO',
                   3.5,
                   'SIN VIVIENDA',
                   'SIN VIVIENDA',
                   'SI',
                   'SI',
                   6.6048256285482685,
                   'NO',
                   'SI',
                   'SI',
                   'SI',
                   'SI',
                   0,
                   0,
                   7.7724949999999993,
                   '25 a 29',
                   'ACCION CIUDADANA'],
                  [163745.0,
                   3347.97998046875,
                   48.908595916118387,
                   'SI',
                   100.42963633915565,
                   'NO',
                   'NO',
                   3.622425832851488,
                   'SIN VIVIENDA',
                   'SIN VIVIENDA',
                   'SI',
                   7.0192843085489276,
                   34.363464675079719,
                   'NO',
                   'SI',
                   'SI',
                   'SI',
                   'SI',
                   0,
                   0,
                   7.6101939999999999,
                   '20 a 24',
                   'RESTAURACION NACIONAL']]


def test_generar_muestra_pais2():
    _g05.cambiar_semilla(9000)
    _a = _g05.generar_muestra_pais(50)
    assert len(_a) == 50
    for i in range(50):
        assert len(_a[i]) == 23


def test_generar_muestra_pais3():
    _g05.cambiar_semilla(9000)
    _a = _g05.generar_muestra_pais("5")
    assert _a is None


def test_generar_muestra_pais4():
    _g05.cambiar_semilla(9000)
    _a = _g05.generar_muestra_pais(-4)
    assert _a is None


def test_generar_muestra_pais5():
    _g05.cambiar_semilla(9000)
    _a = _g05.generar_muestra_pais(3.3)
    assert _a is None


def test_generar_muestra_provincia1():
    _g05.cambiar_semilla(9000)
    _a = _g05.generar_muestra_provincia(5, "")
    assert _a is None


def test_generar_muestra_provincia2():
    _g05.cambiar_semilla(9000)
    _a = _g05.generar_muestra_provincia(5, "Alafuela")
    assert _a is None


def test_generar_muestra_provincia3():
    _g05.cambiar_semilla(9000)
    _a = _g05.generar_muestra_provincia("5", "ALAJUELA")
    assert _a is None


def test_generar_muestra_provincia4():
    _g05.cambiar_semilla(9000)
    _a = _g05.generar_muestra_provincia(-5, "ALAJUELA")
    assert _a is None


def test_generar_muestra_provincia5():
    _g05.cambiar_semilla(9000)
    _a = _g05.generar_muestra_provincia(3, "SAN JOSE")
    assert _a == [[288054.0,
                   44.619998931884773,
                   6455.7150805792835,
                   'SI',
                   89.905262949704309,
                   'NO',
                   'NO',
                   3.4999816856525405,
                   'SIN VIVIENDA',
                   'SIN VIVIENDA',
                   'SI',
                   9.8767649953085659,
                   46.246173674883423,
                   'NO',
                   'SI',
                   'SI',
                   'SI',
                   'SI',
                   0,
                   0,
                   6.8666589999999994,
                   '20 a 24',
                   'RESTAURACION NACIONAL'],
                  [288054.0,
                   44.619998931884773,
                   6455.7150805792835,
                   'SI',
                   89.905262949704309,
                   'NO',
                   'NO',
                   3.4999816856525405,
                   'SIN VIVIENDA',
                   'SIN VIVIENDA',
                   'SI',
                   'SI',
                   9.5269698148616691,
                   'NO',
                   'SI',
                   'SI',
                   'SI',
                   'SI',
                   0,
                   0,
                   6.8666589999999994,
                   '25 a 29',
                   'ACCION CIUDADANA'],
                  [288054.0,
                   44.619998931884773,
                   6455.7150805792835,
                   'SI',
                   89.905262949704309,
                   'NO',
                   'NO',
                   3.4999816856525405,
                   'SIN VIVIENDA',
                   'SIN VIVIENDA',
                   'SI',
                   9.8767649953085659,
                   46.246173674883423,
                   'NO',
                   'SI',
                   'SI',
                   'SI',
                   'SI',
                   0,
                   0,
                   6.8666589999999994,
                   '20 a 24',
                   'REPUBLICANO SOCIAL CRISTIANO']]


def test_generar_muestra_provincia6():
    _g05.cambiar_semilla(9000)
    _a = _g05.generar_muestra_provincia(50, "SAN JOSE")
    assert len(_a) == 50
    for i in range(50):
        assert len(_a[i]) == 23
