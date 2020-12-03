import socket
import _thread
import sys
import tqdm
import pickle as pck
#from cryptage import RSAEncryption
import os
class FileServer:
    SEPARATOR = "<SEPARATOR>"
    BUFFERSIZE= 2048
    @classmethod
    def start(cls, server="localhost", port=5555):
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            s.bind((server, port))
        except socket.error as e:
            print(str(e))

        s.listen(5)

        print(f"[+] Serveur créer: {server}:{port} ")

        clients = dict()
        cles = dict()
        def threaded_client(conn, addr):
            conn.send(pck.dumps(('addr', addr)))
            for i in clients.keys():
                clients[i].send(pck.dumps(
                    ('listclient',
                        {
                            'addr': list(clients.keys()),
                            'cle': cles
                        }
                    )
                ))
            while True:
                data = conn.recv(cls.BUFFERSIZE)
                try:
                    reply = pck.loads(data)
                    print(f'receive from:{addr}\n   {reply[0]}: {reply[1]}')
                    if reply[0]=="filename":
                        filedetail = reply[1]
                        filename = filedetail['filename']
                        filesize = filedetail['filesize']
                        destination = filedetail['sendto']
                        cle = filedetail['cle']
                        for i in destination:
                            try:
                                clients[i].send(pck.dumps(('filename',
                                                            {
                                                                'from': str(addr),
                                                                'filesize': filesize,
                                                                'filename': filename,
                                                                'cle': cle
                                                            })
                                                            ))
                            except Exception as e:
                                print("[SENDING ERROR]", e)
                        try:
                            while True:
                                byte_read = conn.recv(248)
                                if byte_read == b'<STOP>':
                                    for i in destination:
                                        try:
                                            clients[i].send(b"<STOP>")
                                        except Exception as e:
                                            print("[SENDING ERROR]", e)
                                    break
                                for i in destination:
                                    try:
                                        clients[i].send(byte_read)
                                    except Exception as e:
                                        print("[SENDING ERROR]", e)
                                           

                        except Exception as e:
                            print("[*] File sending error: ",e)
                    if reply[0]=="message":
                        message = reply[1]
                        try:
                            clients[message['sendto']].send(pck.dumps(('message',
                                {
                                    'from':str(addr),
                                    'value':message['value'],
                                })
                            ))
                        except Exception as e:
                            print("[SENDING ERROR]",e)
                    if not data:
                        print("disconnected")
                        break
                except:
                    pass
            conn.close()

        while True:
            conn, addr = s.accept()
            clients[str(addr)] = conn

            data = conn.recv(cls.BUFFERSIZE)
            cle = pck.loads(data)
            cles[str(addr)] = pck.loads(cle[1])
            
            print(addr, "is Connected")
            _thread.start_new_thread(threaded_client, (conn, addr))

    @classmethod
    def testclient(cls,server="localhost",port=5555):
        s = socket.socket()
        print("Waiting!!")
        filename = "./Complete_Bootstrap_Crash_Course__Bootstrap_4_Tutorial(360p).mp4"
        filesize = os.path.getsize(filename)
        try:
            s.connect((server,port))
        except Exception as e:
            print("[ERROR]:",e)
        print(f"[+] Connecting to {server}:{port}")
        try:
            s.send(f"{filename}{cls.SEPARATOR}{filesize}".encode())
        except Exception as e:
            print("[ERROR]:", e)
        progress = tqdm.tqdm(range(filesize),f"Sending {filename}",unit="B",unit_scale=True)
        with open(filename,"rb") as f:
            for _ in progress:
                byte_read = f.read(cls.BUFFERSIZE)
                if not byte_read:
                    break
                s.sendall(byte_read)
                progress.update(len(byte_read))
    
    @classmethod
    def teststart(cls,server="localhost",port=5555):
        s = socket.socket()

        try:
            s.bind((server, port))
        except socket.error as e:
            print(str(e))

        s.listen(5)
        conn,addr = s.accept()

        print(f"[+]{addr} is connected")
        received = conn.recv(2048).decode()
        filename,filesize = received.split(cls.SEPARATOR)
        filename = os.path.basename(filename)
        filesize = int(filesize)
        progress = tqdm.tqdm(range(filesize),f"Receiving {filename}",unit="B",unit_scale=True)
        with open(filename, "wb") as f:
            for _ in progress:
                byte_read = conn.recv(cls.BUFFERSIZE)
                if not byte_read:
                    break
                f.write(byte_read)
                progress.update(len(byte_read))

        conn.close()
        s.close()
