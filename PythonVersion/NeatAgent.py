
#-----Imports-----#
from TennisEnv import Game
import visualize

import os
import neat
import visualize
import numpy as np
import pickle
import matplotlib.pyplot as plt

#----------Summary----------#
#This trains an agent to play the TennisEnv using the NEAT algorithm.
#Use the if statements below to set if you want to run NEAT, plot previous run
#or find the best genome in previous run. When running NEAT the results are
#saved every generation so you can end training any time. You can change the
#hyper parameters of NEAT in the 'neat_config.txt' text file.
#---------------------------#

#Wrapper for the tennis env to change input and output
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


#Calculates the fitness of every genome by playing tennis games
def eval_genomes(genomes, config, game, rounds, savePath):
    
    fitnessList = []
    for genome_id, genome in genomes:

        myNet = neat.nn.FeedForwardNetwork.create(genome, config)
    
        myAgent = TennisModel(myNet, game)
        enemyAgent = TennisModel(None, game)
        
        #You can uncomment this to show a match every few generaitons
        # if(genome_id % 80 == 0):
        #     myAgent.compete(enemyAgent, 8, True)
        
        myScore, enemyScore = myAgent.compete(enemyAgent, rounds)
        
        fitness = myScore / rounds      
        genome.fitness = fitness
        fitnessList.append(fitness)
        
    genome_id, bestGenome = genomes[np.argmax(fitnessList)]
    genomeList.append(bestGenome)
    fitnessArray.append(fitnessList)
    
    with open(savePath, "wb") as saveFile:
        pickle.dump([genomeList, fitnessArray], saveFile)

        


#Runs neat
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

    evaluator = lambda genomes, config: eval_genomes(genomes, config, game, nRounds, saveFile)
 
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


#Used for better looking plots
def reduce(array, interval):
    
        while not len(array) % interval == 0:           
            array = array[1:]
                 
        return np.mean(array.reshape(-1, interval), axis=1)
    
#Finds best performing genome out of a set of genomes
def getBestGenome(genomes, config, game, testRounds):
    
    enemyAgent = TennisModel(None, game)
    generationList = []
    fitnessList = []
    
    #Loop through all genomes to find best performing one
    for i, genome in enumerate(genomes):
        
        print("Testing genome {}/{}".format(i+1,len(genomes)))
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        myAgent = TennisModel(net, game)
        myScore, enemyScore = myAgent.compete(enemyAgent, testRounds, False)
        fitness = myScore / testRounds
        generationList.append(i)
        fitnessList.append(fitness)
        
    #Retest best performing genome
    bestGenome = genomes[np.argmax(fitnessList)]
    bestNet = neat.nn.FeedForwardNetwork.create(bestGenome, config)
    bestAgent = TennisModel(bestNet, game)
    myScore, enemyScore = bestAgent.compete(enemyAgent, 500, False)
    
    fitness = myScore / 500
        
    return genomes[np.argmax(fitnessList)], fitness
    
if __name__ == '__main__':

    
    
    savePath = "genomeHistory.txt"
    
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat_config.txt')
    
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    
    #Run neat
    if(0):
    
        genomeList = []
        fitnessArray = []
        rounds = 12 #rounds used in estimating fitness
        run(config_path, rounds,  savePath)
    
    #Plot previous run
    if(0):
              
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                             neat.DefaultSpeciesSet, neat.DefaultStagnation,
                             config_path)
        
        game = Game()
        
        FolderName = "run3" #You can change this to run1/run2 to plot other data
        with open(FolderName +"/" + savePath, "rb") as saveFile:
            genomeHistory, fitnessArray = pickle.load(saveFile)
        
        
        #Calculate average fitness and std
        averageFitnessList = np.array([np.average(fitnessArray[i]) for i in range(len(fitnessArray))])
        stdFitnessList = np.array([np.sqrt(np.average((fitnessArray[i]-averageFitnessList[i])**2)) for i in range(len(fitnessArray))])    
        generationList = np.arange(len(averageFitnessList))
        
        #Reduce array size to increase visibility
        averagingInterval = 6      
        averageFitnessList = reduce(averageFitnessList, averagingInterval)
        stdFitnessList = reduce(stdFitnessList, averagingInterval)
        generationList = reduce(generationList, averagingInterval)              
        
        #Plot the fitness over time
        plt.figure()
        
        plt.plot(generationList, averageFitnessList, label="Average Fitness", color = "black")
        plt.fill_between(generationList, averageFitnessList-stdFitnessList, averageFitnessList+stdFitnessList, label="Standard deviation")
        
        plt.xlim(0, np.amax(generationList))
        plt.ylim(0.4, 1)
        
        plt.xlabel("Generation")
        plt.ylabel("Fitness")
        
        plt.grid(linestyle="--")
        plt.legend()
        
        plt.savefig("FitnessPlot.png")
        
    #Find best genome
    if(0):
            
        testRounds = 50
        
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                             neat.DefaultSpeciesSet, neat.DefaultStagnation,
                             config_path)
        
        game = Game()
        
        FolderName = "run3" #You can change this to run1/run2 to plot other data
        with open(FolderName + "/" + savePath, "rb") as saveFile:
            genomeHistory, fitnessArray = pickle.load(saveFile)
        
        bestGenome, bestFitness = getBestGenome(genomeHistory, config, game, testRounds)
        print("bestFitness = {}".format(bestFitness))
        
    #Play a trained agent
    if(1):
        
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                             neat.DefaultSpeciesSet, neat.DefaultStagnation,
                             config_path)
        
        game = Game()

        FolderName = "run3" #You can change this to run1/run2 to plot other data
        with open(FolderName + "/" + savePath, "rb") as saveFile:
            genomeHistory, fitnessArray = pickle.load(saveFile)        

        genome = genomeHistory[-1]

        net = neat.nn.FeedForwardNetwork.create(genome, config)
        myAgent = TennisModel(net, game)
        myScore, enemyScore = myAgent.compete(myAgent, 30, True)




        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    