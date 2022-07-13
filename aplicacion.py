from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
from identificadorPlanta import crearImagen
from tkinter.filedialog import askdirectory
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
    crearImagen(filename, directory)
elif filename[-3:] in {'mp4', 'mov', 'wmv', 'flv', 'avi', 'mkv', 'webm'}:
    pass
