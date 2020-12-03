import tkinter as tk
from tkinter import ttk
import threading
import socket as s
import os
from cryptage import RSAEncryption
import pickle as pck
import tqdm
import re
from cryptography.fernet import Fernet
import time
import numpy as np
class Widget:
    def addInput(self,side="top", **kwargs):
        _ = tk.Entry(self, **kwargs)
        _.pack(side=side)
        return _

    def addbtn(self,side="top", **kwargs):
        _ = ttk.Button(self, **kwargs)
        _.pack(side=side)
        return _

    def addLabel(self,side="top",**kwargs):
        _ = tk.Label(self,**kwargs)
        _.pack(side=side)
        return _
    
    def addFileInput(self, side="top", **kwargs):
        _ = tk.Message(self, **kwargs)
        _.pack(side=side)
        return _
    
    def addListBox(self, side="top", **kwargs):
        _ = tk.Listbox(self, **kwargs)
        return _

    def addComboBox(self,_list=[],**kwargs):
        l = ttk.Combobox(self,values=_list, **kwargs)
        l.pack()
        return l

class App(tk.Tk,Widget):
    client = s.socket()
    SEPARATOR = "<SEPARATOR>"
    BUFFERSIZE = 2048
    def __init__(self): 
        tk.Tk.__init__(self)
        frame = tk.Frame(self)
        frame.pack()
        self.zone = self.addLabel(side='top')

        self.frame = frame

        self.message = list()

        self.addLabel(
            text="message"
        ).place(x=100,y=0)

        self.message = list()

        self.addLabel(
            text="Destinataire"
        ).place(x=100,y=110)

        self.addLabel(
            text="Liste des clients connecter"
        ).place(x=190,y=190)

        self.listbox = self.addListBox(height=5,width=80)
        self.listbox.place(x=10, y=20)

        self.listuser = self.addListBox(height=3,width=80)
        self.listuser.place(x=10, y=130)

        self.listclient = list()

        self.combobox = self.addComboBox(width=60,_list=[])
        self.combobox.place(x=60,y=210)
        self.addbtn(text="ajouter",width=62,
            command= self.ajouter
        ).place(
            x=60,y=235
        )
        self.addbtn(text="effacer",width=62,
            command= self.effacer
        ).place(
            x=60,y=260
        )
        self._listuser= list()
        self.key = dict()
        self.text = self.addLabel(text="",side="bottom")

    def ajouter(self):
        val = self.combobox.get()
        if val != "":
            self.listuser.insert(tk.END, val)
            self._listuser.append(val)

    def effacer(self):
        self.listuser.delete(first=0, last=len(self._listuser)-1)
        self._listuser = []

    def _send(self,data):
        self.client.send(data)
            
    def connect(self,host="localhost",port=5555):
        self.client.connect((host,port))
        d, e, n = RSAEncryption._key(1024)
        
        self.client.send(pck.dumps(
            ('cle',pck.dumps((d,n)))
        ))
        self.decryptage = RSAEncryption(use_to_encrypt=False)
        self.decryptage.set_private_key((e,n))
        def recvMessage():
            while True:
                serverMessage = self.client.recv(self.BUFFERSIZE)
                decode = pck.loads(serverMessage)
                self.message.append(decode)
                if decode[0] == "addr":
                    self.title(decode[1])
                if decode[0] == "listclient":
                    self._clients = decode[1]
                    self.listclient=self._clients['addr']
                    cle = self._clients['cle']
                    for i in self.listclient:
                        cryptage = RSAEncryption()
                        cryptage.set_public_key(cle[i])
                        self.key[i] = cryptage
                    self.combobox['values'] = self.listclient
                    msg = f"Server: {decode[0]}\n {decode[1]}"
                    self.listbox.insert(tk.END,msg)
                    print("[+]",msg)
                
                if decode[0] == "message":
                    msg = f"{decode[1]['from']}: {self.decryptage.decrypter(decode[1]['value'])}"
                    self.listbox.insert(tk.END,msg)
                    print("[+]",msg)

                if decode[0] == "filename":
                    filedetail = decode[1]
                    filename = filedetail['filename']
                    filesize = filedetail['filesize']
                    sender = filedetail['from']
                    cle = filedetail['cle']
                    cle = self.decryptage.decrypter_bin(cle)
                    fernet_decrypt = Fernet(cle)
                    self.listbox.insert(
                        tk.END, f"{sender}: {filename} ({filesize}B)")
                    progress = range(filesize)
                    filecr = bytes()
                    pr = int()
                    t0 = 0
                    avg = list()
                    try:
                        for _ in progress:
                            t0 = time.time()
                            avg.append(t0)
                            crypted = self.client.recv(248)
                            pr = progress.stop
                            if crypted.decode().__contains__("<"):
                                i = crypted.decode().index("<")
                                if crypted[:i] is not b'':
                                    byte_read = fernet_decrypt.decrypt(crypted[:i])
                                    filecr += byte_read
                                    t0 = time.time() - t0
                                    avg.append(t0)
                                    progress = range(filesize-len(byte_read))
                                    break
                            else:
                                byte_read = fernet_decrypt.decrypt(crypted)
                                filecr += byte_read
                                t0 = time.time() - t0
                                avg.append(t0)
                                progress = range(filesize-len(byte_read))
                        os.chdir("./receive")
                        with open(filename,"wb") as f:
                            self.text['text'] = "Reception fini.... Ecriture en cours......"
                            print(self.text['text'])
                            f.write(filecr)
                            self.text['text'] = "Ecriture du fichier fini"
                            print(self.text['text'])
                    except Exception as e:
                        print("Exception ",e)
        thread = threading.Thread(target=recvMessage)
        thread.daemon = True
        thread.start()


    def send(self):
        t = self.text.get()
        t = ('message', t)
        t = pck.dumps(t)
        self._send(t)
