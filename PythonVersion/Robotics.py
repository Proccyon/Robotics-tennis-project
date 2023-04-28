
#-----imports-----#
from Vector import vec
from Physics import Ball, PhysicsBorder, LineBorder, CircleBorder

import numpy as np
from pyglet import shapes

class Joint():
    
    def __init__(self, game, positionOffset, rotationOffset):
        
        #---Parameters---#
        
        self.positionOffset = positionOffset
        self.rotationOffset = rotationOffset
        self.parentBar = None
        self.childBar = None
        
        #---Variables---#
        
        self.game = game
        self.locked = False
        
        
    def getFrame(self):
        
        parentPosition, parentRotation = self.parentBar.position, self.parentBar.rotation      
        parentDirection = vec(np.cos(parentRotation), np.sin(parentRotation))
        distanceFromParent = self.parentBar.length - self.positionOffset
        
        self.position = parentPosition + parentDirection * distanceFromParent
        self.rotation = parentRotation + self.rotationOffset
        
        angularVelocityDirection = vec(-np.sin(self.rotation), np.cos(self.rotation))
        
        self.angularVelocity = self.parentBar.angularVelocity
        self.velocity = self.parentBar.velocity + angularVelocityDirection * distanceFromParent * self.angularVelocity
        
        self.updateBorder()
        
        
        return self.position, self.rotation, self.velocity, self.angularVelocity
        
    def updateBorder(self):
        pass
    
        
    def setParent(self, parentBar):
        self.parentBar = parentBar
        parentBar.childJoint = self
        
    def getChildFrame(self):
         
        return None
    
    def updateUp(self):
        
        self.getFrame()
        if(self.childBar != None):
            self.childBar.updateUp()
            
            
    def draw(self, batchD0, batchD1, color):
        
        pass
    
    def drawUp(self, batchD0, batchD1, color):
        
        #print("({},{},{})".format(self.position.x,self.position.y,self.rotation))
        drawingList = [self.draw(batchD0, batchD1, color)]
        if(self.childBar != None):
            drawingList += self.childBar.drawUp(batchD0, batchD1, color)          
        return drawingList
        
    def setBorderGroup(self, group):
        pass
        
        

class RotatingJoint(Joint):
    
    
    def __init__(self, game, positionOffset, rotationOffset, minTheta, maxTheta, theta, radius):
        
        #---Parameters---#
        self.minTheta = minTheta
        self.maxTheta = maxTheta
        self.radius = radius
        self.maxVelocity = 3
        self.acceleration = 0.15
        
        #---Variables---#
        self.theta = theta
        self.motorVelocity = 0
        self.targetVelocity = 0       
        
        Joint.__init__(self, game, positionOffset, rotationOffset)
    
    def getChildFrame(self):
        
        childPosition = self.position
        childRotation = self.rotation + self.theta
        childVelocity = self.velocity
        childAngularVelocity = self.angularVelocity + self.motorVelocity
        
        return childPosition, childRotation, childVelocity, childAngularVelocity
    
    def draw(self, batchD0, batchD1, color):
        
        c1 = shapes.Circle(self.position.x, self.position.y, self.radius, color=color, batch=batchD0)
        c2 = shapes.Circle(self.position.x, self.position.y, 0.5 * self.radius, color=(200, 200, 200), batch=batchD1)
        
        return [c1, c2]

    #Moves the joint, runs every tick
    def step(self, dt):
        
        if(self.locked):
            targetV = 0
        else:
            if(self.targetVelocity >= self.maxVelocity):
                targetV = self.maxVelocity
            elif(self.targetVelocity <= -self.maxVelocity):
                targetV = -self.maxVelocity
            else:
                targetV = self.targetVelocity
               
        dV = dt * self.acceleration
        velocityOffset = targetV - self.motorVelocity
        
        if(np.abs(velocityOffset) <= dV):
            self.motorVelocity = targetV
        else:
            direction = velocityOffset / np.abs(velocityOffset)
            self.motorVelocity += direction * dV
            
        dTheta = dt * self.motorVelocity
        
        if(self.theta + dTheta >= self.maxTheta):
            self.theta = self.maxTheta
            self.motorVelocity = 0
        elif(self.theta + dTheta <= self.minTheta):
            self.theta = self.minTheta
            self.motorVelocity = 0
        else:
            self.theta += dTheta
            



class ExtendingJoint(Joint):

    def __init__(self, game, positionOffset, rotationOffset, minLength, maxLength, currentLength, width):
        
        #---Parameters---#
        
        self.minLength = minLength #Minimum extension length
        self.maxLength = maxLength #Maximum extension length    
        self.width = width
        self.maxVelocity = 100
        self.acceleration = 20
        
        #---variables---#
        
        self.leftBorder = LineBorder(vec(0,0),0,0)
        self.rightBorder = LineBorder(vec(0,0),0,0)
        
        game.borderList.append(self.leftBorder)
        game.borderList.append(self.rightBorder)
        
        self.currentLength = currentLength #
        self.motorVelocity = 0
        self.targetVelocity = 0
        
        
        Joint.__init__(self, game, positionOffset, rotationOffset)
        
    def getChildFrame(self):
          
        jointDirection = vec(np.cos(self.rotation), np.sin(self.rotation))
        
        childPosition = self.position + jointDirection * self.currentLength
        childRotation = self.rotation
        
        angularVelocityDirection = vec(-np.sin(self.rotation), np.cos(self.rotation))
        
        childVelocity = self.velocity + jointDirection * self.motorVelocity + angularVelocityDirection * self.currentLength * self.angularVelocity
        childAngularVelocity = self.angularVelocity
        
        return childPosition, childRotation, childVelocity, childAngularVelocity
    

    #Update the borders for the physics engine
    def updateBorder(self):
        
        perpendicular = vec(-np.sin(self.rotation), np.cos(self.rotation))
        
        self.leftBorder.position = self.position - perpendicular * 0.5 * self.width
        self.rightBorder.position = self.position + perpendicular * 0.5 * self.width
        
        self.leftBorder.rotation = self.rotation
        self.rightBorder.rotation = self.rotation
        
        self.leftBorder.length = self.currentLength
        self.rightBorder.length = self.currentLength
        
        self.leftBorder.velocity = self.velocity
        self.rightBorder.velocity = self.velocity
        
        self.leftBorder.angularVelocity = self.angularVelocity
        self.rightBorder.angularVelocity = self.angularVelocity

    def draw(self, batchD0, batchD1, color):
              
        rotationCorrection = vec(-np.sin(self.rotation), np.cos(self.rotation)) * 0.5
        d1 = shapes.Rectangle(self.position.x - rotationCorrection.x * self.width, self.position.y - rotationCorrection.y * self.width, self.currentLength, self.width, color=color, batch=batchD0) 
        d2 = shapes.Rectangle(self.position.x - rotationCorrection.x * self.width * 0.3, self.position.y - rotationCorrection.y * self.width * 0.3, self.currentLength, self.width * 0.3, color=(200,200,200), batch=batchD1) 

        d1.rotation = -self.rotation * 180 / np.pi
        d2.rotation = -self.rotation * 180 / np.pi
        return [d1,d2]
    
    #Moves the joint, runs every tick
    def step(self, dt):
        
        if(self.locked):
            targetV = 0
        else:
            if(self.targetVelocity >= self.maxVelocity):
                targetV = self.maxVelocity
            elif(self.targetVelocity <= -self.maxVelocity):
                targetV = -self.maxVelocity
            else:
                targetV = self.targetVelocity
        
        dV = dt * self.acceleration
        velocityOffset = targetV - self.motorVelocity
        
        if(np.abs(velocityOffset) <= dV):
            self.motorVelocity = targetV
        else:
            direction = velocityOffset / np.abs(velocityOffset)
            self.motorVelocity += direction * dV
            
        dL = dt * self.motorVelocity
        
        if(self.currentLength + dL>= self.maxLength):
            self.currentLength = self.maxLength
        elif(self.currentLength + dL <= self.minLength):
            self.currentLength = self.minLength
        else:
            self.currentLength += dL
            
            
    def setBorderGroup(self, group):
        
        self.leftBorder.group = group
        self.rightBorder.group = group
        
        

class Bar():
    
    def __init__(self, game, length, width):
        
        self.game = game
        self.length = length
        self.width = width
        self.parentJoint = None
        self.childJoint = None
        
        self.leftBorder = LineBorder(vec(0,0),0,0)
        self.rightBorder = LineBorder(vec(0,0),0,0)
        
        game.borderList.append(self.leftBorder)
        game.borderList.append(self.rightBorder)
        
    def getFrame(self):
        
        if(self.parentJoint != None):
            self.position, self.rotation, self.velocity, self.angularVelocity = self.parentJoint.getChildFrame()
        
        self.updateBorder()
        
        return self.position, self.rotation
    
    #Update the borders for the physics engine
    def updateBorder(self):
        
        perpendicular = vec(-np.sin(self.rotation), np.cos(self.rotation))
        
        self.leftBorder.position = self.position - perpendicular * 0.5 * self.width
        self.rightBorder.position = self.position + perpendicular * 0.5 * self.width
        
        self.leftBorder.rotation = self.rotation
        self.rightBorder.rotation = self.rotation
        
        self.leftBorder.length = self.length
        self.rightBorder.length = self.length
        
        self.leftBorder.velocity = self.velocity
        self.rightBorder.velocity = self.velocity
        
        self.leftBorder.angularVelocity = self.angularVelocity
        self.rightBorder.angularVelocity = self.angularVelocity
        
    def setBorderGroup(self, group):
        
        self.leftBorder.group = group
        self.rightBorder.group = group
    
    def setParent(self, parentJoint):
        self.parentJoint = parentJoint
        parentJoint.childBar = self
        
    def updateUp(self):
        
        self.getFrame()
        if(self.childJoint != None):
            self.childJoint.updateUp()
            
    def draw(self, batchD0, batchD1, color):
              
        rotationCorrection = vec(-np.sin(self.rotation), np.cos(self.rotation)) * 0.5 * self.width
        barDrawn = shapes.Rectangle(self.position.x - rotationCorrection.x, self.position.y - rotationCorrection.y, self.length, self.width, color=color, batch=batchD0)    
        barDrawn.rotation = -self.rotation * 180 / np.pi
        return barDrawn
    
    def drawUp(self, batchD0, batchD1, color):
        
        #print("({},{},{})".format(self.position.x,self.position.y,self.rotation))
        drawingList = [self.draw(batchD0, batchD1, color)]
        if(self.childJoint != None):
            drawingList += self.childJoint.drawUp(batchD0, batchD1, color)    

        return drawingList
        

class GroundedBar(Bar):
    
    def __init__(self, game,  position, rotation, length, width):
        self.position = position
        self.rotation = rotation
        self.velocity = vec(0,0)
        self.angularVelocity = 0
        self.parentJoint = None
        
        Bar.__init__(self, game, length, width)
        
        
        