#!/usr/bin/python
#
# A pygame implementation of a cellular automaton using adjacency maps. 
#
# This is probably not the most efficient way to do this, but it generalizes
# to an adjacency map of a 3D polygon model, so it can be used to operate a 
# cellular automaton over a 3D surface. 
#
# For the purposes of a 2D rectangle, the left and right edges are connected, 
# as are the top and bottom. Each pixel is an area, and the surface is a toroid. 

import pygame
import copy
import random
from pprint import pprint

#Size of the game board
sizeX = 100
sizeY = 100

#Iterations to run the system for
maxIter = 1300

#Color count, used for color mapping
colors = 4

#generate map of colors to values
colorIndex = {}
for color in range(0,colors):
    colorIndex[color] = (random.choice(range(60,255)), 
                         random.choice(range(60,255)),
                         random.choice(range(60,255)))

def genAdjMap(width,height):
    adjMap = {}
    for cellX in range(0,width):
        for cellY in range(0,height):
            cell = (cellX, cellY)
            #This is the 1-unit Moore neighborhood
            XlessOne = width-1 if cellX-1 < 0 else cellX-1
            YlessOne = height-1 if cellY-1 < 0 else cellY-1
            XplusOne = 0 if cellX+1 >= width else cellX+1
            YplusOne = 0 if cellY+1 >= height else cellY+1
            neighbors = [(XlessOne, YlessOne),
                         (XlessOne, cellY),
                         (XlessOne, YplusOne),
                         (cellX, YlessOne),
                         (cellX, YplusOne),
                         (XplusOne, YlessOne),
                         (XplusOne, cellY),
                         (XplusOne, YplusOne)]
            adjMap[cell] = neighbors
    return adjMap
    

def update(adjMap, cellValues, updateRule):
    #Do the updates on a copy
    newCellValues = copy.deepcopy(cellValues)
    
    for cell in adjMap.keys():
        #Get the value of all the neighbors
        neighborVals = [cellValues[neighbor] for neighbor in adjMap[cell]]
        newCellValues[cell] = updateRule(cellValues[cell], neighborVals)
        
    return newCellValues

#Attempt at Greenberg-Hastings:
# On update, if cell is zero and there are more than threshold 1 cells in 
# the neighborhood, transition to one. 
# All other values trainstion by one automatically, until they wrap to zero. 

def ghRule(currentColor, neighborVals):
    thresh = 1
    
    nextVal = currentColor
    
    if currentColor == 0:
        count = sum([1 if c == 1 else 0 for c in neighborVals])
        if count > thresh:
            nextVal = 1
    else:
        nextVal = currentColor + 1 if currentColor + 1 < colors else 0

    return nextVal
    
#Attempt to implement a cyclic cellular automaton, treating R, G, B as seperate 
#states, so the cell is actually three cells stacked on top of each other. 
#In a CCA, 
def ccaRule(currentColor, neighborVals):
    #Advance only if N cells around me are the next color
    thresh = 2
    
    #If we don't update, decay
    nextVal = currentColor-1 if currentColor-1 >= 0 else 0
    #Works
    
    #Count surrounding cells that are my next value
    nextColor = currentColor+1 if currentColor < colors else 0
    count = sum([1 if c == nextColor else 0 for c in neighborVals])
    
    #Update if threshold was passed
    if count > thresh:
        nextVal = nextColor
    return nextVal
      
def render(surface, colorMap):
    #Get the array of the surface:
    asArray = pygame.PixelArray(surface)
    for point in colorMap.keys():
        asArray[point[0], point[1]] = colorIndex[colorMap[point]]
    #Do the update
    pygame.display.flip()
    del asArray

                         
#Generate the adjacency map
spaceMap = genAdjMap(sizeX,sizeY)

#Generate the cell color map
colorMap = {}
for key in spaceMap.keys():
    colorMap[key] = random.choice(range(0,colors))

pygame.init()
screen = pygame.display.set_mode((sizeX,sizeY))
surface = pygame.display.get_surface()


iteration = 0
while iteration < maxIter:
    print "Iteration: {0}".format(iteration)
    #colorMap = update(spaceMap, colorMap, ccaRule)  
    colorMap = update(spaceMap, colorMap, ghRule)
    
    render(surface, colorMap)
    iteration += 1
    

while not pygame.event.get ([pygame.QUIT]):
    pass
  

