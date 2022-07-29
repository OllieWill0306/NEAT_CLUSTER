import random
#from tkinter import N
#from matplotlib.pyplot import switch_backend
import matplotlib.pyplot as plt
import neat
import time
from multiprocessing import Pool
from enum import Enum
import math
import numpy as np
import pickle


class Node():
    def __init__(self):
        self.name = None
        self.genome_recive_count = None
        self.flops = None
        self.soc = None
nodeList = []



progressList = []
def eval_genomes(genomes, config):
    #for gdx,(c,g) in enumerate(genomes):
    #    argList[gdx][0] = g
    is_newNode = False
    for cdx,c in enumerate(server.clientList):
        if c.new:
            is_newNode = True
            newNode = Node()
            newNode.soc = c
            c.new = False
            c.send("CONNECTED")
            newNode.name = c.recive(str)
            print("New Client: ", newNode.name)
            c.send("DATA")
            c.send(pickle.dumps(train_images))
            c.send(pickle.dumps(train_labels))
            c.send(pickle.dumps(config))
            newNode.flops = c.recive(int)
            nodeList.append(newNode)

    if is_newNode:# re calculate genome distrubution
        totalNumberOfGenomes = len(genomes)
        totalFlops = 0
        for i in nodeList:
            totalFlops += i.flops
        totalAllocatedGenomes = 0
        for i in nodeList:
            num = math.floor((i.flops / totalFlops)  * totalNumberOfGenomes)
            i.genome_recive_count = num
            totalAllocatedGenomes += num
        #random distributest the remainder amoungs nodes
        for i in range(totalNumberOfGenomes - totalAllocatedGenomes):
            random.choice(nodeList).genome_recive_count += 1

    start = time.time()
    genome_byteList = []
    for gdx,(c,g) in enumerate(genomes):
        genome_byteList.append(pickle.dumps(g))
    send_idx = 0
    server.sendAll("SENDING")
    for i in nodeList:
        print(i.name, " reciving ", i.genome_recive_count, " genomes")
        for j in range(i.genome_recive_count):
            i.soc.send(genome_byteList[j + send_idx])
        send_idx += i.genome_recive_count
    
    server.sendAll("SENDING_DONE")
    print("Sending data took: ", time.time() - start)

    results = []
    for i in nodeList:
        for j in range(i.genome_recive_count):
            fitnessValue = pickle.loads(i.soc.recive())
            results.append(fitnessValue)






    for i, (genome_id1, genome1) in enumerate(genomes):
        genomes[i][1].fitness = results[i] 
    progressList.append(sum(results) / len(results))




def get_one_hot(targets, nb_classes):
    res = np.eye(nb_classes)[np.array(targets).reshape(-1)]
    return res.reshape(list(targets.shape)+[nb_classes])
def runNeat(config):
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(1))

    #load data
    import tensorflow as tf
    fashion_mnist = tf.keras.datasets.mnist
    global train_images, train_labels
    (train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()
    numberOfImg = 1000
    train_images = train_images[:numberOfImg]    
    train_labels = get_one_hot(train_labels[:numberOfImg],10)
    train_images = np.reshape(train_images.astype(float),[numberOfImg,28*28]) / 255.0
    global argList
    argList = []
    idx, genomeList = zip(*p.population.items())
    for i in range(len(genomeList)):
        argList.append([0, config, (train_images, train_labels)])

    winner = p.run(eval_genomes,300)

    #kills all clients
    for i in nodeList:
        i.soc.send("DISCONNECT")
    return winner
if __name__ == '__main__':
    import multiprocessing
    from multiprocessing import Process
    from multiprocessing import set_start_method
    import sys
    sys.path.append("C:\\Users\\xbox\\Documents\\Prog\\python\\aaa_Headers\\")
    import network
    global server
    server = network.Server(network.PORT)

    #waits for client to connect
    print("Waiting for client to connect")
    while len(server.clientList) == 0: pass
    print("Client connected starting programm")

    set_start_method("spawn")
    confPath = "config.txt"

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, confPath)
    
    winner = runNeat(config)
    plt.plot(progressList)
    plt.show()







    import tensorflow as tf
    fashion_mnist = tf.keras.datasets.mnist
    (train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()
    train_images = train_images[:200]
    train_labels = train_labels[:200]
    numberOfImg = train_images.shape[0]
    train_images_no = list(train_images).copy()
    train_images = np.reshape(train_images.astype(float),[numberOfImg,28*28]) / 255.0

    myNet = neat.nn.FeedForwardNetwork.create(winner, config)
    nrCorrect = 0
    for i in range(numberOfImg):
        output = myNet.activate(train_images[i])
        pick = int(np.argmax(output))
        if pick == int(train_labels[i]):
            nrCorrect += 1
        print(output)
        print("Picked: ",pick," Correct: ",int(train_labels[i])," Answer: ",pick == int(train_labels[i]))
        print("\n\n")
        class_names = list("0123456789")
        #fig = plt.figure()
        plt.imshow(train_images_no[i])
        fig = plt.figure()
        #ax = fig.add_axes([0,0,1,1])
        plt.bar(class_names,list(output))
        plt.show()
        #plt.show()




    run = True
    while run:
        pygame.draw.rect(window,(255,0,0),(0,0,screenx,screeny))
        pygame.display.update()
