#-----Imports-----#
import numpy as np



class vec():
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __add__(self, vec2):
        return vec(self.x + vec2.x, self.y + vec2.y)
    
    def __sub__(self, vec2):
        return vec(self.x - vec2.x, self.y - vec2.y)
        
    def __mul__(self, obj):

        if(isinstance(obj, vec)):
            return vec(self.x * obj.x, self.y * obj.y)
        else:
            return vec(obj * self.x, obj * self.y)
        
    def __truediv__(self, obj):

        if(isinstance(obj, vec)):
            return vec(self.x / obj.x, self.y / obj.y)
        else:
            return vec(self.x / obj, self.y / obj)

    
    def length(self):
        return np.sqrt(self.x**2 + self.y**2)
    
    def dot(self, vec2):
        return self.x * vec2.x + self.y * vec2.y
    
    def __str__(self):
        return "({},{})".format(self.x, self.y)
        