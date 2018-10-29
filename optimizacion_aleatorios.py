import numpy as np
import re
import random
import time
def numeros_y_simbolos(restriccion):
    indice = restriccion.find(">=")
    condicion = ">="
    if indice == -1:
        indice = restriccion.find("<=")
        condicion = "<="
    #se utiliza el indice obtenido para indexar y partir a trozos las cadenas de restricciones
    resultado = float(restriccion[indice+3:])
    trozo_cadena = restriccion[0:indice].split()
    #se divide la cadena y se convierten todos los coeficientes numericos a flotantes
    coeficientes = np.array(list(map(float,trozo_cadena[0:len(trozo_cadena)])))
    #se guardan los signos de suma y resta en una sublista
    #nota: no es necesario
    return (coeficientes,resultado,condicion)


def evaluar_limites(lista_restricciones,n_restricciones,variables):
    #el argumento de lista_restricciones contiene los coeficientes, signos e igualdades
    limites = np.zeros((n_restricciones,variables))
    for x in range(n_restricciones):
        for y in range(variables):
            #se itera sobre la cantidad de restricciones y los coefiecientes de cada variable
            if lista_restricciones[x][0][y] != 0:
                limites[x,y] = lista_restricciones[x][1]/lista_restricciones[x][0][y]
            else:
                limites[x,y] = 0     
    
    maximos = np.zeros(variables)
    minimos = np.zeros(variables)
 
    for x in range(variables):
        maximos[x] = np.max(limites[:,x])
        logic_index = limites[:,x]<0
        if limites[logic_index,x] != []:
            minimos[x] = np.max(limites[logic_index,x])
        else:    
            minimos[x] = np.min(limites[:,x])
    return maximos,minimos

def generar_aleatorios(tam_poblacion,variables,max_lims,min_lims):
    matriz_poblacion = np.zeros((tam_poblacion,variables))
    if len(list(set(max_lims)))==1:
        condicion =1
    else:
        condicion =-1
    for x in range(tam_poblacion):
        for y in range(variables):
            #print(min_lims[y],max_lims[y])
            #if condicion == 1:
            matriz_poblacion[x][y] = random.randint(min_lims[y],max_lims[y])
            #else:
                #matriz_poblacion[x][y] = random.random()*max_lims[y]
            #    matriz_poblacion[x][y] = random.uniform(min_lims[y],max_lims[y])
    return matriz_poblacion


def evaluar_aleatorios(matriz_aleatorios,funcion_objetivo,lista_valores,n_restricciones,variables,tam_poblacion):
    nueva_mat = np.zeros((tam_poblacion,2+variables+n_restricciones))
    for x in range(tam_poblacion):
        nueva_mat[x][0] = x
        for y in range(1,2+variables+n_restricciones):
            #se guardan valores aleatorios de las variables
            if y <= variables:
                nueva_mat[x][y] = matriz_aleatorios[x][y-1]
            #se verifica que los valores generados de las variables cumplan con las condiciones de desigualdad
            elif y < 1+variables+n_restricciones:
                if lista_valores[y-1-variables][-1] == "<=":
                    if np.sum(nueva_mat[x,1:variables+1]*lista_valores[y-1-variables][0]) <= lista_valores[y-1-variables][1]:
                        nueva_mat[x][y] = 1
                    else:
                        nueva_mat[x][y] = 0
                elif lista_valores[y-1-variables][-1] == ">=":
                    if np.sum(nueva_mat[x,1:variables+1]*lista_valores[y-1-variables][0]) >= lista_valores[y-1-variables][1]:
                        nueva_mat[x][y] = 1
                    else:
                        nueva_mat[x][y] = 0
            else:
                #si se cumplen todas las condiciones
                if np.sum(nueva_mat[x,1+variables:1+variables+n_restricciones]) == len(lista_valores):
                    nueva_mat[x,y] = np.sum(nueva_mat[x,1:variables+1]*funcion_objetivo)
                else:
                    nueva_mat[x,y] = -1
    #print(nueva_mat)
    return nueva_mat

def encuentra_maximo(tabla,variables):
        indice_maximo = tabla[:,tabla.shape[1]-1].argmax()
        
        valor_maximo = tabla[indice_maximo][-1]
        if valor_maximo !=-1:
            print("coeficientes de variables: ",*np.round(tabla[indice_maximo,1:variables+1],2))
            print("valor maximo: ",valor_maximo)
        else:
            print("no se encontro maximo")
        
def encuentra_minimo(tabla,variables):
    try:
        indices = tabla[:,tabla.shape[1]-1] != -1
        nueva = tabla[indices,:]
        minimo = tabla[indices,tabla.shape[1]-1].argmin()
        print("coeficientes de variables: ",*np.round(nueva[minimo,1:variables+1],2))
        print("valor minimo",nueva[minimo][-1])
    except:
        print("no se encontro minimo")




variables = int(input())
funcion_objetivo = np.array(list(map(float,input().split())))
restricciones = []
num_restricciones = int(input())
lista_valores = []
for x in range(num_restricciones):
    restricciones.append(input())
    lista_valores.append(numeros_y_simbolos(restricciones[-1]))
poblacion = 500000

#print(lista_valores)


inicio = time.time()
#limites = evaluar_limites(lista_valores,num_restricciones,variables)
max_lims,min_lims = evaluar_limites(lista_valores,num_restricciones,variables)
#random.seed(2)
#print(limites)

            



for x in range(10):
    mat_alet = generar_aleatorios(poblacion,variables,max_lims,min_lims)
    alea = evaluar_aleatorios(mat_alet,funcion_objetivo,lista_valores,num_restricciones,variables,poblacion)
    encuentra_maximo(alea,variables)
    encuentra_minimo(alea,variables)
    print("\n")


fin = time.time()


print("tiempo de ejecucion: ",fin-inicio)

