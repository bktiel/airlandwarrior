from random import randint, randrange, uniform

from direct.showbase.ShowBase import ShowBase, Point3, WindowProperties, Vec3F
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task import Task
from direct.actor.Actor import Actor
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import PandaNode, NodePath, Camera, TextNode
from direct.interval.IntervalGlobal import Sequence
# all collision stuff
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerPusher, CollisionHandlerQueue, \
    CollisionRay, CollideMask, CollisionSphere, CollisionHandlerPusher
#custom classes
from actors import player
from helper import *

global base
class mainGame(ShowBase):
    '''
    mainGame class is the actual instance of the panda application, inherits from ShowBase
    it contains functions and methods to control the actual game
    '''
    def __init__(self):
        '''
        class construct
        '''
        # initialize
        #ShowBase.__init__(self)
        # set keybinds
        self.setKeybinds()

        # handle collisions
        # collision traversal 'traverses' instances of collides
        base.cTrav = CollisionTraverser()   #switched to base
        base.pusher = CollisionHandlerPusher()  #switched to base

        # self.render references base.render
        self.render=base.render

        # load environment
        self.makeEnviron("example")

        #set up player and camera
        #set mouse mode to relative
        base.disableMouse()
        self.setMouseMode(1)
        mike = player("panda", base, (0, 90, -20))

    def makeEnviron(self, envModel):
        '''
        creates environment of specified name and parents to renderer
        '''
        self.environment = base.loader.loadModel("models/" + envModel)
        self.environment.reparentTo(self.render)
        self.environment.setPos(0, 0, -10)

    # procedure setKeybinds
    def setKeybinds(self):
        '''
        Inform instance what keypresses to accept and what to do
        Creates dict property containing movement patterns and associates WASD with each
        self.keyMap dict will be used by player class to determine object transforms
        '''
        # set up dictionary that stores which movements to be making - default to false
        base.keyMap = {
            "forward": 0, "left": 0, "back": 0, "right": 0}
        # set up instance to accept keypresses and adjust booleans in keyMap
        # for instance, if pressing D, keyMap["right"] is true - we should be attempting move right with player object
        base.accept("w", self.setKey, ["forward", True])
        base.accept("a", self.setKey, ["left", True])
        base.accept("s", self.setKey, ["back", True])
        base.accept("d", self.setKey, ["right", True])
        # if key is lifted set dict movement entries to false
        base.accept("w-up", self.setKey, ["forward", False])
        base.accept("a-up", self.setKey, ["left", False])
        base.accept("s-up", self.setKey, ["back", False])
        base.accept("d-up", self.setKey, ["right", False])

    # procedure setKey
    def setKey(self, key, value):
        '''
        Instance contains a dictionary that will store what actions to store with what keys
        This function is necessary as it is the action performed on self.accept in self.setKeyBinds
        :return:
        '''
        base.keyMap[key] = value

    #procedure mouseMode
    def setMouseMode(self, mode):
        '''
        switches mouse mode between absolute, relative, and confined
        absolute allows mouse freedom, relative is fixed inside, confined is confined inside window
        '''
        #new instance of windowproperties
        props = WindowProperties()
        # get appropriate mousemode based on mode and apply to properties
        if mode is 0:
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


#app = mainGame()
#app.run()
