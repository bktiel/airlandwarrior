from math import sin,cos

#function: rotateVector
from panda3d.core import WindowProperties


def rotateVector(vector,angle):
    '''

    '''
    #https://stackoverflow.com/questions/14607640/rotating-a-vector-in-3d-space
    newX=vector[0]*cos(angle)-vector[1]*sin(angle)
    newY=vector[0]*sin(angle)-vector[1]*cos(angle)
    return newX,newY,vector[2]

global base
# procedure setKeybinds
# None -> None
def setKeybinds():
    '''
    Inform instance what keypresses to accept and what to do
    Creates dict property containing movement patterns and associates WASD with each
    base.keyMap dict will be used by player class to determine object transforms
    '''
    # set up dictionary that stores which movements to be making - default to false
    base.keyMap = {
        "forward": 0, "left": 0, "back": 0, "right": 0}
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