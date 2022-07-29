import socket
import _thread as thread
import time
import math
import hashlib
import copy
conf = False
CONFMSG = "Conf."
PORT = 1500
def selfIp():
    return socket.gethostbyname(socket.gethostname())
class Client():
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.soc.connect((self.ip,self.port))
        except:
            print("failed to connect")
            while 1:pass
    def recive(self,convert_type = None):
        return reciveProtocol(self.soc,convert_type)
    def send(self,item):
        sendProtocol(self.soc,item)
    def rawRecive(self,size):
        return self.soc.recv(size)
    def rawSend(self,b):
        if type(b) == str:b = b.encode("utf-8")
        self.soc.send(b)
class ServerClient():
    def __init__(self,network,address):
        self.soc = network
        self.address = address
        self.new = True
        self.dead = False
    def send(self,item):
        sendProtocol(self.soc,item)
    def recive(self,convert_type = None):
        return reciveProtocol(self.soc,convert_type)
    def rawRecive(self,size):
        return self.soc.recv(size)
    def rawSend(self,b):
        if type(b) == str:b = b.encode("utf-8")
        self.soc.send(b)
class Server():
    def __init__(self,port):
        self.port = port
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.bind(("",self.port))
        self.setListen(5)
        self.clientList = []
        self.clientListLock = False
        self.acceptClientThread = thread.start_new_thread(self.acceptNewClients,())
        self.killAcceptThead = False        
    def acceptNewClients(self):
        while not self.killAcceptThead:
            time.sleep(0.5)
            network,address = self.soc.accept()
            self.clientListLock = True
            newClient = ServerClient(network,address)
            self.clientList.append(newClient)     
            self.clientListLock = False       
    def setListen(self,num):
        self.listen = num
        self.soc.listen(self.listen)
    def sendIndex(self,ind,st):
        self.clientList[ind].send(st)
    def sendAll(self,st):
        for i in self.clientList:
            i.send(st)
    #can be class or idx
    def disconnectClient(self,client):
        idx = client
        if type(client) == Client:
            idx = self.clientList.index(client)
        self.clientList.pop(idx)


def sendProtocol(soc,item,is_confirm=True):
    byteList = item
    if type(item) == str:byteList = bytes(item, 'utf-8')
    if type(item) == int:byteList = item.to_bytes(4, byteorder='big')
    size = len(byteList)
    if size == 0: return
    soc.send(int(size).to_bytes(8, byteorder='big'))
    while size != int.from_bytes(soc.recv(8), "big"):
        soc.send(int(size).to_bytes(8, byteorder='big'))
    soc.send(int(0).to_bytes(8, byteorder='big'))

    hashString = hashlib.sha256(byteList).hexdigest()

    oldByteList = copy.deapcopy(byteList)

    while 1:
        sent = 0
        while len(byteList) > 4096:
            print("Sending: ", byteList[:4096])
            soc.send(byteList[:4096])        
            byteList = byteList[4096:]
            sent += 4096
        #send remaining bytes
        if size - sent > 0:
            soc.send(byteList)

        recvHash = soc.recv(256).decode("ascii")
        if recvHash == hashString:
            break
        soc.send("NO.".encode("ascii"))
        byteList = copy.deepcopy(oldByteList)

    soc.send("OK.".encode("ascii"))
       
        
    

def reciveProtocol(soc,convert_type=None,is_confirm=True):
    while 1:
        size = int.from_bytes(soc.recv(8), "big")
        soc.send(int(size).to_bytes(8, byteorder='big'))
        if int.from_bytes(soc.recv(8), "big") == 0:
            break
    MAX_SIZE = 4096
    while 1:
        b = b""
        for i in range(math.floor(size/MAX_SIZE)):
            b += soc.recv(MAX_SIZE)
        b += soc.recv(size-(math.floor(size/MAX_SIZE) * MAX_SIZE))

        hashString = hashlib.sha256(b).hexdigest()

        soc.send(hashString.encode("ascii"))

        if soc.recv(len("OK.")).decode("ascii") == "OK.":
            break

    if convert_type == int:
        b = int.from_bytes(b, "big")   
    if convert_type == str:
        b = b.decode("utf-8")

    return b













