from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
import tkinter as tk
from tkinter import messagebox
import time
Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
# show an "Open" dialog box and return the path to the selected file
print("Select your image/video")
time.sleep(2)
filename = str(askopenfilename())
print("Select the folder where you want to save your file")
time.sleep(2)
directory = str(askdirectory())
# Para conocer si desea optimizar o no la aplicacion
Optimizacion = False
root = tk.Tk()
root.withdraw()
MsgBox = tk.messagebox.askquestion(
    'Optimización', 'Do you want to optimize this process? Be aware that this can affect image quality')
if MsgBox == 'yes':
    Optimizacion = True
# Para conocer el tiempo de demora del programa
start_time = time.time()
if filename[-3:] in {'jpg', 'jpeg', 'png'}:
    from identificadorPlanta import crearImagen
    crearImagen(filename, directory, Optimizacion)
elif filename[-3:] in {'mp4', 'mov', 'wmv', 'flv', 'avi', 'mkv', 'webm'}:
    import identificadorVideo
    identificadorVideo.crearVideo(filename, directory, Optimizacion)
# Imprime el tiempo de demora
print("--- %s seconds ---" % (time.time() - start_time))
