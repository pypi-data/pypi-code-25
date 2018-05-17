"""
Modulo para dar color al texto de la consola
"""


class Colores:
    # COLORES
    MAGENTA = '\033[35m'
    AZUL = '\033[34m'
    VERDE = '\033[32m'
    AMARILLO = '\033[33m'
    ROJO = '\033[31m'
    CYAN = '\033[36m'
    BLANCO = '\033[37m'
    NEGRO = '\033[30m'

    # EFECTOS O ESTILOS
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DEBIL = '\033[2m'
    CURSIVA = '\033[3m'
    SUBRAYADO = '\033[4m'
    INVERSO = '\033[5m'
    OCULTO = '\033[6m'
    TACHADO = '\033[7m'

    # FONDOS
    FONDO_BLANCO = '\033[47m'
    FONDO_CYAN = '\033[46m'
    FONDO_MAGENTA = '\033[45m'
    FONDO_AZUL = '\033[44m'
    FONDO_AMARILLO = '\033[43m'
    FONDO_VERDE = '\033[42m'
    FONDO_ROJO = '\033[41m'
    FONDO_NEGRO = '\033[40m'
