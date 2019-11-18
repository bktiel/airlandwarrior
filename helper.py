from math import sin,cos

#function: rotateVector
def rotateVector(vector,angle):
    '''

    '''
    #https://stackoverflow.com/questions/14607640/rotating-a-vector-in-3d-space
    newX=vector[0]*cos(angle)-vector[1]*sin(angle)
    newY=vector[0]*sin(angle)-vector[1]*cos(angle)
    return newX,newY,vector[2]