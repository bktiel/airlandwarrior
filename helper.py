import math


#function: rotateVector
import random

from panda3d.core import WindowProperties, Quat, Vec3

from templates import entity



def rotateVector(vector,angle):
    '''

    '''
    #https://stackoverflow.com/questions/14607640/rotating-a-vector-in-3d-space
    newX= vector[0] * math.cos(angle) - vector[1] * math.sin(angle)
    newY= vector[0] * math.sin(angle) - vector[1] * math.cos(angle)
    return newX,newY,vector[2]


# procedure setKeybinds
# None -> None
def setKeybinds():
    '''
    Inform instance what keypresses to accept and what to do
    Creates dict property containing movement patterns and associates WASD with each
    base.keyMap dict will be used by player class to determine object transforms

    This is really just a series of event handlers on base
    '''
    # set up dictionary that stores which movements to be making - default to false
    base.keyMap = {
        "forward": 0, "left": 0, "back": 0, "right": 0, "firing": 0, "secondary":0}
    # set up instance to accept keypresses and adjust booleans in keyMap
    # for instance, if pressing D, keyMap["right"] is true - we should be attempting move right with player object
    base.accept("w", setKey, ["forward", True])
    base.accept("a", setKey, ["left", True])
    base.accept("s", setKey, ["back", True])
    base.accept("d", setKey, ["right", True])
    # if key is lifted set dict movement entries to false
    base.accept("w-up", setKey, ["forward", False])
    base.accept("a-up", setKey, ["left", False])
    base.accept("s-up", setKey, ["back", False])
    base.accept("d-up", setKey, ["right", False])
    # if mouse down, firing, and opposite
    base.accept("mouse1", setKey, ["firing", True])
    base.accept("mouse1-up", setKey,["firing", False])


# procedure setKey
# str key, str value -> key mappings
def setKey(key, value):
    '''
    Instance contains a dictionary that will store what actions to store with what keys
    This function is necessary as it is the action performed on self.accept in self.setKeyBinds
    :return:
    '''
    base.keyMap[key] = value

#procedure mouseMode
#int mode -> None
def setMouseMode(mode):
    '''
    switches mouse mode between absolute, relative, and confined
    absolute allows mouse freedom, relative is fixed inside, confined is confined inside window
    '''
    #new instance of windowproperties
    props = WindowProperties()
    # get appropriate mousemode based on mode and apply to properties
    if mode is 0:
        #if absolute reveal cursor and enable mouse
        props.setCursorHidden(False)
        base.enableMouse()
        props.setMouseMode(WindowProperties.M_absolute)
    elif mode is 1:
        #relative
        props.setMouseMode(WindowProperties.M_relative)
        base.disableMouse()
        props.setCursorHidden(True)
    elif mode is 2:
        props.setMouseMode(WindowProperties.M_confined)
    #set window mouse mode
    base.win.requestProperties(props)
    #record as property
    base.mouseMode=mode

#procedure: bulletCollided
def bulletCollided(entry):
    '''
    handle a bullet colliding with another object
    delete bullet and cause specified damage to object
    '''
    bullet=entry.getFromNodePath()
    victim=entry.getIntoNodePath()
    #try each for owner, generally if it's a collision that matters it'll have pythontag
    bullet=bullet.getPythonTag("owner")
    victim=victim.getPythonTag("owner")
    if victim is not None and bullet is not None:
        #if it is of type entity or inherited cause damage
        if isinstance(victim,entity):
            victim.addDamage(bullet.sender,bullet.damage)
        #then destroy
        bullet.delete()

def entityCollided(entry):
    perp=entry.getFromNodePath()
    victim=entry.getIntoNodePath()

    # try each for owner, generally if it's a collision that matters it'll have pythontag
    perp = perp.getPythonTag("owner")

    if perp is None:
        return

    # if it is terrain, make grounded
    if 'terrain' in victim.name:
        if not perp.isGrounded:
            perp.isGrounded=True
        return
    else:
        return
    # try each for owner, generally if it's a collision that matters it'll have pythontag
    #perp=perp.getPythonTag("owner")
    #victim=victim.getPythonTag("owner")

#https://stackoverflow.com/a/481153
#function: pointInCircle
#Tuple,Float,Tuple->Boolean
def pointInCircle(circlePos,circleRadius,point):
    '''
    Calculates whether given point is inside the circle defined by circlePos and circleRadius
    '''
    #Calculate square distance between center and point
    #circlePos[0] and point[0] analogous to circlePos.x and point.x (assuming x,y,z tuples)
    square_dist = (circlePos[0] - point[0]) ** 2 + (circlePos[1] - point[1]) ** 2
    #return whether this distance is less than radius^2 (inside the circle)
    return square_dist <= circleRadius ** 2

#https://discourse.panda3d.org/t/convert-vector-to-hpr/2118/5
#function: vectorToHPR()
def vectorToHPR(vector):
    '''
    converts direction vector into Heading, Pitch, and Roll Panda3D attributes
    '''
    X,Y,Z=vector[0],vector[1],vector[2]
    H= -math.atan2(X, Y) * 180 / math.pi
    P= math.asin(Z) * 180 / math.pi
    R=0
    return H, P, R

#https://discourse.panda3d.org/t/points-and-vectors/1782/6
#function: HPRtoVector
def HPRtoVector(hpr):
    #q1 = Quat()
    #q1.setHpr(hpr)
    #return q1.xform(Vec3(0, 1, 0))
    X = math.sin(hpr[0] / 180 * math.pi)
    Y = math.cos(hpr[0] / 180 * math.pi)
    Z = 0
    return X,Y,Z

#function: randomPointInCircle
#find a random point within a circle created from passed args
#arg origin presumed to be of type tuple or vector ([0] is x, [1] is y)
#tuple,float,float->tuple
def randomPointInCircle(origin,outerRadius,innerRadius=0):
    #get random radius that is between two radius definitions
    radius=random.randrange(int(innerRadius),int(outerRadius))
    #get random point around circle
    #inner degrees can be up to 360
    angle=random.randrange(0,360)
    #get x,y
    x=radius*math.cos(angle)+origin[0]
    y=radius*math.sin(angle)+origin[1]
    return x,y
global base