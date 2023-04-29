
#-----Imports-----#

from Main import Game

import numpy as np
import tensorflow as tf

   
class EvolutionaryTrainer():
    
    def __init__(self, mutationMethod, crossoverMethod, selectionMethod, mutationArgs, crossoverArgs, selectionArgs):
        
        self.mutationMethod = mutationMethod
        self.crossoverMethod = crossoverMethod
        self.selectionMethod = selectionMethod
        self.mutationArgs = mutationArgs
        self.crossoverArgs = crossoverArgs
        self.selectionArgs = selectionArgs
    
    
    def train(self, nSteps, nPop, nRounds):
        
        modelPopulation = [TennisModel() for i in range(nPop)]
        game = Game()
        
        for i in range(nSteps):
            
            print("Round {}".format(i))
            if(len(game.timeRatioList) > 0):
                print("TimeRatio = {}".format(np.average(game.timeRatioList)))
            
            if(i % 2 == 0):         
                np.random.choice(modelPopulation).compete(game, np.random.choice(modelPopulation), 8, True)
            
            modelPopulation = [self.mutationMethod(model, *self.mutationArgs) for model in modelPopulation]
            modelPopulation = self.selectionMethod(modelPopulation, game, nRounds,  *self.selectionArgs)
            
        return np.random.choice(modelPopulation)
            
            
            
 
class TennisModel():
    
    def __init__(self, ann = None):
        
        if(ann != None):
            self.ann = ann
        else:
            self.ann = self.initModel()
        
    def __call__(self, inputs):
        
        transformedInput = self.transformInput(inputs)
        rawOutput = self.ann(transformedInput)
        transformedOutput = self.transformOutput(rawOutput)
        
        return transformedOutput
        
        
    def initModel(self):
    
        ann = tf.keras.Sequential([
            tf.keras.layers.InputLayer(input_shape=(12,)),
            tf.keras.layers.Dense(100, activation='relu'),
            tf.keras.layers.Dense(100, activation='relu'),
            tf.keras.layers.Dense(8)
        ])
        
        return ann


    def transformInput(self, rawIn):
        
        Input = np.empty((1,len(rawIn)))
        
        Input[0,:] = rawIn
        
        return Input

    def transformOutput(self, rawOut):
        
        output = np.array(rawOut)[0,:]
    
        output[4:8] = output[4:8] > 0

        return output
    
    def compete(self, game, competitor, rounds, draw=False):
        
        myScore, enemyScore = game.run(rounds, draw, blueAgent = self, redAgent = competitor)
        
        return myScore, enemyScore
    


        
        


#-----MutationMethods-----#

def normalMutation(model, learningRate):
    
    ann = model.ann
    annClone = tf.keras.models.clone_model(model.ann)
    
    for i in range(len(ann.layers)):
        
        weights = np.array(ann.layers[i].weights[0])
        biases = np.array(ann.layers[i].weights[1])
        
        weightMutation = np.random.normal(0, learningRate, size=weights.shape)
        biasesMutation = np.random.normal(0, learningRate, size = biases.shape)
        
        annClone.layers[i].set_weights([weights + weightMutation, biases + biasesMutation])
        
        
    return TennisModel(annClone)


#-----SelectionMethods-----#


def tournamentSelection(modelPopulation, game, rounds):
    
    newModelPopulation = []
    for model in modelPopulation:
        
        enemyModel = np.random.choice(modelPopulation)
        myScore, enemyScore = model.compete(game, enemyModel, rounds, False)
        
        if(myScore > enemyScore):
            newModelPopulation.append(model)
        elif(myScore < enemyScore):
            newModelPopulation.append(enemyModel)
        else:
            
            if(np.random.random() < 0.5):
                newModelPopulation.append(model)
            else:
                newModelPopulation.append(enemyModel)
                
    return newModelPopulation



#-----Main-----#


nSteps = 200
nPop = 10
nRounds = 6

mutationMethod = normalMutation
mutationArgs = [0.1] #Learning rate

selectionMethod = tournamentSelection
selectionArgs = []

trainer = EvolutionaryTrainer(mutationMethod, None, selectionMethod, mutationArgs, None, selectionArgs)

finalModel = trainer.train(nSteps, nPop, nRounds)


#game = Game()

#model = tf.keras.Sequential([
#    tf.keras.layers.InputLayer(input_shape=(12,)),
#    tf.keras.layers.Dense(100, activation='relu'),
#    tf.keras.layers.Dense(8)
#])


#nChild = 3
#nRuns = 1000
#nRounds = 10
#learningRate = 0.005

#firstAgent = lambda x: agent(x, model)

#game.run(100, True, blueAgent = firstAgent, redAgent = firstAgent)  

#for i in range(nRuns):
#    
#    print("Round {}".format(i))
#    
#    parentAgent = lambda x: agent(x, model)
#    performanceList = []
#    childModels = []
#    
#    if(i % 2 == 0):
#        
#        game.run(3, True, blueAgent = parentAgent, redAgent = parentAgent)
#        
#
#    for j in range(nChild):
#
#        childModel = mutate(model, learningRate)      
#        childAgent= lambda x: agent(x, childModel)
#    
#        parentScore, childScore = game.run(nRounds, False, blueAgent = parentAgent, redAgent = childAgent)
        
#        childModels.append(childModel)
#        performanceList.append(childScore / (parentScore + childScore))
        
#    model = childModels[np.argmax(performanceList)]
    

#finalAgent = lambda x: agent(x, model)

#game.run(100, True, blueAgent = finalAgent, redAgent = finalAgent)  
        









