#!/usr/bin/python
from objloader import *
import sys
import math
import numpy as np
from pprint import pprint
import random

#Given an object, calculate the normal vector for each face of that object
def calcNormals(obj):
    faceNormals = []
    for face in obj.faces:
        #The normals in the face are the normals of the verticies, but we
        #want the vector normal to the face, not the vertices
        #Select the first three verticies, which define two edges of the poly. 
        #Need to subtract one because normal indicies are specified from 1
        p1 = obj.vertices[face[0][0]-1]
        p2 = obj.vertices[face[0][1]-1]
        p3 = obj.vertices[face[0][2]-1]
       
        #The vectors from p1 -> p2 and p2-> p3 
        a = [p1[0] - p2[0], p1[1]-p2[1], p1[2]-p2[2]]
        b = [p2[0] - p3[0], p2[1]-p3[1], p2[2]-p3[2]]
        
        #Cross product of the vectors
        cp = ((a[1]*b[2]-a[2]*b[1]), (a[2]*b[0]-a[0]*b[2]), (a[0]*b[1]-a[1]*b[0]))
        faceNormals.append(cp)
    return faceNormals
        
#Given a list of faces and a list of normal vectors, rotate each face into the 
#XY plane and return a list of faces that are in a flat plane. 
def calcFlatRotation(obj, normals):
    faceNrmlPairs = zip(obj.faces, normals)
    flatRotated = []
    for pair in faceNrmlPairs:
        #Want to build a transformation matrix, third row is the normal to the 
        #face, second row is a unit vector perpendicular to it, first row is 
        #cross product of the two
        
        #The normal to a face is perpendicular to any edge, so get an edge
        face = pair[0]
        p1 = obj.vertices[face[0][0]-1]
        p2 = obj.vertices[face[0][1]-1]
        a = [p1[0] - p2[0], p1[1]-p2[1], p1[2]-p2[2]]
        
        #Convert it to a unit vector
        length = math.sqrt(a[0]**2 + a[1]**2 + a[2]**2)
        a = [a[0]/length, a[1]/length, a[2]/length]
        
        #The normal is the other vector
        b = list(pair[1])
        
        #Convert it to a unit vector 
        length = math.sqrt(b[0]**2 + b[1]**2 + b[2]**2)
        b = [b[0]/length, b[1]/length, b[2]/length]
        
        #Cross product of the vectors
        cp = [(a[1]*b[2]-a[2]*b[1]), (a[2]*b[0]-a[0]*b[2]), (a[0]*b[1]-a[1]*b[0])]

        #Convert to Numpy
        rotMatrix = [cp, b, a]
        rotMatrix = np.matrix(rotMatrix)
        #Check the determinant, should be 1 (or -1 for improper reflections)
        #print np.linalg.det(rotMatrix)
        
        newPoints = []
        for point in face[0]:
            #Get the point and apply the rotation matrix to it
            point = obj.vertices[point - 1]
            point = np.matrix(point)
            point = rotMatrix * np.transpose(point)
            #Turns out, the middle entry is the one that ends up all the same,
            #so drop it when creating the points
            point = (point[0,0] , point[2,0])
            newPoints.append(point)
        flatRotated.append(newPoints)
    return flatRotated

#Find the largest x or y dimension of all polygons in the list
def findLargestPoly(polys):
    largest = 0
    for poly in polys:
        for p1 in poly:
            for p2 in poly:
                dx = abs(p1[0]-p2[0])
                dy = abs(p1[1]-p2[1])
                largest = max([dx,dy,largest])
    return largest

#Find if a number is a square, from http://stackoverflow.com/a/2489519
def isSquare(apositiveint):
  x = apositiveint // 2
  seen = set([x])
  while x * x != apositiveint:
    x = (x + (apositiveint // x)) // 2
    if x in seen: return False
    seen.add(x)
  return True
  
#Return the number, if it is a square, otherwise, the next square up
def nextSquare(val):
    if isSquare(val):
        return val
    else:
        return (int(math.sqrt(val))+1)**2

#Given a set of faces and a set of RGB tuples for each face, generate a 
#set of vertex textures and a corresponding texture file that maps each face
#to a texture of that color.
def genTexture(faces, colors):
    gridSize = findLargestPoly(faces) * 3
    imageSize = nextSquare(len(colors))
    
    #Do everything in integers
    limit = int(math.sqrt(imageSize))
    step = math.ceil(gridSize)
    
    size = int(limit*step)
    
    pygame.init()
    surface = pygame.Surface([size,size])
    colorIdx = 0
    
    #Compose the image, and calculate the offsets for the points
    textureVertices = []
    #debugVerts = []
    for y in range(0, limit):
        for x in range(0, limit):
            #Fill in the color area
            if colorIdx >= len(colors):
                color = (0,0,0)
            else:
                color = colors[colorIdx]
            surface.fill(color, pygame.Rect((x*step, y*step), (step, step)))
            
            #Create the texture verticies for the face
            if colorIdx < len(faces):
                xOff = (x*step) + step/2
                yOff = (y*step) + step/2
                face = faces[colorIdx]
                texVerts = []
                for point in face:
                    #Divide by size to scale to 0-1 range
                    #The y coordinate is subtracted from 1 because textures have the origin
                    #at the lower left, while pygame has the origin at the upper left
                    texVert = ((point[0] + xOff)/size, 1-(point[1] + yOff)/size)
                    texVerts.append(texVert)
                    #dbgVert = (point[0] + xOff, point[1] + yOff)
                    #debugVerts.append(dbgVert)
                textureVertices.append(texVerts)
            #Increment the index            
            colorIdx = colorIdx+1

    #Save the image and return the verticies            
    pygame.image.save(surface, "texture.png")        
    
    #Debugging:
    #for vert in debugVerts:
    #    surface.fill((0,0,200), pygame.Rect((vert[0], vert[1]), (1,1)))
    #pygame.image.save(surface, "debug.png")
    
    return textureVertices
        

#From an object loaded from an obj file, generate a map of the adjacencies of 
#the faces of that object. This map is used to play the actual game of life
#on the surface. I may eventually want to make a surface-shatterer that splits
#an object up into more polygons than it really should be, to have a higher-
#resolution game board. 
#TODO there is probably a way to do this in one iteration

def genAdjacencyMap(obj):
    edgewise = {}
    #For each face, make a list of its edges
    faceIdx = 0
    for face in obj.faces:
        vertices = face[0]
        for vIdx in range(-1, len(vertices)-1):
            #Both the reversed and the normal version, in case some polys are 
            #not listed in the same order as others
            edge = (vertices[vIdx], vertices[vIdx+1])
            if edge in edgewise.keys():
                edgewise[edge].append(faceIdx)
            else:
                edgewise[edge] = [faceIdx]
            #Store the reversed version too
            rEdge = (vertices[vIdx+1], vertices[vIdx])
            if rEdge in edgewise.keys():
                edgewise[rEdge].append(faceIdx)
            else:
                edgewise[rEdge] = [faceIdx]
            #Each face gets a number
        faceIdx = faceIdx + 1
    #pprint(edgewise)
            
    #For each face, find all the other 
    #faces it is adjacent to and add them to its list. 
    facewise = {}
    faceIdx = 0
    for face in obj.faces:
        vertices = face[0]
        faces = []
        for vIdx in range(-1, len(vertices)-1):
            #Both the reversed and the normal version, in case some polys are 
            #not listed in the same order as others
            edge = (vertices[vIdx], vertices[vIdx+1])
            rEdge = (vertices[vIdx+1], vertices[vIdx])
            faces.extend(list(set(edgewise[edge])|set(edgewise[rEdge])))
        #dedupe and remove self from adjacency set
        faces = list(set(faces)-set([faceIdx]))
        facewise[faceIdx] = faces
        faceIdx = faceIdx+1
    #Return the map of face ids to their adjacent faces
    return facewise
    
#Load a .obj file. Generally, the object should have only one group (no g lines)
#because generating an adjacency map won't work across the gaps. 
def loadObject(filename):
    obj = OBJ(filename, swapyz=True)
    return obj

#Display a list of 2-d polygons. Press up and down to move in the list      
def show2DList(pList):
    index = 0
    
    #Start up pygame
    pygame.init()
    
    #Set the scale factor for scaling up points
    scale = 60
    
    # Set the height and width of the screen
    width = 400
    height = 300
    size = [width, height]
    screen = pygame.display.set_mode(size)
    
    #Load no font, get some default
    font=pygame.font.Font(None,30)
 
    pygame.display.set_caption("Shapes!")
 
    #Loop until the user clicks the close button.
    done = False
    changed = True
    clock = pygame.time.Clock()

    #Draw in blue-green
    color =  (  0,   200, 200)
 
    while not done:
 
        # This limits the while loop to a max of 10 times per second.
        # Leave this out and we will use all CPU we can.
        clock.tick(10)
     
        # Handle the user quitting or pressing the up and down keys
        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                done=True # Flag that we are done so we exit this loop
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    index = index+1
                    #Roll off the end of the array and back to the start
                    if index >= len(pList) - 1:
                        index = 0
                    changed = True
                if event.key == pygame.K_DOWN:
                    index = index-1
                    #Roll off the start of the array and back to the end
                    if index < 0:
                        index = len(pList) - 1
                    changed = True
                    
        #If what we are drawing changed, get the points and draw it
        if(changed):
            changed = False
            points = pList[index]
            
            #Fill with black and draw
            screen.fill((0,0,0))    
            
            #Print the number in the corner
            polyNum=font.render("Poly:"+str(index), 1,(255,255,255))
            screen.blit(polyNum, (20, 20))

            #Draw the polygon
            for ptIdx in range(-2, len(points)-2):
                p1 = points[ptIdx]
                p2 = points[ptIdx+1]
                
                #Scale and center everything
                p1 = ((p1[0]*scale)+(width/2) , (p1[1]*scale)+(height/2))
                p2 = ((p2[0]*scale)+(width/2) , (p2[1]*scale)+(height/2))
                #Draw a line between the points, in the color, 3px wide
                pygame.draw.line(screen, color, p1, p2, 3)
            
            #Flip the buffer
            pygame.display.flip()

#Implement a cellular automata that operates on an adjacency map. 
#TODO implement instead of just assigning every map region a random color
def cellAutomate(gameboard):
    regions = gameboard.keys()
    colors = []
    color = (255,0,0)
    for region in regions:
        #color = (random.random()*155+100, random.random()*155+100, random.random()*155+100)
        colors.append(color)
        r = color[0] - 5
        g = color[1] + 5
        b = color[2]
        color=(max(r,0), min(g,255), b)
    return colors

#Write a new object file that includes the texture info and the new texture 
#verticies. 
def writeNewObj(obj, texVerts):
    #Header
    print "mtllib test.mtl"

    #Vertices
    for vertex in obj.vertices:
        asString = ""
        for coord in vertex:
            asString += str(coord) + " "
        print "v {0}".format(asString)

    #Texture vertices
    for tVertex in texVerts:
        for point in tVertex:
            print "vt {0} {1}".format(point[0], point[1])
    
    #Faces
    print "usemtl Default"
    texIndex = 1 #WHY U NO INDEX FROM ZERO
    for face in obj.faces:
        vertices = ""
        for vertex in face[0]:
            vertices += " {0}/{1}".format(vertex,texIndex)
            texIndex += 1
        print "f " + vertices

            
if __name__ == "__main__":

    #Load the object and generate the adjacency map for it
    obj = loadObject(sys.argv[1])
    adjMap = genAdjacencyMap(obj)
    
    #Running the cellular automata generates a list of the colors of each edge
    colors = cellAutomate(adjMap)
    
    #Get the flat shapes of each polygon in the object
    faceNormals = calcNormals(obj)
    flatRotated = calcFlatRotation(obj, faceNormals)
    #Debugging, show the flat shapes
    #show2DList(flatRotated)
    
    #Generate the texture verticies and the texture for the shape
    texVerts = genTexture(flatRotated, colors)
    
    #At this point, we have the texture verticies, a texture, and the original
    #object, which has its own verticies. From this, we can create a new .obj
    #file with the verticies of the original file, but with the faces extended
    #with texture verticies and the textures applied. 
    writeNewObj(obj, texVerts)
    
    
    
