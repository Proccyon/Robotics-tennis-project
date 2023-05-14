# -*- coding: utf-8 -*-
"""
Created on Thu May 11 17:00:22 2023

@author: Gebruiker
"""

class monke():
    
    def __init__(self, count):
        self.count = count


import pickle
import neat

fileName = "testText.txt"

a = [monke(1), monke(2), monke(34), monke(5) ]

pickle.dump(a, open(fileName, "wb"))

a.append(monke(9))


pickle.dump(a, open(fileName, "wb"))

b = pickle.load(open(fileName, "rb"))

print(type(b))

for monkey in b:
    print(monkey.count)

