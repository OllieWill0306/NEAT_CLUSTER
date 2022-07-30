#from distutils.command.config import config
import neat
import numpy as np
from multiprocessing import Pool
import multiprocessing
import time

def measureFLOPS():
    count = 1.0
    num = 0
    testedNumberCount = 0
    start = time.time()
    while time.time() - start < 2:
        count = count * 10.0 + 1.0
        if count > 999999.0:
            count = 0.0
        testedNumberCount += 1
    return testedNumberCount * multiprocessing.cpu_count()
def run_genome(dataList):
    genome,config,pictureList = dataList      
    myNet = neat.nn.FeedForwardNetwork.create(genome, config)
    genome.fitness = 0
    for i in range(pictureList[0].shape[0]):
        output = myNet.activate(pictureList[0][i])
        #output = np.clip(output, 0.0, 20.0)
        correct = np.argmax(pictureList[1][i])
        pick = int(np.argmax(np.array(output)))
        output = 1.0 / (1.0 + np.exp(-np.array(output,dtype=float)))
        ans = min(output[correct],20.0)
        output[correct] = 0
        genome.fitness += ans - (np.sum(output) / 9.0) + float(pick == correct)
    print("Evaluated Genome/", end = "")
    return genome
progressList = []
def eval_genomes():
    SINGLE_THREAD = False
    if SINGLE_THREAD:
        results = []
        for i in argList:
            global is_draw
            is_draw = True
            results.append(run_genome(i))
    else:
        with Pool() as pool:
            results = pool.map(run_genome, argList)
    for i in range(len(results)):
        argList[i][0].fitness = results[i].fitness
    print("")
def ReadConfigFile(): 
    ip_string = None   
    userName = None

    f = open("ClientSetup.txt","r")
    content = f.read()
    lineList = content.split("\n")
    for l in lineList:
        wordList = l.split(" ")
        if wordList[0] == "ClientName:":
            userName = wordList[1]
        elif wordList[0] == "IpAddress:":
            ip_string = wordList[1]
    f.close()
    if userName == None:
        print("ClientSetup.txt could not find Client username. Stopping")
        input()
    if ip_string == None:
        print("ClientSetup.txt could not find Ip Address. Stopping")
        input()
    return userName, ip_string
def is_stopping():
    clientStopFile = open("Client_stop.txt","r")
    content = clientStopFile.read()
    clientStopFile.close()
    return bool(content == "true")
if __name__ == "__main__":
    import sys
    import multiprocessing
    from multiprocessing import Process
    from multiprocessing import set_start_method
    import network
    import pickle    

    print("Measureing FLOPS:")
    flops = measureFLOPS()
    print("FLOPS: ", flops)

    print("Reading Config File:")
    userName, ip_string = ReadConfigFile()
    print("Client Name: ", userName)
    print("Connecting to: ", ip_string)

    soc = network.Client(ip_string, network.PORT)

    clientStopFile = open("Client_stop.txt","w")
    clientStopFile.write("false")
    clientStopFile.close()

    #wait for acnoligment
    while soc.recive(str) != "CONNECTED": pass
    soc.send(userName)
    print("Connected to Server")

    global argList
    argList = []

    while 1==1:
        stopping = is_stopping()
        if stopping == True: print("Stopping waiting for stopping point...")

        data = soc.recive()
        if data == "DISCONNECT".encode("utf-8"):
            print("Disconnected by server")
            break
        if data == "DATA".encode("utf-8"):
            print("Reciving data")
            global train_images, train_labels, config
            train_images = pickle.loads(soc.recive())
            train_labels = pickle.loads(soc.recive()) 
            config = pickle.loads(soc.recive())
            soc.send(flops)
        if data == "ARE_DISCONNECT".encode("utf-8"):
            soc.send(int(stopping))
            if stopping:
                print("Disconnecting from server")                
                break
        if data == "SENDING".encode("utf-8"):
            print("Server sending genomes")
            add_idx = 0
            while 1==1:
                msg = soc.recive()
                if msg == "SENDING_DONE".encode("utf-8"):
                    break
                g = pickle.loads(msg)
                if add_idx >= len(argList):
                    argList.append([0,config, (train_images, train_labels)])
                argList[add_idx][0] = g
                add_idx += 1
            #remove extra
            while add_idx < len(argList):
                argList.pop()
            print("Evaluating fitness")
            #evaluate genomes
            eval_genomes()
            #send data back to server
            print("Sending fitness back")
            for i in argList:
                soc.send(pickle.dumps(float(i[0].fitness)))
            
    print("Exitted")
