"""Dies ist das Modul "schachtler.py". Es stellt eine Funktion namens print_lvl()
bereit, die eine Liste mit beliebig vielen eingebetteten Listen ausgibt"""

def print_lvl(liste):
    """Diese Funktion erwartet ein positionelles Argument namens "liste", das eine
    beliebige Python-Liste (mit evntuellen eingebetteten Listen ist. Jedes Element der
    Liste wird (rekursiv) auf dem Bildschirm jeweils in einer eigenen Zeile ausgegeben."""
    for element in liste:
        if isinstance(element, list):
            print_lvl(element)
        else:
            print(element)    
