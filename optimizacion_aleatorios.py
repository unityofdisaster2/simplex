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
    return (coeficientes,resultado,condicion)


def evaluar_limites(lista_restricciones,n_restricciones,variables,negatividad):
    #el argumento de lista_restricciones contiene los coeficientes, signos e igualdades
    limites = np.zeros((n_restricciones,variables))
    #se itera sobre la cantidad de restricciones y los coefiecientes de cada variable
    for x in range(n_restricciones):
        for y in range(variables):
            if lista_restricciones[x][0][y] != 0:
                limites[x,y] = lista_restricciones[x][1]/lista_restricciones[x][0][y]
            else:
                limites[x,y] = 0     
    
    maximos = np.zeros(variables)
    minimos = np.zeros(variables)
    print(limites)
    for x in range(variables):
        maximos[x] = np.max(limites[:,x])
        #se verifica cuantos numeros negativos hay en los minimos
        if negatividad == 'si':
            minimos[x] = 0
        else:
            logic_index = limites[:,x]<=0
            cumplen = limites[logic_index,x] 
            if cumplen != []:
                minimos[x] = np.max(limites[logic_index,x])
            else:    
                minimos[x] = np.min(limites[:,x])
    print(maximos,minimos)
    return maximos,minimos

def generar_aleatorios(tam_poblacion,variables,max_lims,min_lims):
    matriz_poblacion = np.zeros((tam_poblacion,variables))
    for x in range(tam_poblacion):
        #matriz_poblacion[x] = min_lims+(max_lims-min_lims)*np.random.random((3,))
        for y in range(variables):
            matriz_poblacion[x][y] = random.randint(min_lims[y],max_lims[y])
            #matriz_poblacion[x][y] = random.random()*max_lims[y]
            #matriz_poblacion[x][y] = random.uniform(min_lims[y],max_lims[y])
    return matriz_poblacion


def evaluar_aleatorios(matriz_aleatorios,funcion_objetivo,lista_valores,n_restricciones,variables,tam_poblacion):
    nueva_mat = np.zeros((tam_poblacion,2+variables+n_restricciones))
    for x in range(tam_poblacion):
        nueva_mat[x][0] = x
        #se guardan valores aleatorios de las variables
        nueva_mat[x,1:variables+1] = matriz_aleatorios[x]
        for y in range(1+variables,2+variables+n_restricciones): 
            if y < 1+variables+n_restricciones:
                if lista_valores[y-1-variables][-1] == "<=":
                    if np.dot(nueva_mat[x,1:variables+1],lista_valores[y-1-variables][0]) <= lista_valores[y-1-variables][1]:
                        nueva_mat[x][y] = 1
                    else:
                        nueva_mat[x][y] = 0
                elif lista_valores[y-1-variables][-1] == ">=":
                    if np.dot(nueva_mat[x,1:variables+1],lista_valores[y-1-variables][0]) >= lista_valores[y-1-variables][1]:
                        nueva_mat[x][y] = 1
                    else:
                        nueva_mat[x][y] = 0
            else:
                #si se cumplen todas las condiciones
                if np.sum(nueva_mat[x,1+variables:1+variables+n_restricciones]) == len(lista_valores):
                    nueva_mat[x,y] = np.dot(nueva_mat[x,1:variables+1],funcion_objetivo)
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




if __name__ == "__main__":
    variables = int(input('ingrese numero de variables: '))
    funcion_objetivo = np.array(list(map(float,input('ingrese la funcion objetivo: ').split())))
    restricciones = []
    negatividad = input('asumir no negatividad: ')
    num_restricciones = int(input('ingrese numero de restricciones: '))
    lista_valores = []
    for x in range(num_restricciones):
        print('r'+str(x)+': ',end="")
        restricciones.append(input())
        lista_valores.append(numeros_y_simbolos(restricciones[-1]))
    poblacion = 1000000

    inicio = time.time()

    max_lims,min_lims = evaluar_limites(lista_valores,num_restricciones,variables,negatividad)


    for x in range(10):
        mat_alet = generar_aleatorios(poblacion,variables,max_lims,min_lims)
        alea = evaluar_aleatorios(mat_alet,funcion_objetivo,lista_valores,num_restricciones,variables,poblacion)
        encuentra_maximo(alea,variables)
        encuentra_minimo(alea,variables)
        print("\n")


    fin = time.time()


    print("tiempo de ejecucion: ",fin-inicio)
