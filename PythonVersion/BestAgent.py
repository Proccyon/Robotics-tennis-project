#-----Imports-----#

from NeatAgent import TennisModel
from NeatAgent import getFitness
from Main import Game
import pickle
import neat
import os
import numpy as np

game = Game()

game.dt = 0.2

local_dir = os.path.dirname(__file__)
savePath = "genomeHistory.txt"
config_path = os.path.join(local_dir, 'neat_config.txt')

config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_path)


with open("run6/" + savePath, "rb") as saveFile:
    genomeHistory = pickle.load(saveFile)


testRounds = 50
interval = 1
#generationList, fitnessList = getFitness(genomeHistory, config, game, testRounds, interval)    

#winner = genomeHistory[np.argmax(fitnessList)]
winner = genomeHistory[-9]

#print(np.argmax(fitnessList))

net = neat.nn.FeedForwardNetwork.create(winner, config)
winnerAgent = TennisModel(net, game)
myScore, enemyScore = winnerAgent.compete(winnerAgent, 20, True)
        