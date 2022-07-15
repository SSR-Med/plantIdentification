from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
import tkinter as tk
from tkinter import messagebox
import os
import time
Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
# show an "Open" dialog box and return the path to the selected file
print("Select your image/video")
time.sleep(2)
filename = str(askopenfilename())
print("Select the folder where you want to save your file")
time.sleep(2)
directory = str(askdirectory())
if filename[-3:] in {'jpg', 'jpeg', 'png'}:
    from Etiquetador import creadorEtiqueta
    Etiqueta = creadorEtiqueta(filename, directory)
    # EN caso de que no haya ninguna etiqueta en la imagen entonces se borra la imagen
    if Etiqueta == False:
        os.remove(filename)
