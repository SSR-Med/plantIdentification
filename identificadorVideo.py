import cv2
from graphviz import render
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import matplotlib.patches as patches
import os
import identificadorPlanta
# De video a imagen


def videoImagen(video_path):
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    # Imagenes a guardar
    imagenes_cargadas = []
    while success:
        img_resized = identificadorPlanta.image_resize(image, 200, 200)
        imagenes_cargadas.append(img_resized)
        success, image = vidcap.read()
    return imagenes_cargadas

# Cambiar luz imagenes


def luzImagen(listaImagen):
    brillo_aumentado = []
    for img in listaImagen:
        a = 1
        gamma = 0.75
        # cv2.cvtColor(img, cv2.COLOR_BGR2XYZ)
        # Aplicar la transformación corrección gamma sobre la imagen de entrada
        brillo = identificadorPlanta.apply_f_on_rgb(cv2.cvtColor(
            img, cv2.COLOR_BGR2RGB), identificadorPlanta.gamma_correction, [a, gamma])
        brillo_aumentado.append(brillo)
    return brillo_aumentado

# Identificar los pixeles verdes


def verdeAjustar(brillo):
    verdeAjustado = []
    for img_rgb in brillo:
        verdeAjustado.append(identificadorPlanta.aislarVerde(img_rgb))
    return verdeAjustado

# Creación de los grafos


def crearGrafos(verde):
    grafos = []
    for elemento in verde:
        grafos.append(identificadorPlanta.creacionGrafos(elemento))
    return grafos

# Eliminar los componentes con x cantidad menor de nodos


def eliminarComponente(grafos, verde):
    for i in range(len(verde)):
        grafos[i] = identificadorPlanta.eliminarComponentes(
            grafos[i], verde[i])

# Lista de componentes como lista y no como set


def listComponent(grafo):
    listaComponente = []
    for i in range(len(grafo)):
        listaComponente.append(identificadorPlanta.listaComponente(grafo[i]))
    return listaComponente

# Función para encontrar cuadrado de cada imagen


def encontrarCuadradoVideo(grafos, listaComponente):
    for i in range(len(grafos)):
        grafos[i] = identificadorPlanta.encontrarCuadrados(
            grafos[i], listaComponente[i])
# Guardar las imagenes para realizar el video


def consolidarImagenVideo(grafoVideo, imagenVideo, nombreVideo, direccionVideo, dimensionVideo):
    newPath = '{direccionArchivo}/Video'.format(
        direccionArchivo=direccionVideo)
    if not os.path.exists(newPath):
        os.makedirs(newPath)
    for i in range(len(grafoVideo)):
        fig, ax1 = plt.subplots(1, 1, figsize=(10, 8))
        Elemento = nx.connected_components(grafoVideo[i])
        for elemento in Elemento:
            lista = list(elemento)
            # Se obtienen las coordenadas de cada componente
            listaCoordenadas = [grafoVideo[i].nodes[x]
                                ['position'] for x in lista]
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
        ax1.imshow(cv2.cvtColor(
            imagenVideo[i], cv2.COLOR_BGR2RGB), aspect="auto")
        plt.close(fig)
        nombre = os.path.basename(nombreVideo)
        nombre = str(nombre) + str(i)
        direccionNuevoArchivo = '{direccionArchivo}/Video/{nombreArchivo}.png'.format(
            nombreArchivo=nombre, direccionArchivo=direccionVideo)
        fig.savefig(direccionNuevoArchivo)
        # Ahora a reescalar el archivo
        img_resized = cv2.imread(direccionNuevoArchivo, cv2.IMREAD_COLOR)
        img_resized = identificadorPlanta.image_resize(
            img_resized, dimensionVideo[1], dimensionVideo[0])
        img_resized = cv2.detailEnhance(img_resized, sigma_s=10, sigma_r=0.15)
        cv2.imwrite(direccionNuevoArchivo, img_resized)
    return '{direccionArchivo}/Video'.format(direccionArchivo=direccionVideo)

# Creacion del video (se realiza el .mp4)


def renderizarVideo(grafoVideo, direccionImagenes, nombreArchivo, direccionVideo):
    img_array = []
    for i in range(len(grafoVideo)):
        filename = direccionImagenes+("/Imagen{numero}.png".format(numero=i))
        img = cv2.imread(filename)
        img_array.append(img)
    size = (img.shape[1], img.shape[0])
    nombreArchivo = os.path.basename(nombreArchivo)
    nombreArchivo = os.path.splitext(nombreArchivo)[0]
    out = cv2.VideoWriter(direccionVideo+'/Modificado{nombre}.avi'.format(
        nombre=nombreArchivo), cv2.VideoWriter_fourcc(*'DIVX'), 15, size)
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()


def crearVideo(video_path, direccion):
    # Obtener resolución del video
    vid = cv2.VideoCapture(video_path)
    dim = (int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT)),
           int(vid.get(cv2.CAP_PROP_FRAME_WIDTH)))
    imagenes_cargadas = videoImagen(video_path)
    brillo_aumentado = luzImagen(imagenes_cargadas)
    verdeAjustado = verdeAjustar(brillo_aumentado)
    grafos = crearGrafos(verdeAjustado)
    eliminarComponente(grafos, verdeAjustado)
    listaComponentes = listComponent(grafos)
    encontrarCuadradoVideo(grafos, listaComponentes)
    direccionImagenes = consolidarImagenVideo(
        grafos, imagenes_cargadas, 'Imagen', direccion, dim)
    renderizarVideo(grafos, direccionImagenes, video_path, direccion)
    # Eliminar carpeta de videos
    import shutil
    shutil.rmtree(direccionImagenes)
