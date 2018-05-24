import sys
from tec.ic.ia.pc2.g05 import a_star_search, algortimo_genetico


def main(argv):
    
    largo_parametros = len(argv)
    
    bandera_tablero_inicial = ""
    archivo_txt = ""
    bandera_tipo_algoritmo = ""
    bandera_vision = ""
    cantidad_vision = 0
    bandera_zanahorias = ""
    cantidad_zanahorias = 0
    bandera_direccion_genetico = ""
    valor_direccion = ""
    bandera_individuos = ""
    cantidad_individuos = 0
    bandera_generaciones = ""
    cantidad_generaciones = 0
    bandera_mutacion_agregar = ""
    valor_mutacion_agregar = 20
    bandera_mutacion_cambiar = ""
    valor_mutacion_cambiar = 30
    bandera_mutacion_quitar = ""
    valor_mutacion_quitar = 15
    bandera_tipo_cruce = ""
    valor_tipo_cruce = 1
    
    
    if largo_parametros < 7:
        print("Número insuficiente de parámetros, se esperan mínimo 7")
        return 0
    else:
        bandera_tablero_inicial = argv[0]
        if bandera_tablero_inicial != "--tablero-inicial":
            print("Error de bandera de tablero, se esperaba '--tablero-inicial', pero se digitó: "+bandera_tablero_inicial)
            return 0
        else:
            archivo_txt = argv[1]
            bandera_tipo_algoritmo = argv[2]
            if bandera_tipo_algoritmo != "--a-estrella" and bandera_tipo_algoritmo != "--genetico":
                print("Error de bandera de tipo de algoritmo, se esperaba '--a-estrella' o '--genetico', pero se digitó: "+bandera_tipo_algoritmo)
                return 0
            else:
                if bandera_tipo_algoritmo == "--a-estrella":
                    if largo_parametros != 7:
                        print("Para el algoritmo de A* se deben pasar 7 parámetros")
                        return 0
                    else:
                        bandera_vision = argv[3]
                        if bandera_vision != "--vision":
                            print("Error de bandera de visión, se esperaba '--vision', pero se digitó: "+bandera_vision)
                            return 0
                        else:
                            cantidad_vision = int(argv[4])
                            bandera_zanahorias = argv[5]
                            if bandera_zanahorias != "--zanahorias":
                                print("Error de bandera de zanahorias, se esperaba '--zanahorias', pero se digitó: "+bandera_zanahorias)
                                return 0
                            else:
                                cantidad_zanahorias = int(argv[6])
                                a_star_search(archivo_txt, cantidad_vision, cantidad_zanahorias)
                elif bandera_tipo_algoritmo == "--genetico":
                    if largo_parametros < 8:
                        print("Para el algoritmo genético se deben pasar al menos 8 parámetros")
                        return 0
                    else:
                    
                        bandera_direccion_genetico = argv[3]
                        if bandera_direccion_genetico != "--derecha" and bandera_direccion_genetico != "--izquierda" and bandera_direccion_genetico != "--arriba" and bandera_direccion_genetico != "--abajo":
                            print("Error de bandera de dirección, se esperaba '--derecha', '--izquierda', '--arriba' o '--abajo', pero se digitó: "+bandera_direccion_genetico)
                            return 0
                        else:
                            valor_direccion = bandera_direccion_genetico[2:]
                            bandera_individuos = argv[4]
                            if bandera_individuos != "--individuos":
                                print("Error de bandera de individuos, se esperaba '--individuos', pero se digitó: "+bandera_individuos)
                                return 0
                            else:
                                cantidad_individuos = int(argv[5])
                                bandera_generaciones = argv[6]
                                if bandera_generaciones != "--generaciones":
                                    print("Error de bandera de generaciones, se esperaba '--generaciones', pero se digitó: "+bandera_generaciones)
                                    return 0
                                else:
                                    cantidad_generaciones = int(argv[7])
                                    if largo_parametros == 8:
                                            algortimo_genetico(archivo_txt, valor_direccion, cantidad_individuos, cantidad_generaciones, valor_mutacion_agregar, valor_mutacion_cambiar, valor_mutacion_quitar, valor_tipo_cruce)
                                            return 0
                                    else:
                                        
                                        bandera_mutacion_agregar = argv[8]
                                        if bandera_mutacion_agregar != "--mutacion-agregar":
                                            print("Error de bandera mutación agregar, se esperaba '--mutacion-agregar', pero se digitó: "+bandera_mutacion_agregar)
                                            return 0
                                        else:
                                            valor_mutacion_agregar = float(argv[9])
                                            if largo_parametros == 10:
                                                algortimo_genetico(archivo_txt, valor_direccion, cantidad_individuos, cantidad_generaciones, valor_mutacion_agregar, valor_mutacion_cambiar, valor_mutacion_quitar, valor_tipo_cruce)
                                                return 0

                                            else:    
                                                bandera_mutacion_cambiar = argv[10]
                                                if bandera_mutacion_cambiar != "--mutacion-cambiar":
                                                    print("Error de bandera mutación cambiar, se esperaba '--mutacion-cambiar', pero se digitó: "+bandera_mutacion_cambiar)
                                                    return 0
                                                else:
                                                    valor_mutacion_cambiar = float(argv[11])
                                                    if largo_parametros == 12:
                                                        algortimo_genetico(archivo_txt, valor_direccion, cantidad_individuos, cantidad_generaciones, valor_mutacion_agregar, valor_mutacion_cambiar, valor_mutacion_quitar, valor_tipo_cruce)
                                                        return 0
                                                    else:
                                                        bandera_mutacion_quitar = argv[12]
                                                        if bandera_mutacion_quitar != "--mutacion-quitar":
                                                            print("Error de bandera mutación quitar, se esperaba '--mutacion-quitar', pero se digitó: "+bandera_mutacion_quitar)
                                                            return 0
                                                        else:
                                                            valor_mutacion_quitar = float(argv[13])
                                                            suma_porcentajes = valor_mutacion_agregar + valor_mutacion_cambiar + valor_mutacion_quitar
                                                            if suma_porcentajes > 100:
                                                                print("La suma de los valores de mutación debe ser menor o igual a 100")
                                                                return 0
                                                            else:
                                                                if largo_parametros == 14:
                                                                    algortimo_genetico(archivo_txt, valor_direccion, cantidad_individuos, cantidad_generaciones, valor_mutacion_agregar, valor_mutacion_cambiar, valor_mutacion_quitar, valor_tipo_cruce)
                                                                    return 0
                                                                else:                                        
                                                                    bandera_tipo_cruce = argv[14]
                                                                    if bandera_tipo_cruce != "--tipo-cruce":
                                                                        print("Error bandera tipo cruce, se esperaba '--tipo-cruce', pero se digitó: "+ bandera_tipo_cruce)
                                                                        return 0
                                                                    else:
                                                                        valor_tipo_cruce = int(argv[15])
                                                                        if valor_tipo_cruce != 0 and valor_tipo_cruce != 1:
                                                                            print("El valor del tipo de cruce debe ser 0 o 1")
                                                                            return 0
                                                                        else:
                                                                            algortimo_genetico(archivo_txt, valor_direccion, cantidad_individuos, cantidad_generaciones, valor_mutacion_agregar, valor_mutacion_cambiar, valor_mutacion_quitar, valor_tipo_cruce)
                                                        

                                    

                                    #llamar función de karina

if __name__ == "__main__":
    main(sys.argv[1:])
