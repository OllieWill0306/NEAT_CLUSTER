#from distutils.command.config import config
import neat
import numpy as np
from multiprocessing import Pool
import multiprocessing
import time

def measureFLOPS():
    #start = time.time()
    #count = 1
    #testedNumberCount = 0
    #while time.time() - start < 2:
    #    num = count
    #    while num != 4:
    #        if num % 2 == 0: num = num / 2
    #        else:
    #            num = num * 3 + 1
    #    count += 1
    #    testedNumberCount += 1
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
if __name__ == "__main__":
    import sys
    import multiprocessing
    from multiprocessing import Process
    from multiprocessing import set_start_method
    sys.path.append("C:\\Users\\xbox\\Documents\\Prog\\python\\aaa_Headers")
    import network
    import pickle
    soc = network.Client(network.selfIp(), network.PORT)

    print("Measureing FLOPS:")
    flops = measureFLOPS()
    print("FLOPS: ", flops)

    #wait for acnoligment
    while soc.recive(str) != "CONNECTED": pass
    soc.send("Main PC")
    print("Connected to Server")

    global argList
    argList = []

    while 1==1:
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
