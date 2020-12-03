from gui import Widget
import pickle as pck
import tkinter as tk
import tkinter.filedialog as f
import tqdm
import os


class Settings(tk.Tk, Widget):
    def __init__(self):
        tk.Tk.__init__(self)
        frame = tk.Frame(self)
        frame.pack()

settings = Settings()
settings.geometry("300x300")

settings.title("SETTINGS")

text = settings.addLabel(text="SETTINGS")

settings.addLabel(text='host')
host = settings.addInput()

settings.addLabel(text='port')

port = settings.addInput()
error = settings.addLabel(text='')


def sauver(host, port):
    try:
        with open('settings.dat', 'wb') as file:
            pck.dump((host, int(port)), file)
    except Exception as e:
        error['text'] = f'options invalide {e}'

settings.addbtn(text="Confirmer",
    command= lambda : sauver(host.get(),port.get())
)

settings.mainloop()
