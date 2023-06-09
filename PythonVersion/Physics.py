

#-----Imports-----#

import pyglet
from pyglet import shapes
import numpy as np
from Vector import vec


#----------Summary----------#
#This file contains all the collision interactions. Collisions only happen
#between balls and PhysicsBorders. The physicsBorders are attached to the walls
#and all the parts of the robot which is what allows them to interact with the
#ball. The physicsBorder defines the collision through the getCollision method
#and collide methods. getCollision returns when and where a collision with a given
#ball will take place, assuming no change in direction. collide changes the velocity
#off the ball based on energy and momentum conservation.
#---------------------------#


class Ball():
    
    def __init__(self, position, radius):
        
        self.position = position
        self.radius = radius
        self.velocity = vec(0,0)

        
    def draw(self, batchD0, batchD1, color):
        
        c1 = shapes.Circle(self.position.x, self.position.y, self.radius, color=(255,255,255), batch=batchD0)
        c2 = shapes.Circle(self.position.x, self.position.y, 0.9 * self.radius, color=color, batch=batchD1)
        
        return [c1,c2]
    
    def step(self, dt):
        
        self.position += self.velocity * dt
    
    
#A 1D element that the ball can collide with
class PhysicsBorder():
    
    def __init__(self, position, static = False):
        
        self.static = static
        self.position = position
        self.velocity = vec(0,0)
        self.angularVelocity = 0
        self.lastCollided = -900
    
    #Calculate where and when the ball will collide if it follows its current path
    def getCollision(self, ball):
        return 0, vec(0,0), False
    
    def collide(self, ball, position):
        pass
    
#Not implemented yet, would be used by rotating joints
class CircleBorder():
    
    def __init__(self, position, radius, static = False):
        self.radius = radius
        
        PhysicsBorder.__init__(self, position, static)
        
    def getCollision(ball):
        pass

#This is attached to every wall and robot part
class LineBorder():
    
        def __init__(self, position, rotation, length, static = False):
            
            self.rotation = rotation
            self.length = length
            
            PhysicsBorder.__init__(self, position, static)
            
        def getCollision(self, ball):
            
            
            collisionTimes = []
            collisionArgsList = []
            
            borderDirection = vec(np.cos(self.rotation), np.sin(self.rotation))
            angularVelocityDirection = vec(-np.sin(self.rotation), np.cos(self.rotation))
            
            edgePos = self.position
            edgeVel = self.velocity
            
            #Check collision between ball and start point of line
            cTime, cSuc, cArgs = self.pointGetCollision(ball, edgePos, edgeVel)
            if(cSuc):
                collisionTimes.append(cTime)
                collisionArgsList.append(cArgs)
                            
            edgePos = self.position + borderDirection * self.length
            edgeVel = self.velocity + self.velocity + angularVelocityDirection * self.angularVelocity
            
            #Check collision between ball and end point of line
            cTime, cSuc, cArgs = self.pointGetCollision(ball, edgePos, edgeVel)
            if(cSuc):
                collisionTimes.append(cTime)
                collisionArgsList.append(cArgs)
                
            #Check collision between ball and line
            cTime, cSuc, cArgs = self.lineGetCollision(ball)
            if(cSuc):
                collisionTimes.append(cTime)
                collisionArgsList.append(cArgs)
                
            #Return whichever collision happens first
            if(len(collisionTimes) > 0):               
                minIndex = np.argmin(collisionTimes)
                return collisionTimes[minIndex], True, collisionArgsList[minIndex]
            else:
                return 0, False, []
                
        
        def collide(self, ball, collisionTime, collisionPosition, collisionVelocity):
            
            impactDirection = ball.position - collisionPosition
            if(impactDirection.length == 0):
                print("Impact direction 0")
            impactDirection /= impactDirection.length() 
           
            #print("{}->{}".format(newBallPos, collisionPosition)) 
           
            dV = impactDirection * -2 * impactDirection.dot(ball.velocity - collisionVelocity)
            
            ball.velocity += dV
            
        def distanceTo(self, targetPosition):
            
            barDirection = vec(np.cos(self.rotation), np.sin(self.rotation))
            myLength = barDirection.dot(self.position)
            targetLength = barDirection.dot(targetPosition)
            endLength = myLength + self.length
            endPosition = self.position + barDirection * self.length
                    
            if(myLength > targetLength):
                return (targetPosition - self.position).length()
            elif(endLength < targetLength):
                return (targetPosition - endPosition).length()
            else:
                return np.sqrt((targetPosition - self.position).length()**2 - (targetLength - myLength)**2)
            
            
              
            
        #Calculates position and time of collision between ball and point         
        def pointGetCollision(self, ball, pointPosition, pointVelocity):
            
            PosDiff = ball.position - pointPosition
            VelDiff = ball.velocity - pointVelocity
            
            if(VelDiff.length() == 0):
                return 0, False, []
            
            #If ball and point intersect
            if( PosDiff.length() < ball.radius):
                
                if(PosDiff.dot(VelDiff) < 0):                   
                    return 0, True, [pointPosition, pointVelocity]
                else:
                    return 0, False, []
                  
            VbSquared = (VelDiff).length()**2
            el1 = (VelDiff).dot(PosDiff)
            el2 = VbSquared * (PosDiff.length()**2 - ball.radius**2)
            D = el1**2 - el2
            
            if(D < 0):
                return 0, False, []
            
            collisionTime = (-el1 + np.sqrt(D)) / VbSquared 
            
            if(collisionTime > 0):
                return collisionTime, True, [pointPosition + pointVelocity * collisionTime, pointVelocity] 
            else:
                return 0, False, []
            
                    
        def lineGetCollision(self, ball):
            
            borderDirection = vec(np.cos(self.rotation), np.sin(self.rotation))
            angularVelocityDirection = vec(-np.sin(self.rotation), np.cos(self.rotation))
            
            #Calculate which part of the ball will hit the border
            ballPositionRel = ball.position - self.position
            impactDirection = ballPositionRel - borderDirection * borderDirection.dot(ballPositionRel)
            impactDirection /= impactDirection.length()
            ballImpactposition = ball.position - impactDirection * ball.radius
                  
            Kvr = angularVelocityDirection.dot(ballImpactposition - self.position)
            Krv = borderDirection.dot(self.velocity - ball.velocity)
            Krr = borderDirection.dot(ballImpactposition - self.position)
            Kvv = angularVelocityDirection.dot(self.velocity - ball.velocity)
             
            #Check if ball and border intersect
            distanceVertical = np.abs(angularVelocityDirection.dot(ball.position - self.position))
            distanceHorizontal =  Krr       
            if(distanceVertical <= ball.radius and distanceHorizontal > 0 and distanceHorizontal < self.length):
                borderVelocity = self.velocity + angularVelocityDirection * self.angularVelocity * Krr
                
                if(impactDirection.dot(ball.velocity - borderVelocity) <= 0):
                    collisionPosition = self.position + borderDirection * distanceHorizontal
                    collisionVelocity = self.velocity + angularVelocityDirection * self.angularVelocity * distanceHorizontal 
                    return 0, True, [collisionPosition,collisionVelocity]
                else:
                    return 0, False, []
                       
            D = (Kvv - Krr * self.angularVelocity)**2 - 4 * self.angularVelocity * (Kvr * Krv - Krr * Kvv)
            
            if(D < 0 or Kvv == 0):
                return 0, False, []
            
            if(self.angularVelocity != 0):
                collisionDistance = ((Krr * self.angularVelocity - Kvv) + np.sqrt(D)) / (2 * self.angularVelocity)
            else:
                collisionDistance = Krr - Kvr * Krv / Kvv
                                   
            collisionTime = (Krr - collisionDistance) / Krv
            collisionPosition = ball.position + ball.velocity * collisionTime - impactDirection * ball.radius
            collisionVelocity = self.velocity + angularVelocityDirection * self.angularVelocity * collisionDistance
            
            if(collisionDistance >= 0 and collisionDistance <= self.length and collisionTime > 0):
                collisionSuccess = True
            else:
                collisionSuccess = False
                
            return collisionTime, collisionSuccess, [collisionPosition, collisionVelocity]
        
        
                         
        
        
        