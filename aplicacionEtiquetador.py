from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askdirectory
import tkinter as tk
from tkinter import messagebox
import os
import time
Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
# show an "Open" dialog box and return the path to the selected file
print("Select the folder of your images")
time.sleep(2)
directoryImages = str(askdirectory())
dir_list = os.listdir(directoryImages)
print("Select the folder where you want to save your label.txt")
time.sleep(2)
directory = str(askdirectory())
for img in dir_list:
    filename = "{direccion}/{imagen}".format(
        direccion=directoryImages, imagen=str(img))
    if filename[-3:] in {'jpg', 'jpeg', 'png'}:
        from Etiquetador import creadorEtiqueta
        Etiqueta = creadorEtiqueta(filename, directory)
        # EN caso de que no haya ninguna etiqueta en la imagen entonces se borra la imagen
        if Etiqueta == False:
            os.remove(filename)
    else:
        os.remove(filename)
