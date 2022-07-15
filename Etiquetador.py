import identificadorPlanta
import cv2
import networkx as nx
import os
# Transforma las coordenadas de una caja de una imagen
# a lo requerido para yoloV5
# Se pide (Xmin,Xmax,Ymin,Ymax)
# Tambien se pide el tamaño (width,height) de la imagen


def convert(size, box):
    dw = 1./size[0]
    dh = 1./size[1]
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x, y, w, h)


def creadorTxt(grafo, dimensiones, direccion, nombre):
    # Crear el archivo txt
    nombre = os.path.basename(nombre)
    direccionNuevoArchivo = '{direccionArchivo}/{nombreArchivo}.txt'.format(
        nombreArchivo=nombre, direccionArchivo=direccion)
    f = open(direccionNuevoArchivo, "w+")
    Elemento = nx.connected_components(grafo)
    # Se agrega lineas para ir escribiendo en el archivo txt
    linea = 1
    cantidadComponentes = nx.number_connected_components(grafo)
    for elemento in Elemento:
        lista = list(elemento)
        # Se obtienen las coordenadas de cada componente
        listaCoordenadas = [grafo.nodes[x]['position'] for x in lista]
        # Se obtienen las posiciones más arriba, más abajo
        posMinY = min(listaCoordenadas, key=lambda x: x[0])[0]
        posMaxY = max(listaCoordenadas, key=lambda x: x[0])[0]
        posMinX = min(listaCoordenadas, key=lambda x: x[1])[
            1]  # Más izquierda, más derecha
        posMaxX = max(listaCoordenadas, key=lambda x: x[1])[1]
        posicionYolo = convert(
            dimensiones, (posMinX, posMaxX, posMinY, posMaxY))
        posicionYolo = [str(x) for x in posicionYolo]
        # Para evitar el salto de linea
        if linea != cantidadComponentes:
            stringTxt = '0 ' + ' '.join(posicionYolo) + "\n"
        else:
            stringTxt = '0 ' + ' '.join(posicionYolo)
        f.write(stringTxt)
        linea += 1
    f.close()


# Creación de funciones para realizar el identificador por imagen


def creadorEtiqueta(img_path, direccion):
    nombrePath = img_path[:-4]
    img_pathOriginal = cv2.imread(img_path, cv2.IMREAD_COLOR)
    img_path = img_pathOriginal.copy()
    dim = (img_pathOriginal.shape[1], img_pathOriginal.shape[0])
    # Se aplica la transformación de gamma
    a = 1
    gamma = 0.75
    # cv2.cvtColor(img, cv2.COLOR_BGR2XYZ)
    # Aplicar la transformación corrección gamma sobre la imagen de entrada
    img_path = identificadorPlanta.apply_f_on_rgb(cv2.cvtColor(
        img_path, cv2.COLOR_BGR2RGB), identificadorPlanta.gamma_correction, [a, gamma])
    verdeAislado = identificadorPlanta.aislarVerde(img_path)
    grafo = identificadorPlanta.creacionGrafos(verdeAislado)
    # En caso de que no haya identificado nada -> Que no siga trabajando
    if nx.number_connected_components(grafo) == 0:
        return False  # Significa que no identificó una planta, entonces se va a eliminar esta imagen
    # Ahora el grafo actualizado
    grafo = identificadorPlanta.eliminarComponentes(grafo, verdeAislado, False)
    listaComponent = identificadorPlanta.listaComponente(grafo)
    grafo = identificadorPlanta.encontrarCuadrados(grafo, listaComponent)
    creadorTxt(grafo, dim, direccion, nombrePath)
