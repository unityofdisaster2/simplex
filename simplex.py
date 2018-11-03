"""
script para calcular maximos y minimos mediante el metodo simplex dual
las entradas del programa son las siguientes:

#variables
funcion objetivo
#restricciones
r1 x1 x2 ... xn <= c1
r2 x1 x2 ... xn <= c2
...
rn r1 x1 x2 ... xn <= cn
operacion

ejemplo:

2
0.10 0.07
4
1 1 <= 500
1 0 <= 300
0 1 >= 100
-1 1 <= 0
min

"""


import numpy as  np
import time

#funcion para descomponer cadena en un arreglo que contenga coeficientes numericos
#valor final y simbolo de desigualdad
def numeros_y_simbolos(restriccion):
    indice = restriccion.find(">=")
    condicion = ">="
    if indice == -1:
        indice = restriccion.find("<=")
        condicion = "<="
    #se utiliza el indice obtenido para ordenar los valores de la cadena(restriccion) en distintas variables
    resultado = float(restriccion[indice+3:])
    trozo_cadena = restriccion[0:indice].split()
    #se divide la cadena y se convierten todos los coeficientes numericos a flotantes
    coeficientes = np.array(list(map(float,trozo_cadena[0:len(trozo_cadena)])))
    #se guardan los signos de suma y resta en una sublista
    return (coeficientes,resultado,condicion)


#funcion para crear todas las tablas y vectores necesarios para optimizar con metodo simplex
def crear_tabla_max(fo,restricciones):
    #constante
    cj = np.zeros(len(fo)+len(restricciones))
    #se crea diccionario para mantener ubicadas las variables por sus indices
    diccionario_cj = {}
    for x in range(len(cj)):
        if x < len(fo):
            diccionario_cj[x] = 'x'+str(x+1)
        else:
            diccionario_cj[x] = 'h'+str(x-len(fo)+1)
    columna_cj = np.zeros(len(restricciones))
    diccionario_fila = {}
    for x in range(len(columna_cj)):
        diccionario_fila[x] = 'h'+str(x+1)
    
    #se crea tabla principal donde se realizaran todos los calculos
    cj[0:len(fo)] = fo
    tabla = np.zeros((len(restricciones)+2,len(fo)+len(restricciones)+1))
    tabla[-1][:len(cj)] = cj
    #se manejan las desigualdades para dejar todo de la forma <= para evitar
    #crear variables artificiales 
    for x in range(len(restricciones)):
        if restricciones[x][-1] == ">=":
            #se 'niegan' coeficientes de la desigualdad para equilibrar las ecuaciones
            tabla[x][0:len(fo)] = -restricciones[x][0]
            tabla[x][-1] = -restricciones[x][-2]
        else:
            tabla[x][0:len(fo)] = restricciones[x][0]
            tabla[x][-1] = restricciones[x][-2]
        #se crean coeficientes de variables de holgura
        tabla[x][len(fo)+x] = 1
    return cj,columna_cj,tabla,diccionario_cj,diccionario_fila








#funcion para mostrar en formato de tabla los cambios que hay en los valores 
def imprime_formato(tabla,cj,columna_cj,variables):
    for x in range(len(cj)+1):
        if x == 0:
            print("{:<10}".format("cj"),end=" ")
        if x+1< variables+1:
            print("{:<10}".format("x"+str(x+1)),end=" ")
        elif x < len(cj):
            print("{:<10}".format(" h"+str(x-variables+1)),end="")
        else:
            print(" fo")
    for x in range(tabla.shape[0]):
        if x < len(columna_cj):
            print("{:<10}".format(diccionario_fila[x]),end=" ")
        elif x == len(columna_cj):
            print("{:<10}".format("zj"),end=" ")
        elif x == len(columna_cj)+1:
            print("{:<10}".format("cj-zj"),end=" ")
        else:
            print("{:<10}".format(" "),end=" ")
        for y in range(tabla.shape[1]):
            
            print("{:<10}".format(tabla[x,y]),end=" ")
        print("\n")
    print("\n"*4)

def pivote_max(tabla,positivos,variables,diccionario_cj,diccionario_fila):
    """
    si hay algun valor negativo en la columna de la funcion objetivo
    se aplica metodo simplex 3 y se elige un pivote de tal forma que se trate
    de eliminar dicho valor negativo
    """
    if not positivos:
        #se busca indice del valor mas negativo de la funcion objetivo
        fila = np.argmin(tabla[:len(restricciones),-1])
        #se divide la fila obtenida con la fila cj-zj
        aux = tabla[fila,:tabla.shape[1]-1]/tabla[-1,:tabla.shape[1]-1]
        #se busca el indice del valor mas negativo
        columna = np.nanargmin(aux)
        diccionario_fila[fila] = diccionario_cj[columna]
        return fila,columna
    else:
        """
        si no hay negativos en la columna de la funcion objetivo se aplica
        el metodo simplex 2
        """
        #se busca valor mas positivo de cj-zj
        columna = np.argmax(tabla[-1])
        #se divide columna de funcion objetivo sobre columna cj-zj
        aux = tabla[:,-1]/tabla[:,columna]
        #se agrega esta linea para manejar problemas presentados con valores infinitos obtenidos por
        #cocientes que arrojan valores infinitos
        aux [aux == np.inf] = -np.inf
        contador = 0

        #se busca la fila que haya dado menor valor positivo
        min_pos = np.max(aux[:-2])
        fila = np.argmax(aux[:-2])
        #se realiza indexado logico para identificar cuando la fila obtenida unicamente
        #cuenta con valores negativos
        logic_index = aux[:-2] <=0
        for x in aux[:-2]:
            if logic_index.all():
                if x >= 0:
                    if contador == 0:
                        if x<min_pos:
                            min_pos = x
                            fila = contador
                    else:
                        if x<=min_pos:
                            min_pos = x
                            fila = contador                   
            else:
                if x > 0:
                    if contador == 0:
                        if x<min_pos:
                            min_pos = x
                            fila = contador
                    else:
                        if x<=min_pos:
                            min_pos = x
                            fila = contador                   
            contador += 1
            #se actualiza diccionario cj con las nuevas variables
        diccionario_fila[fila] = diccionario_cj[columna]
        return fila,columna
    
def pivote_min(tabla,positivos,variables,diccionario_cj,diccionario_fila):
    if not positivos:
        #similar al caso de maximizacion
        fila = np.argmin(tabla[:len(restricciones),-1])
        aux = tabla[fila,:tabla.shape[1]-1]/tabla[-1,:tabla.shape[1]-1]
        #se manejan valores para evitar problemas con infinitos y ceros a la hora de buscar un maximo en la columna
        aux[aux==np.inf] = np.nan
        aux[aux==-np.inf] = np.nan
        aux[aux == 0] = np.nan
        columna = np.nanargmax(aux)
        diccionario_fila[fila] = diccionario_cj[columna]
        return fila,columna
    else:
        columna = np.argmin(tabla[-1])
        aux = tabla[:,-1]/tabla[:,columna]
        contador = 0
        min_pos = np.max(aux)
        fila = np.argmax(aux)
        for x in aux[:-2]:
            if x >= 0:
                if contador == 0:                       
                    if x<min_pos:
                        min_pos = x
                        fila = contador
                else:
                    if x<=min_pos:
                        min_pos = x
                        fila = contador                    
            contador += 1
        diccionario_fila[fila] = diccionario_cj[columna]
        return fila,columna



def maximizar(cj,columna_cj,tabla,variables):
    converge = tabla[-1] > 0
    #se itera hasta que no haya valores positivos en fila cj-zj
    while(converge.any()):
        #se hace indexado logico para identificar si hay valores negativos en funcion objetivo
        condicion = tabla[:-2,-1]>= 0
        fila,columna = pivote_max(tabla,condicion.all(),variables,diccionario_cj,diccionario_fila)
        #se actualiza multiplicador de la columna cj 
        columna_cj[fila] = cj[columna]
        #se divide la fila entre el pivote
        tabla[fila] = tabla[fila]/tabla[fila,columna]
        #ciclo para hacer ceros en la columna del pivote
        for x in range(tabla.shape[0]-2):
            if x != fila:
                tabla[x]= tabla[x,columna]*-tabla[fila] + tabla[x]
        
        arreglo_auxiliar = np.zeros(tabla[0].shape)
        for x in range(tabla.shape[0]-2):
            #se multiplican cj por cada fila y se suman para conformar a zj
            arreglo_auxiliar+= columna_cj[x]*tabla[x]
        
        #se actualizan filas zj y cj-zj
        tabla[tabla.shape[0]-2] = arreglo_auxiliar
        
        tabla[tabla.shape[0]-1][:-1] = cj-arreglo_auxiliar[:-1]
        imprime_formato(tabla,cj,columna_cj,variables)
        converge = tabla[-1] > 0
    return tabla,diccionario_fila


def minimizar(cj,columna_cj,tabla,variables):
    converge = np.array([True,True])
    while(converge.any()):
        condicion = tabla[:-2,-1] >= 0
        if not condicion.all():
            fila,columna = pivote_min(tabla,condicion.all(),variables,diccionario_cj,diccionario_fila)
            columna_cj[fila] = cj[columna]
            #se divide la fila entre el pivote
            tabla[fila] = tabla[fila]/tabla[fila,columna]
            
            #ciclo para hacer ceros en la columna del pivote
            for x in range(tabla.shape[0]-2):
                if x != fila:
                    tabla[x]= tabla[x,columna]*-tabla[fila] + tabla[x]
                    #tabla[x] = tabla[x]*tabla[fila,columna] + tabla[x]
            arreglo_auxiliar = np.zeros(tabla[0].shape)
            for x in range(tabla.shape[0]-2):
                arreglo_auxiliar+= columna_cj[x]*tabla[x]
            
            #se actualizan filas zj y cj-zj
            tabla[tabla.shape[0]-2] = arreglo_auxiliar
            tabla[tabla.shape[0]-1][:-1] = cj-arreglo_auxiliar[:-1]
            imprime_formato(tabla,cj,columna_cj,variables)
            #converge = tabla[-1] < 0
        else:   
            converge = tabla[-1] < 0
            if converge.any():
                fila,columna = pivote_min(tabla,condicion.all(),variables,diccionario_cj,diccionario_fila)
                columna_cj[fila] = cj[columna]
                #se divide la fila entre el pivote
                tabla[fila] = tabla[fila]/tabla[fila,columna]
                
                #ciclo para hacer ceros en la columna del pivote
                for x in range(tabla.shape[0]-2):
                    if x != fila:
                        tabla[x]= tabla[x,columna]*-tabla[fila] + tabla[x]
                        #tabla[x] = tabla[x]*tabla[fila,columna] + tabla[x]
                arreglo_auxiliar = np.zeros(tabla[0].shape)
                for x in range(tabla.shape[0]-2):
                    arreglo_auxiliar+= columna_cj[x]*tabla[x]
                
                #se actualizan filas zj y cj-zj
                tabla[tabla.shape[0]-2] = arreglo_auxiliar
                tabla[tabla.shape[0]-1][:-1] = cj-arreglo_auxiliar[:-1]
                imprime_formato(tabla,cj,columna_cj,variables)            
        #imprime_formato(tabla,cj,columna_cj,variables)
    return tabla,diccionario_fila

def muestra_resultados(tabla,etiquetas):
    objetivo = tabla[:-1,-1]
    for x in etiquetas.keys():
        print(etiquetas[x]," = ",objetivo[x])
    print("z = ",objetivo[-1])


#funcion principal
if __name__ == "__main__":
    #no mostrar errores provocados por generar valores nan o inf
    np.warnings.filterwarnings('ignore')
    variables = int(input('ingrese numero de variables: '))
    funcion_objetivo = np.array(list(map(float,input('ingrese la funcion objetivo: ').split())))
    restricciones = []
    num_restricciones = int(input('ingrese numero de restricciones: '))
    lista_valores = []
    
    for x in range(num_restricciones):
        print('r'+str(x)+': ',end="")
        restricciones.append(input())
        lista_valores.append(numeros_y_simbolos(restricciones[-1]))
    

    accion = input("indique accion a realizar:")
    inicio = time.time()
    if accion == "max":
        print('\n'*2)
        cj,columna_cj,tabla,diccionario_cj,diccionario_fila = crear_tabla_max(funcion_objetivo,lista_valores)
        imprime_formato(tabla,cj,columna_cj,variables)
        tabla,etiquetas = maximizar(cj,columna_cj,tabla,variables)
        muestra_resultados(tabla,etiquetas)
    elif accion == "min":
        print('\n'*2)
        cj,columna_cj,tabla,diccionario_cj,diccionario_fila = crear_tabla_max(funcion_objetivo,lista_valores)
        imprime_formato(tabla,cj,columna_cj,variables)
        tabla,etiquetas = minimizar(cj,columna_cj,tabla,variables)
        muestra_resultados(tabla,etiquetas)
    fin = time.time()


    print("tiempo de ejecucion: ",fin-inicio)
    