import socket
import _thread as thread
import time
import math
import hashlib
import copy
conf = False
CONFMSG = "Conf."
PORT = 8692
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

    soc.send(byteList)
    

def reciveProtocol(soc,convert_type=None,is_confirm=True):
    size = int.from_bytes(soc.recv(8), "big")

    b = soc.recv(size)
    print("Missing bytes: ", size - len(b))

    if convert_type == int:
        b = int.from_bytes(b, "big")   
    if convert_type == str:
        b = b.decode("utf-8")

    return b


'''
def sendProtocol(soc,item,is_confirm=True):
    byteList = item
    if type(item) == str:byteList = bytes(item, 'utf-8')
    if type(item) == int:byteList = item.to_bytes(4, byteorder='big')
    size = len(byteList)
    if size == 0: return
    soc.send(int(size).to_bytes(8, byteorder='big'))
    #while size != int.from_bytes(soc.recv(8), "big"):
    #    soc.send(int(size).to_bytes(8, byteorder='big'))
    #soc.send(int(0).to_bytes(8, byteorder='big'))

    hashString = hashlib.sha256(byteList).hexdigest()

    oldByteList = copy.deepcopy(byteList)

    newByteList = b""
    
    while 1:
        sent = 0
        while len(byteList) >= 4096:
            #print("Sending: ", byteList[:4096])
            #print("Bytes to go: ", len(byteList))
            soc.send(byteList[:4096])
            newByteList += byteList[:4096]
            byteList = byteList[4096:]
            sent += 4096
        #send remaining bytes
        if size - sent > 0:
            print("Extra send: ", len(byteList), " should be the same ", size - sent)
            soc.send(byteList)
            newByteList += byteList
            sent += len(byteList)
        print("Should be 1: ", newByteList == oldByteList)
        print("Total sent data: ", sent)

        recvHash = soc.recv(64).decode("ascii")
        time.sleep(1)
        print("Hash: ", hashString)
        print("Recv Hash: ", recvHash)
        if recvHash == hashString:
            break
        print("Resending Data as returned hash did not match")
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
'''


'''
def sendProtocol(soc,item,is_confirm=True):
    if conf and is_confirm: sendProtocol(soc,CONFMSG,False)
    byteList = item
    if type(item) == str:byteList = bytes(item, 'utf-8')
    if type(item) == int:byteList = item.to_bytes(4, byteorder='big')
    oldSize = len(byteList)
    size = len(byteList)
    print("Send size: ", size)
    while 1:
        if size > 255:
            size -= 255
            soc.send(bytes([255]))
        else:
            if size != 0:
                soc.send(bytes([size]))
            break
    soc.send(bytes([0]))
    while len(byteList) > 4096:
        soc.send(byteList[:4096])
        byteList = byteList[4096:]
        #time.sleep(5/(oldSize/4096))
    if len(byteList) > 0: soc.send(byteList) 
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
        count = 0
        for i in range(number):
            b += soc.recv(4096)
            count += 1
        extra = size - (number * 4096)
        if extra > 0:
            b += soc.recv(extra) ; count += 1
        #print("Recived ", count, " packets")
    else:
        b = soc.recv(size)
    if convert_type == int:
        b = int.from_bytes(b, "big")   
    if convert_type == str:
        b = b.decode("utf-8")
    if conf and is_confirm:
        sendProtocol(soc,CONFMSG,False)
    return b
'''













