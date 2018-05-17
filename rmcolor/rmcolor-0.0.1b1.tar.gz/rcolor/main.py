#!/usr/bin/env python3
"""Pinta las letras de la terminal de colore"""
from colores import Colores as c
from os import system,name
import sys
import time



print(c.BOLD,c.CYAN,"""

  /$$$$$$            /$$                           /$$$$$$$$                    /$$    
 /$$__  $$          | $$                          |__  $$__/                   | $$    
| $$  \__/  /$$$$$$ | $$  /$$$$$$   /$$$$$$          | $$  /$$$$$$  /$$   /$$ /$$$$$$  
| $$       /$$__  $$| $$ /$$__  $$ /$$__  $$         | $$ /$$__  $$|  $$ /$$/|_  $$_/  
| $$      | $$  \ $$| $$| $$  \ $$| $$  \__/         | $$| $$$$$$$$ \  $$$$/   | $$    
| $$    $$| $$  | $$| $$| $$  | $$| $$               | $$| $$_____/  >$$  $$   | $$ /$$
|  $$$$$$/|  $$$$$$/| $$|  $$$$$$/| $$               | $$|  $$$$$$$ /$$/\  $$  |  $$$$/
 \______/  \______/ |__/ \______/ |__/               |__/ \_______/|__/  \__/   \___/                            
                             
                                                                                 
""",c.ENDC)

entradas = []
while True:
    print("Escribe 'exit' para salir")
    print("Todo lo que escribas se te mostrara al salir del programa con el color elejido")
    print("""
    Colores disponibles:
    {r}Rojo{er} {v}Verde{ev} {am}Amarillo{eam} {az}Azul{eaz} {b}Blanco{eb}
    {ma}Magenta, morado o purpura{ema} {n}Negro{en} {c}Cyan{ec} 
    """.format(
        r=c.ROJO,er=c.ENDC,v=c.VERDE,ev=c.ENDC,am=c.AMARILLO,eam=c.ENDC,az=c.AZUL,
        eaz=c.ENDC,ma=c.MAGENTA,ema=c.ENDC,n=c.NEGRO,en=c.ENDC,c=c.CYAN,ec=c.ENDC,
        b=c.BLANCO,eb=c.ENDC
    ))
    color = input("Que color quieres usar para escribir el siguiente texto?\n>> ")
    text = input("Escribe un nuevo texto.\n>> ")

    if color.lower() in ('rojo','red'):
        entradas.append("{cb} {c} {txt} {ce}".format(cb=c.BOLD,c=c.ROJO,txt=text,ce=c.ENDC))
    
    elif color.lower() in ('amarillo','yellow'):
        entradas.append("{cb} {c} {txt} {ce}".format(cb=c.BOLD,c=c.AMARILLO,txt=text,ce=c.ENDC))

    elif color.lower() in ('cian','cyan'):
        entradas.append("{cb} {c} {txt} {ce}".format(cb=c.BOLD,c=c.CYAN,txt=text,ce=c.ENDC))
    
    elif color.lower() in ('azul','blue'):
        entradas.append("{cb} {c} {txt} {ce}".format(cb=c.BOLD,c=c.AZUL,txt=text,ce=c.ENDC))
        
    elif color.lower() in ('verde','green'):
        entradas.append("{cb} {c} {txt} {ce}".format(cb=c.BOLD,c=c.VERDE,txt=text,ce=c.ENDC))
    
    elif color.lower() in ('negro','black'):
        entradas.append("{cb} {c} {txt} {ce}".format(cb=c.BOLD,c=c.NEGRO,txt=text,ce=c.ENDC))

    elif color.lower() in ('magenta','morado', 'purple', 'purpura'):
        entradas.append("{cb} {c} {txt} {ce}".format(cb=c.BOLD,c=c.MAGENTA,txt=text,ce=c.ENDC))

    elif color.lower() in ('blanco','white'):
        entradas.append("{cb} {c} {txt} {ce}".format(cb=c.BOLD,c=c.BLANCO,txt=text,ce=c.ENDC))

    elif color.lower() in ('exit', 'salir', 'quit'):
        print(c.VERDE, "Saliendo del programa...",c.ENDC)
        time.sleep(1.5)
        print(c.CURSIVA,"\n","="*70,c.ENDC,"\n")
        
        if len(entradas) > 0:
            for entrada in entradas:
                print(entrada)
        else:
            print(c.BOLD,c.CURSIVA,c.ROJO,"\t\tNo se registro ninguna entrada...!",c.ENDC)

        print(c.CURSIVA,"\n","="*70,c.ENDC)
        break
    
    else:
        print(c.BOLD, c.ROJO, "Opcion desconocida intenta de nuevo!", c.ENDC)
        time.sleep(1.5)
        if name == 'nt':
            system('cls')
        else:
            system('clear')

