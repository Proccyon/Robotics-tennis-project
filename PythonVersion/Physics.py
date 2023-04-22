

#-----Imports-----#

import pyglet
from pyglet import shapes
import numpy as np
from Vector import vec

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
    
    
class CircleBorder():
    
    def __init__(self, position, radius, static = False):
        self.radius = radius
        
        PhysicsBorder.__init__(self, position, static)
        
    def getCollision(ball):
        pass
    
class LineBorder():
    
        def __init__(self, position, rotation, length, static = False):
            
            self.rotation = rotation
            self.length = length
            
            PhysicsBorder.__init__(self, position, static)
            
        def getCollision(self, ball):
            
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
             
            #Check if ball and border collide
            distanceVertical = np.abs(angularVelocityDirection.dot(ball.position - self.position))
            distanceHorizontal =  Krr       
            if(distanceVertical <= ball.radius and distanceHorizontal > 0 and distanceHorizontal < self.length):
                borderVelocity = self.velocity + angularVelocityDirection * self.angularVelocity * Krr
                
                if(impactDirection.dot(ball.velocity - borderVelocity) <= 0):
                    return 0, ball.position, True
                else:
                    return 0, vec(0,0), False
            
            
            D = (Kvv - Krr * self.angularVelocity)**2 - 4 * self.angularVelocity * (Kvr * Krv - Krr * Kvv)
            
            if(D < 0 or Kvv == 0):
                return 0, vec(0,0), False
            
            if(self.angularVelocity != 0):
                collisionDistance = ((Krr * self.angularVelocity - Kvv) + np.sqrt(D)) / (2 * self.angularVelocity)
            else:
                collisionDistance = Krr - Kvr * Krv / Kvv
                
            collisionPosition = self.position + borderDirection * collisionDistance           
            collisionTime = (Krr - collisionDistance) / Krv
            
            if(collisionDistance >= 0 and collisionDistance <= self.length and collisionTime > 0):
                collisionSuccess = True
            else:
                collisionSuccess = False
                
            return collisionTime, collisionPosition, collisionSuccess
        
        def collide(self, ball, collisionPosition):
            
            #print("colliding...")
            
            borderDirection = vec(np.cos(self.rotation), np.sin(self.rotation))
            angularVelocityDirection = vec(-np.sin(self.rotation), np.cos(self.rotation))
            collisionOffset = (collisionPosition - self.position).length()
            
            collisionVelocity = self.velocity + angularVelocityDirection * self.angularVelocity * collisionOffset
            
            #Calculate direction of momentum exchange
            ballPositionRel = ball.position - self.position
            impactDirection = ballPositionRel - borderDirection * borderDirection.dot(ballPositionRel)
            impactDirection /= impactDirection.length()
            
            dV = impactDirection * -2 * impactDirection.dot(ball.velocity - collisionVelocity)
            
            ball.velocity += dV
            
            
              
            
            
            
            
            
                
        
        
                         
        
        
        