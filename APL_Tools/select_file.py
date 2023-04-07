import tkinter
from tkinter import filedialog

def getfilename(filetoget):

    filetypewanted = filetoget

    windowtext = 'Select ' + filetypewanted

    root = tkinter.Tk()
    root.withdraw()

    filename = filedialog.askopenfilename(initialdir='.', title=windowtext)

    return filename