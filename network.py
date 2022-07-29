import socket
import _thread as thread
import time
import math
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
    if conf and is_confirm: sendProtocol(soc,CONFMSG,False)
    byteList = item
    if type(item) == str:byteList = bytes(item, 'utf-8')
    if type(item) == int:byteList = item.to_bytes(4, byteorder='big')    
    size = len(byteList)
    if size > 1000000:
        print("Network error trying to send to much data")
        while 1==1: pass
    while 1:
        if size > 255:
            size -= 255
            soc.send(bytes([255]))
        else:
            if size != 0:
                soc.send(bytes([size]))
            break
    soc.send(bytes([0]))
    soc.send(byteList) 
    if conf and is_confirm:
        ret = ""
        while ret != CONFMSG:
            ret = reciveProtocol(soc,str,False)

def reciveProtocol(soc,convert_type=None,is_confirm=True):
    if is_confirm and conf:
        ret = ""
        while ret != CONFMSG:
            ret = reciveProtocol(soc,str,False)
        sendProtocol(soc,CONFMSG,False)
    size = 0
    while 1:
        addNum = int.from_bytes(soc.recv(1), "big")   
        if addNum == 0:
            break
        size += addNum
    if size > 4096:
        b = b""
        number = math.floor(size / 4096)
        for i in range(number):
            b += soc.recv(4096)
        extra = size - (number * 4096)
        if extra > 0: b += soc.recv(extra)
    else:
        b = soc.recv(size)
    if convert_type == int:
        b = int.from_bytes(b, "big")   
    if convert_type == str:
        b = b.decode("utf-8")
    if conf and is_confirm:
        sendProtocol(soc,CONFMSG,False)
    return b













