

#-----Imports-----#
from Vector import vec
from Physics import Ball, PhysicsBorder, LineBorder, CircleBorder
from Robotics import Bar, GroundedBar, ExtendingJoint, RotatingJoint


import pyglet
from pyglet import shapes
from pyglet.window import key, mouse
import numpy as np




#-----Methods-----#



class TennisRobot():
    
    def __init__(self, game, team, groundPosition, groundPositionFake, platformRotation):
        
        
        platformLength, armLength1, armLength2, batLength = 50, 50, 50, 100
        platformWidth = 15
        rotatorMaxTheta = 0.35 * np.pi
        primaryRotatorRadius, secondaryRotatorRadius = 13, 10
        groundLength, groundWidth = 30, 20
        minMoverLength = 40
        maxMoverLength = game.Ly - 2 * game.wallSize - 2 * groundLength - batLength
        
        self.ground = GroundedBar(game, groundPosition, 0.5 * np.pi, groundLength, groundWidth)       
        self.mover = ExtendingJoint(game, 0, 0, minMoverLength, maxMoverLength, 0, 10)
        self.platform = Bar(game, platformLength, platformWidth)
        self.rotator1 = RotatingJoint(game, 0.5 * platformLength, platformRotation, -rotatorMaxTheta, rotatorMaxTheta, 0, primaryRotatorRadius)
        self.arm1 = Bar(game, armLength1, 10)
        self.rotator2 = RotatingJoint(game, 0, 0, -rotatorMaxTheta, rotatorMaxTheta, 0, secondaryRotatorRadius)
        self.arm2 = Bar(game, armLength2, 10)
        self.rotator3 = RotatingJoint(game, 0, 0, -rotatorMaxTheta, rotatorMaxTheta, 0, secondaryRotatorRadius)
        self.bat = Bar(game, batLength, 5)
        
        self.mover.setParent(self.ground)
        self.platform.setParent(self.mover)
        self.rotator1.setParent(self.platform)
        self.arm1.setParent(self.rotator1)
        self.rotator2.setParent(self.arm1)
        self.arm2.setParent(self.rotator2)
        self.rotator3.setParent(self.arm2)
        self.bat.setParent(self.rotator3)
        
        self.ground.setBorderGroup(team + "Joint")
        self.mover.setBorderGroup(team + "Joint")
        self.platform.setBorderGroup(team + "Joint")
        self.arm1.setBorderGroup(team + "Joint")
        self.arm2.setBorderGroup(team + "Joint")
        self.bat.setBorderGroup(team + "Bat")
        
        #The mover at the top doesnt actually do anything
        self.groundFake = GroundedBar(game, groundPositionFake, -0.5 * np.pi, groundLength, groundWidth)    
        self.moverFake = ExtendingJoint(game, 0, 0, 0, 0, 0, 10)
        
        self.moverFake.setParent(self.groundFake)
        
        self.groundFake.setBorderGroup(team + "Joint")
        self.moverFake.setBorderGroup(team + "Joint")
        
        self.ground.updateUp()
        self.groundFake.updateUp()

    def setInput(self, mVelocity, r1Velocity, r2Velocity, r3Velocity, mLocked, r1Locked, r2Locked, r3Locked):
        
        self.mover.targetVelocity = mVelocity
        self.mover.locked = mLocked
        self.rotator1.targetVelocity = r1Velocity
        self.rotator1.locked = r1Locked
        self.rotator2.targetVelocity = r2Velocity
        self.rotator2.locked = r2Locked
        self.rotator3.targetVelocity = r3Velocity
        self.rotator3.locked = r3Locked
        
        self.ground.updateUp()
        
        
    def step(self, dt):
        
        self.mover.step(dt)
        self.rotator1.step(dt)
        self.rotator2.step(dt)
        self.rotator3.step(dt)
            
        self.setFakeMover()
        
        self.ground.updateUp()
        self.groundFake.updateUp()
        
    def setFakeMover(self):
        
        playWidth = (self.ground.position - self.groundFake.position).length() - self.ground.length - self.groundFake.length      
        self.moverFake.currentLength = playWidth - self.mover.currentLength - self.platform.length
        
        
    def draw(self, batchD0, batchD1, color):
        
        return [self.ground.drawUp(batchD0, batchD1, color), self.groundFake.drawUp(batchD0, batchD1, color)]
        

def drawWalls(batch, wallSize, Lx, Ly):
    
    wallLeft = shapes.Rectangle(0, 0, wallSize, Ly, color=(200, 200, 200), batch=batch)
    wallBot = shapes.Rectangle(0, 0, Lx, wallSize, color=(200, 200, 200), batch=batch)
    wallTop = shapes.Rectangle(0, Ly, Lx, -wallSize, color=(200, 200, 200), batch=batch)
    wallRight = shapes.Rectangle(Lx, 0, -wallSize, Ly, color=(200, 200, 200), batch=batch)
    
    return wallLeft, wallBot, wallTop, wallRight
    

class Game:
    
    def __init__(self):
        
        self.time = 0
        self.Lx = 1000 
        self.Ly = 600
        self.wallSize = 25
        self.lineSize = 4
        self.lineOffset = 100
        self.robotOffset = 50
        self.scoreOffset = 70
        self.scoreTextSize = 30
        
        self.blueScore = 0
        self.redScore = 0
        
        self.wallColor = (200, 200, 200)
        self.backgroundColor = (42, 201, 85)
        self.blueRobotColor = (0,0,150)
        self.redRobotColor = (150,0,0)
        
        self.dt = 0.2
        self.turn = "blue"
                
        self.borderList = []
        
        wallLengthX = self.Lx - 2 * self.wallSize
        wallLengthY = self.Ly - 2 * self.wallSize
        
        borderSouth = LineBorder(vec(self.wallSize, self.wallSize), 0, wallLengthX)
        borderWest = LineBorder(vec(self.wallSize, self.wallSize), 0.5 * np.pi, wallLengthY)
        borderNorth = LineBorder(vec(self.Lx - self.wallSize, self.Ly - self.wallSize), np.pi, wallLengthX)
        borderEast = LineBorder(vec(self.Lx - self.wallSize, self.Ly - self.wallSize), 1.5 * np.pi, wallLengthY)
        
        borderSouth.group = "neutral"
        borderWest.group = "neutral"
        borderNorth.group = "neutral"
        borderEast.group = "neutral"
        
        self.borderList += [borderSouth, borderWest, borderNorth, borderEast]
   
        self.blueRobot, self.redRobot = self.createRobots()
        self.ball = Ball(vec(0.5 * self.Lx, 0.5 * self.Ly), 10)
        
        self.initialBallVelocity = 30
        
        ballAngle = np.random.uniform(0, 2 * np.pi)       
        self.ball.velocity = vec(np.cos(ballAngle), np.sin(ballAngle)) * self.initialBallVelocity
        
        self.borderCollisionCooldown = 0.05


    def createRobots(self):
        
        blueRobotX = self.wallSize + self.robotOffset
        blueRobot = TennisRobot(self, "blue", vec(blueRobotX, self.wallSize),vec(blueRobotX, self.Ly - self.wallSize),  -0.5 * np.pi)
        
        redRobotX = self.Lx - self.wallSize - self.robotOffset
        redRobot = TennisRobot(self, "red", vec(redRobotX, self.wallSize),vec(redRobotX, self.Ly - self.wallSize), 0.5 * np.pi)
        
        blueRobot.mover.currentLength = (self.Ly - 2 * self.wallSize) / 2
        redRobot.mover.currentLength = (self.Ly - 2 * self.wallSize) / 2
        
        return blueRobot, redRobot
    
    #Return all information available to the blue robot
    def getBlueOutput(self):
        
        output = []
        
        output += [self.ball.position.x - self.robotOffset - self.wallSize, self.ball.position.y - self.wallSize]
        output += [self.ball.velocity.x, self.ball.velocity.y]
        
        output += [self.blueRobot.mover.currentLength, self.blueRobot.rotator1.theta, self.blueRobot.rotator2.theta, self.blueRobot.rotator3.theta]
        output += [self.blueRobot.mover.motorVelocity, self.blueRobot.rotator1.motorVelocity, self.blueRobot.rotator2.motorVelocity, self.blueRobot.rotator3.motorVelocity]
        
        return output
    
    #Return all information available to the red robot
    def getRedOutput(self):
        
        output = []
        
        output += [self.Lx - self.ball.position.x - self.wallSize - self.robotOffset, self.ball.position.y - self.wallSize]
        output += [self.ball.velocity.x, self.ball.velocity.y]
        
        output += [self.redRobot.mover.currentLength, -self.redRobot.rotator1.theta, -self.redRobot.rotator2.theta, -self.redRobot.rotator3.theta]
        output += [self.redRobot.mover.motorVelocity, -self.redRobot.rotator1.motorVelocity, -self.redRobot.rotator2.motorVelocity, -self.redRobot.rotator3.motorVelocity]
        
        return output
    
    def setBlueInput(self, inputs):
        
        self.blueRobot.setInput(*inputs)
        
    def setRedInput(self, inputs):
        
        inputs[1:4] = -inputs[1:4] #Angular velocity inputs are reversed to account for perspective of red
        
        self.redRobot.setInput(*inputs)
        
        
    
    def drawGame(self):
        
        self.window.clear()
        
        self.batchD0 = pyglet.graphics.Batch()
        self.batchD1 = pyglet.graphics.Batch()
        
        background = shapes.Rectangle(0, 0, self.Lx, self.Ly, color=self.backgroundColor, batch=self.batchD0)
        wallLeft, wallBot, wallTop, wallRight = drawWalls(self.batchD0, self.wallSize, self.Lx, self.Ly)
        
        lineLeftX = self.robotOffset - self.lineOffset + self.wallSize
        lineRightX = self.Lx - self.wallSize + self.lineOffset - self.robotOffset
        lineHeight = self.Ly - 2 * self.wallSize
        lineLeft = shapes.Rectangle(lineLeftX, self.wallSize, self.lineSize, lineHeight, color=(255, 255, 255), batch=self.batchD0)
        lineRight = shapes.Rectangle(lineRightX, self.wallSize, -self.lineSize, lineHeight, color=(255, 255, 255), batch=self.batchD0)
        
        blueRobotDrawing = self.blueRobot.draw(self.batchD0, self.batchD1, self.blueRobotColor)
        redRobotDrawing = self.redRobot.draw(self.batchD0, self.batchD1, self.redRobotColor)     
        ballDrawing = self.ball.draw(self.batchD0, self.batchD1, (114, 245, 66))

        blueScoreText = pyglet.text.Label(str(self.blueScore),
                    font_name='Ink Free',
                    font_size=self.scoreTextSize,
                    x=self.Lx//2 - self.scoreOffset, y=self.Ly//2,
                    anchor_x='center', anchor_y='center',
                    color = (255, 255, 255, 255),
                    batch = self.batchD1)        

        redScoreText = pyglet.text.Label(str(self.redScore),
                    font_name='Ink Free',
                    font_size=self.scoreTextSize,
                    x=self.Lx//2 + self.scoreOffset, y=self.Ly//2,
                    anchor_x='center', anchor_y='center',
                    color = (255, 255, 255, 255),
                    batch = self.batchD1) 


        self.batchD0.draw()
        self.batchD1.draw()
        
        return [background, wallLeft, wallBot, wallTop, wallRight, lineLeft, lineRight, blueRobotDrawing, redRobotDrawing, ballDrawing, blueScoreText]


    def step(self):
        
        allowedTime = self.dt
        
        if(self.blueAgent != None):
            self.setBlueInput(self.blueAgent(self.getBlueOutput()))
            
        if(self.redAgent != None):
            self.setRedInput(self.redAgent(self.getRedOutput()))
        
        while(allowedTime > 0):
        
            if(self.ball.position.x < 0 or self.ball.position.y < 0 or self.ball.position.x > self.Lx or self.ball.position.y > self.Ly):
                self.reset()
        
        
            borders = []
            collisionTimes = []
            collisionPositions = []
            for border in self.borderList:
                
                collisionTime, collisionPosition, collisionSuccess = border.getCollision(self.ball)
                if(collisionSuccess and collisionTime >= 0 and collisionTime <= allowedTime and self.time + collisionTime >= border.lastCollided + self.borderCollisionCooldown):
                    borders.append(border)
                    collisionTimes.append(collisionTime)
                    collisionPositions.append(collisionPosition)
                    
            if(len(borders) > 0):
                
                #print("colliding...")
                
                iMin = np.argmin(collisionTimes)
                minCollisionTime = collisionTimes[iMin]
                collisionBorder = borders[iMin]
                collisionPosition = collisionPositions[iMin]
                
                if(collisionBorder.group == "blueJoint"):
                    self.redScore += 1
                    self.reset()
                    break
                if(collisionBorder.group == "redJoint"):
                    self.blueScore += 1
                    self.reset()
                    break
                
                self.ball.step(minCollisionTime)
                self.blueRobot.step(minCollisionTime)
                self.redRobot.step(minCollisionTime)
                
                collisionBorder.collide(self.ball, collisionPosition)
                
                allowedTime -= minCollisionTime
                self.time += minCollisionTime
                collisionBorder.lastCollided = self.time
                
            else:
                
                self.ball.step(allowedTime)
                self.blueRobot.step(allowedTime)
                self.redRobot.step(allowedTime)
                
                self.time += allowedTime
                break
                
            
    def reset(self):
        
        self.blueRobot.mover.currentLength = (self.Ly - 2 * self.wallSize) / 2
        self.redRobot.mover.currentLength = (self.Ly - 2 * self.wallSize) / 2
        
        self.blueRobot.rotator1.theta = 0
        self.blueRobot.rotator2.theta = 0
        self.blueRobot.rotator3.theta = 0
        self.redRobot.rotator1.theta = 0
        self.redRobot.rotator2.theta = 0
        self.redRobot.rotator3.theta = 0

        self.ball.position = vec(0.5 * self.Lx, 0.5 * self.Ly)
        
        if(self.turn == "blue"):
            ballAngle = np.random.uniform(-0.25 * np.pi, 0.25 * np.pi)
            self.turn = "red"
        else:
            ballAngle = np.random.uniform(0.75 * np.pi, 1.25 * np.pi)
            self.turn = "blue"
            
        self.ball.velocity = vec(np.cos(ballAngle), np.sin(ballAngle)) * self.initialBallVelocity
        
        
    def run(self, rounds, drawGame = False, blueAgent = None, redAgent = None):
        
        self.blueAgent = blueAgent
        self.redAgent = redAgent
        
        self.blueScore = 0
        self.redScore = 0
        
        self.reset()
        
        if(drawGame):
            
            self.window = pyglet.window.Window(self.Lx, self.Ly)
            
            @self.window.event
            def on_draw():
            
                self.step()
                self.drawGame()
                
                if(self.blueScore + self.redScore >= rounds):
                    
                    pyglet.app.exit()

                
            pyglet.app.run()
                        
        else:        
        
            while(self.blueScore + self.redScore < rounds):                
                self.step()
                
        
        if(drawGame):
            self.window.close()
        
        return self.blueScore, self.redScore

        
        



#-----Main-----#


if __name__ == "__main__":
    

    game = Game()
    
    blueAgent = lambda inputs: np.array([np.random.uniform(-30,30), np.random.uniform(-5,5), np.random.uniform(-5,5), np.random.uniform(-5,5), False, False, False, False])
    redAgent = lambda inputs: np.array([np.random.uniform(-30,30), np.random.uniform(-5,5), np.random.uniform(-5,5), np.random.uniform(-5,5), False, False, False, False])
    
    game.run(20, True, blueAgent = blueAgent, redAgent = redAgent)






