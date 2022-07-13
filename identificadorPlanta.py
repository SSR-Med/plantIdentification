import cv2
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import matplotlib.patches as patches
import os
# Funciones para aplicar cambio en luz
# Definir la función para aplicar la transformación sobre la imagen RGB

# Realizado por:
# Javier de Jesus Silva
# Santiago Salazar Ramirez


def apply_f_on_rgb(img, f, args):

    # Crear una matriz de ceros del tamaño de la imagen de entrada
    res = np.zeros(img.shape, np.uint8)
    # Aplicar la transformación f sobre cada canal del espacio de color RGB
    res[:, :, 0] = f(img[:, :, 0], *args)
    res[:, :, 1] = f(img[:, :, 1], *args)
    res[:, :, 2] = f(img[:, :, 2], *args)

    return res

# Definir la función de transformación de la imagen (corrección gamma)


def gamma_correction(img, a, gamma):

    # Crear copia de la imagen tipo flotante dada la normalización
    img_copy = img.copy().astype(np.float32)/255.0
    # La función corrección gamma es de la forma ax^gamma, donde x es la imagen de entrada
    res_gamma = cv2.pow(img_copy, gamma)
    res = cv2.multiply(res_gamma, a)

    # Asegurar que la los datos queden entre 0 y 255 y sean uint8
    res[res < 0] = 0
    res = res*255.0
    res[res > 255] = 255

    res = res.astype(np.uint8)

    return res

# Función encargada de aislar el verde de la imagen


def aislarVerde(img_rgb):
    rc, gc, bc = img_rgb[:, :, 0], img_rgb[:, :, 1], img_rgb[:, :, 2]
    for r in range(gc.shape[0]):
        for c in range(gc.shape[1]):
            # Aquí se hace una diferencia entre el canal verde y el canal azul y rojo: si este canal verde es mayor a los otros se selecciona (también tiene que ser mayor a 100)
            if int(gc[r][c]) > 0.75*int(rc[r][c]) + 0.45*int(bc[r][c]) and int(gc[r][c]) > 100:
                pass
            else:
                # En caso contrario el pixel se vuelve blanco
                gc[r][c] = 0
    return gc

# Creación del grafo para la imagen verde


def creacionGrafos(imagenVerde):
    G = nx.Graph()  # Se inicializa el grafo
    for r in range(imagenVerde.shape[0]):  # r se refiere a row
        for c in range(imagenVerde.shape[1]):  # c se refiere a column
            if imagenVerde[r][c] > 0:  # R
                # Numero_Fila * numeroFilas
                posicionNodo = (imagenVerde.shape[1]*r)+c
                # Para resumir se añade la posición a cada nodo, para no tener problema a la hora de usar las coordenadas
                G.add_node(posicionNodo, position=[r, c])
                if c > 0:  # Si la columna es mayor a 0, para ir haciendo las aristas con los elementos atras de él
                    # Cada vez que se pone que mayor a 0 significa si no es un pixel blanco, porque la idea es hacer adyacencia con los pixeles de colores
                    if imagenVerde[r][c-1] > 0:
                        G.add_edge(posicionNodo, posicionNodo-1)
                if r > 0:  # Ahora si la fila es mayor a 0, para ir haciendo las aristas con: los elementos detras de él, los elementos detrás de él pero a la izquierda y los elementos detrás de él pero a la derecha
                    if imagenVerde[r-1][c] > 0:
                        G.add_edge(posicionNodo, posicionNodo -
                                   (imagenVerde.shape[1]))
                    if c > 0:
                        if imagenVerde[r-1][c-1] > 0:
                            G.add_edge(posicionNodo, posicionNodo -
                                       (imagenVerde.shape[1])-1)
                    if c < imagenVerde.shape[1]-1:
                        if imagenVerde[r-1][c+1] > 0:
                            G.add_edge(posicionNodo, posicionNodo -
                                       (imagenVerde.shape[1])+1)
    return G

# Eliminación de componentes con una cantidad inferior a 50 nodos


def eliminarComponentes(grafo, imagen):
    listaEliminar = []  # Además de poner el pixel a 0 se quita del grafo, para no tenerlo ahí
    Elemento = nx.connected_components(grafo)  # Los componentes del grafo
    for elemento in Elemento:  # Hora de iterar sobre los componentes del grafo
        if len(elemento) < 30:  # Esta es la condición para eliminar el componente y poner sus pixeles en 0. Si el componente tiene menos de 2000 nodos entonces se quita
            # El elemento es un set, toca pasarlo a lista
            lista = list(elemento)
            # Como este se va a eliminar entonces lo metemos a la listaEliminar
            listaEliminar.append(lista)
            # Vamos a transformar la lista (la lista de nodos) a las coordenadas, que es su atributi
            listaCoordenadas = [grafo.nodes[x]['position'] for x in lista]
            for coordenada in listaCoordenadas:  # Vamos a iterar sobre la lista de coordenadas para poder poner ese pixel como un pixel blanco, no verde
                imagen[coordenada[0]][coordenada[1]] = 0
    for elemento in listaEliminar:  # Para cada componente que sea menor a 2000 se le quitan sus nodos al grafo
        for nodo in elemento:
            grafo.remove_node(nodo)
    return grafo

# Crear listas de componentes del grafo


def listaComponente(grafo):
    listaComponente = []
    Elemento = nx.connected_components(grafo)
    for elemento in Elemento:
        listaComponente.append(list(elemento))
    return listaComponente

# La idea de la intersección entre cuadrados es identificar si el punto de un cuadrado está dentro de otro cuadrado. Así es que se dice que existe una intersección o contención del cuadrado


def interseccionCuadrados(cuadrado1, cuadrado2):
    # cuadrado: [ (),(),(),()]
    for ve in cuadrado1:
        # ¿El cuadrado 1 se intersecta o está dentro del cuadrado 2?
        if cuadrado2[3][0] > ve[0] > cuadrado2[0][0] and cuadrado2[0][1] < ve[1] < cuadrado2[1][1]:
            return True
    for ve in cuadrado2:
        # ¿El cuadrado 2 se intersecta o está dentro del cuadrado 1?
        if cuadrado1[3][0] > ve[0] > cuadrado1[0][0] and cuadrado1[0][1] < ve[1] < cuadrado1[1][1]:
            return True
    return False

# Encontrar los cuadrados para cada componente


def encontrarCuadrados(grafo, listaComponent):
    # La lista de coordenadas de cada componente del grafo
    listaCoordenadasComponente = []
    for elemento in listaComponent:
        listaCoordenadasComponente.append(
            [grafo.nodes[x]['position'] for x in elemento])  # Se agregan las coordenadas
    listaPuntos = []
    for componente in listaCoordenadasComponente:
        # Se hallan las posiciones de: Arriba, Abajo, Izquierda y derecha del cuadrado.
        posArriba = min(componente, key=lambda x: x[0])[0]
        posAbajo = max(componente, key=lambda x: x[0])[0]
        posIzquierda = min(componente, key=lambda x: x[1])[1]
        posDerecha = max(componente, key=lambda x: x[1])[1]
        # Los vertices del cuadrado
        vtl = (posArriba, posIzquierda)
        vtr = (posArriba, posDerecha)
        vbl = (posAbajo, posIzquierda)
        vbr = (posAbajo, posDerecha)
        listaPuntos.append([vtl, vtr, vbl, vbr])
    for j in range(len(listaComponent)-1):
        for k in range(j+1, len(listaComponent)):
            # Se revisan entre los componentes si existe una intersección entre cuadrados
            intersectados = interseccionCuadrados(
                listaPuntos[j], listaPuntos[k])
            if intersectados == True:
                # En caso de intersección se une el primer nodo del componente1 y el primer nodo del componente2 -> Ahora sólo hay 1 un componente, se unen los cuadrados
                grafo.add_edge(listaComponent[j][0], listaComponent[k][0])
    return grafo


# Mostrar el cuadrado rojo alrededor de la imagen

def consolidarImagen(grafo, imagen, nombre, direccion, dimensionOriginal):
    fig, ax1 = plt.subplots(1, 1, figsize=(10, 8))
    Elemento = nx.connected_components(grafo)
    for elemento in Elemento:
        lista = list(elemento)
        # Se obtienen las coordenadas de cada componente
        listaCoordenadas = [grafo.nodes[x]['position'] for x in lista]
        # Se obtienen las posiciones más arriba, más abajo
        posArriba = min(listaCoordenadas, key=lambda x: x[0])[0]
        posAbajo = max(listaCoordenadas, key=lambda x: x[0])[0]
        posIzquierda = min(listaCoordenadas, key=lambda x: x[1])[
            1]  # Más izquierda, más derecha
        posDerecha = max(listaCoordenadas, key=lambda x: x[1])[1]
        # Esto para crear un cuadrado alrededor del componente (planta)
        rect = patches.Rectangle((posIzquierda, posAbajo), posDerecha-posIzquierda,
                                 posArriba-posAbajo, linewidth=1, edgecolor='r', facecolor='none')
        ax1.add_patch(rect)  # Se añade al plot
    ax1.axis('off')
    ax1.imshow(cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB), aspect="auto")
    plt.close(fig)
    nombre = os.path.basename(nombre)
    direccionNuevoArchivo = '{direccionArchivo}/{nombreArchivo}Modified.png'.format(
        nombreArchivo=nombre, direccionArchivo=direccion)
    fig.savefig(direccionNuevoArchivo)
    # Ahora a reescalar el archivo
    img_resized = cv2.imread(direccionNuevoArchivo, cv2.IMREAD_COLOR)
    img_resized = cv2.resize(
        img_resized, dimensionOriginal, interpolation=cv2.INTER_AREA)
    cv2.imwrite(direccionNuevoArchivo, img_resized)


def crearImagen(img_path, direccion):
    # Se lee la imagen
    nombrePath = img_path[:-4]
    img_pathOriginal = cv2.imread(img_path, cv2.IMREAD_COLOR)
    # Original dimensions
    dim = (img_pathOriginal.shape[1], img_pathOriginal.shape[0])
    img_pathOriginal = cv2.resize(
        img_pathOriginal, (200, 200), interpolation=cv2.INTER_AREA)
    img_path = img_pathOriginal.copy()
    # Se aplica la transformación de gamma
    a = 1
    gamma = 0.75
    # cv2.cvtColor(img, cv2.COLOR_BGR2XYZ)
    # Aplicar la transformación corrección gamma sobre la imagen de entrada
    img_path = apply_f_on_rgb(cv2.cvtColor(
        img_path, cv2.COLOR_BGR2RGB), gamma_correction, [a, gamma])
    verdeAislado = aislarVerde(img_path)
    grafo = creacionGrafos(verdeAislado)
    # Ahora el grafo actualizado
    grafo = eliminarComponentes(grafo, verdeAislado)
    listaComponent = listaComponente(grafo)
    grafo = encontrarCuadrados(grafo, listaComponent)
    consolidarImagen(grafo, img_pathOriginal, nombrePath, direccion, dim)
