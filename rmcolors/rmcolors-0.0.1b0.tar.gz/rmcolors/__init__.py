"""Paquete main de rmcolors
   Argumentos: on => inicia el programa, tambien se puede usar start
"""

# __all__ = ['main', 'colores']
from rmcolors.main import main
import sys


def error():
    print(colores.Colores.VERDE,
        colores.Colores.BOLD,
        "Argumentos conocidos: 'on' 'start'",
        colores.Colores.ENDC    
    )
    print(colores.Colores.ROJO,
          colores.Colores.BOLD,
          "\nDebes pasar un argumento para ejecutar el programa",
          "\nEste error se muestra porque no has pasado ningun argumento",
          "\no has pasado mas de los necesarios.",
          colores.Colores.ENDC    
    )
    sys.exit(1)    

if len(sys.argv) == 1:
    error()

elif len(sys.argv) > 2:
    error()

elif sys.argv[1] in ('on','start'):
    main()
else:
    print(colores.Colores.VERDE,
        colores.Colores.BOLD,
        "Argumentos conocidos: 'on' 'start'",
        colores.Colores.ENDC    
    )
    

