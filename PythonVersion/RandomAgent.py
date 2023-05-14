#-----Imports-----#

from NeatAgent import TennisModel
from Main import Game
import pickle


game = Game()

game.dt = 0.2

randomAgent = TennisModel(None, game)

randomAgent.compete(randomAgent, 30, True)
