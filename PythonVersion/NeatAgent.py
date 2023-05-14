
#-----Imports-----#
from Main import Game
import visualize

import os
import neat
import visualize
import numpy as np
import pickle
import matplotlib.pyplot as plt


class TennisModel():
    
    def __init__(self, net, game):
        self.net = net
        self.game = game

        
    def __call__(self, inputs):
        
        if(self.net != None):
            transformedInput = self.transformInput(inputs)
            rawOutput = self.net.activate(transformedInput)
            transformedOutput = self.transformOutput(rawOutput)
            return transformedOutput
            
        else:
            return np.array([np.random.uniform(-30,30), np.random.uniform(-5,5), np.random.uniform(-5,5), np.random.uniform(-5,5), False, False, False, False])
        
        
    
    #Transform the input so it falls mostly within [-1, 1]
    def transformInput(self, rawIn):
        
        rawIn = np.array(rawIn)
        scaleFactor = 1 / np.sqrt(self.game.Lx * self.game.Ly)
        rawIn[0:2] *= scaleFactor
        rawIn[2:4] /= self.game.initialBallVelocity
        rawIn[4] *= scaleFactor
        rawIn[5:8] /= self.game.maxTheta
        rawIn[8] /= self.game.maxMoverVelocity
        rawIn[9:12] /= self.game.maxRotatorVelocity
        
        return rawIn

    def transformOutput(self, rawOut):
        
        output = np.array(rawOut)
    
        output[0] *= self.game.maxMoverVelocity
        output[1:4] *= self.game.maxRotatorVelocity
    
        #output[4:8] = output[4:8] > 0
        output[4:8] = False
        
        #print(output)

        return output
    
    def compete(self, competitor, rounds, draw=False):
        
        myScore, enemyScore = self.game.run(rounds, draw, blueAgent = self, redAgent = competitor)
        
        return myScore, enemyScore



def eval_genomes(genomes, config, game, rounds, savePath):
    
    fitnessList = []
    for genome_id, genome in genomes:

        myNet = neat.nn.FeedForwardNetwork.create(genome, config)
    
        myAgent = TennisModel(myNet, game)
        enemyAgent = TennisModel(None, game)
        
        #if(genome_id % 80 == 0):
        #    myAgent.compete(enemyAgent, 8, True)
        
        myScore, enemyScore = myAgent.compete(enemyAgent, rounds)
        
        fitness = myScore / rounds      
        genome.fitness = fitness
        fitnessList.append(fitness)
        
    genome_id, bestGenome = genomes[np.argmax(fitnessList)]
    genomeList.append(bestGenome)
    
    if(genome_id % 3 == 0):
        myNet = neat.nn.FeedForwardNetwork.create(bestGenome, config)    
        myAgent = TennisModel(myNet, game)      
        myAgent.compete(myAgent, 8, True)
    
    with open(savePath, "wb") as saveFile:
        pickle.dump(genomeList, saveFile)

        
def eval_genome(genome, config, game, rounds):
    
    myNet = neat.nn.FeedForwardNetwork.create(genome, config)

    myAgent = TennisModel(myNet, game)
    enemyAgent = TennisModel(None, game)
    
    #if(genome.key % 40 == 0):
    #    myAgent.compete(enemyAgent, 10, True)
    
    myScore, enemyScore = myAgent.compete(enemyAgent, rounds)
    
    return myScore / rounds


def run(config_file, nRounds, saveFile):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    game = Game()
    #evaluator = lambda genome, config: eval_genome(genome, config, game, nRounds)
    evaluator = lambda genomes, config: eval_genomes(genomes, config, game, nRounds, saveFile)

    # Run for up to 300 generations.
    #pe = neat.ThreadedEvaluator(8, evaluator)
    #winner = p.run(pe.evaluate, 300)
    #pe.stop()
    
    winner = p.run(evaluator, 60000)

    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))

    # Show output of the most fit genome against training data.
    print('\nOutput:')
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    
    winnerAgent = TennisModel(winner_net)
    winnerAgent.compete(game, winnerAgent, 30)    

    p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
    p.run(eval_genomes, 10)


def getFitness(genomes, config, game, testRounds, interval):
    
    enemyAgent = TennisModel(None, game)
    generationList = []
    fitnessList = []
    for i, genome in enumerate(genomes):
        
        if(i%interval != 0):
            continue
        
        print("Testing genome {}/{}".format(i+1,len(genomes)))
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        myAgent = TennisModel(net, game)
        myScore, enemyScore = myAgent.compete(enemyAgent, testRounds, False)
        fitness = myScore / testRounds
        generationList.append(i)
        fitnessList.append(fitness)
        
    return generationList, fitnessList

def plotFitness(generationList, fitnessList):
    
        plt.figure()
        
        plt.plot(generationList, fitnessList)
        
        plt.xlim(0, np.amax(generationList))
        plt.ylim(0, 1)
        
        plt.xlabel("Generation")
        plt.ylabel("Fitness")
        
        plt.grid(linestyle="--")
        
        plt.savefig("FitnessPlot.png")
    
    


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    
    savePath = "genomeHistory.txt"
    
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat_config.txt')
    
    #Run neat
    if(1):
    
        genomeList = []     
        rounds = 8
        run(config_path, rounds,  savePath)
    
    #Plot previous run
    if(0):
              
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                             neat.DefaultSpeciesSet, neat.DefaultStagnation,
                             config_path)
        
        game = Game()
        
        with open("run8/" + savePath, "rb") as saveFile:
            genomeHistory = pickle.load(saveFile)
        
        testRounds = 50
        interval = 3
        generationList, fitnessList = getFitness(genomeHistory, config, game, testRounds, interval)               

        #visualize.plot_stats(stats, ylog=False, view=True)
        #visualize.plot_species(stats, view=True)
            
        winner = genomeHistory[-1]
        net = neat.nn.FeedForwardNetwork.create(winner, config)
        winnerAgent = TennisModel(net, game)
        myScore, enemyScore = winnerAgent.compete(winnerAgent, 20, True)
        
        plotFitness(generationList, fitnessList)       
        
        visualize.draw_net(config, winner, True)
        visualize.draw_net(config, winner, True, prune_unused=True)
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    