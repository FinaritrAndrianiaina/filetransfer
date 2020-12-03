from gui import App,threading,pck,RSAEncryption
from pickle import dumps
import tkinter as tk
import tkinter.filedialog as f
import tqdm,os
import fileserver
from cryptography.fernet import Fernet
app = App()
app.geometry('500x500')
app.title("Chatter Crypted")
app.wm_resizable(False,False)

filepath = None
data = None
CURRENT = os.getcwd()
def setfilepath(s):

    filepath = s
    try:
        key = Fernet.generate_key()
        crypter_fernet = Fernet(key)
        filesize = os.path.getsize(s)
        filename = os.path.basename(filepath)
        for i in app._listuser:
            details = ('filename',
                       {
                           'sendto': [i],
                           'filesize': filesize,
                           'filename': filename,
                           'cle': str(app.key[i].crypter_bin(key)).encode()
                       }
            )
            app._send(dumps(details))
            progress = tqdm.tqdm(
                range(filesize), f"Sending {filename}", unit="B", unit_scale=True)
            os.chdir(os.path.abspath(filepath.replace(filename,"")))
            with open(filename, "rb") as f:
                for _ in progress:
                    byte_read = f.read(120)
                    if not byte_read:
                        #crypted = app.key[i].crypter_bin(b"<STOP>")
                        app.client.send(b'<STOP>')
                        break
                    crypted = crypter_fernet.encrypt(byte_read)
                    app.client.send(crypted)
            os.chdir(CURRENT)
    except Exception as e:
        print("[ERROR] ",e)

app.addbtn(text='choisir un fichier à envoyer',width=60,
    command=lambda:setfilepath(f.askopenfilename()),
).place(
    x=60,y=300
)

app.addbtn(text='parametre serveur',
            command=lambda: os.system('python settings.py')).place(
                x= 5,y=400
            )

def creer_serveur():
    with open('settings.dat',"rb") as settings:
        setting = pck.load(settings)
    try:        
        server = threading.Thread(target=lambda: fileserver.FileServer.start(setting[0], setting[1]))
        server.daemon = True
        server.start()
    except Exception as e:
        print("[-] ",e)

def restart():
    app.destroy()
    os.system('python xender.py')


def seconnecter():
    with open('settings.dat', "rb") as settings:
        setting = pck.load(settings)
    try:
        app.connect(host=setting[0],port=setting[1])
    except Exception as e:
        print("[-]",e)
text = app.addInput(width=60)
text.place(
    x = 60,y=340
)
def envoyer():
    try:
        texte = text.get()
        msg = f"You: {texte}"
        app.listbox.insert(tk.END,msg)
        print("[+]",msg)
        for i in app._listuser:
            app.client.send(dumps(('message',{
                'sendto':i,
                'value':app.key[i].crypter(texte)
            })))
    except:
        pass
app.addbtn(text='envoyer à destinataire',width = 60,
           command=envoyer).place(
    x = 60,y=360
)

app.addbtn(text='creer serveur',
           command=creer_serveur).place(
    x=120, y=400
)
app.addbtn(text='se connecter',
           command=seconnecter).place(
    x=200, y=400
)
app.addbtn(text='rebooter',
           command=restart).place(
    x=300, y=400
)


app.mainloop()
