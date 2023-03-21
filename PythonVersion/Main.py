

#-----Imports-----#

import pyglet
from pyglet import shapes
import glm


#-----Methods-----#

class vec():
    
    def __init__(self, x, y):
        self.x = x
        self.y = y


def drawRobot(batch, P0, direction, theta1, theta2, theta3):
    
    motorSize = vec(20, 50)
    
    motor = shapes.Rectangle(P0.x - 0.5 * motorSize.x, P0.y - 0.5 * motorSize.y, motorSize.x, motorSize.y, color=(200, 200, 200), batch=batch)
    motor.rotation = 45
    
    
    
    return motor
    
    
def drawWalls(batch, wallSize, Lx, Ly):
    
    wallLeft = shapes.Rectangle(0, 0, wallSize, Ly, color=(200, 200, 200), batch=batch)
    wallBot = shapes.Rectangle(0, 0, Lx, wallSize, color=(200, 200, 200), batch=batch)
    wallTop = shapes.Rectangle(0, Ly, Lx, -wallSize, color=(200, 200, 200), batch=batch)
    wallRight = shapes.Rectangle(Lx, 0, -wallSize, Ly, color=(200, 200, 200), batch=batch)
    
    return wallLeft, wallBot, wallTop, wallRight

#-----Main-----#
Lx = 1000 
Ly = 600
wallSize = 25
lineSize = 4
lineOffset = 40

window = pyglet.window.Window(Lx, Ly)
batch = pyglet.graphics.Batch()

wallLeft, wallBot, wallTop, wallRight = drawWalls(batch, wallSize, Lx, Ly)

lineLeft = shapes.Rectangle(lineOffset + wallSize, wallSize, lineSize, Ly - 2 * wallSize, color=(255, 255, 255), batch=batch)
lineRight = shapes.Rectangle(Lx - wallSize - lineOffset, wallSize, -lineSize, Ly - 2 * wallSize, color=(255, 255, 255), batch=batch)

blueRobotX = wallSize + lineOffset + 0.5 * lineSize

blueRobot = drawRobot(batch, vec(blueRobotX, 300), 0, 0, 0, 0)

@window.event
def on_draw():
    window.clear()
    batch.draw()

pyglet.app.run()