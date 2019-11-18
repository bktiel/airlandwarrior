from random import randint, randrange, uniform

from direct.showbase.ShowBase import ShowBase, Point3, WindowProperties, Vec3F, DirectionalLight, AmbientLight
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
    #procedure class constructor
    def __init__(self):
        '''
        class constructor
        Creates environment, player objects
        '''
        # initialize
        #ShowBase.__init__(self)
        # set keybinds
        setKeybinds()

        # handle collisions
        # collision traversal 'traverses' instances of collides
        base.cTrav = CollisionTraverser()   #switched to base
        base.pusher = CollisionHandlerPusher()  #switched to base

        # self.render references base.render
        self.render=base.render

        base.cleanup=[]

        # load environment
        self.makeEnviron("example")

        #set up player and camera
        #set mouse mode to relative
        base.disableMouse()
        setMouseMode(1)
        mike = player("models/m1x", base, (0, 150, -20))

    #procedure makeEnviron
    def makeEnviron(self, envModel):
        '''
        creates environment of specified name and parents to renderer
        '''
        #load environment model and add to renderer
        self.environment = base.loader.loadModel("models/" + envModel)
        self.environment.reparentTo(self.render)
        self.environment.setPos(0, 0, -10)
        #add to cleanup list
        base.cleanup.append(self.environment)

        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((.3, .3, .3, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection((-5, -5, -5))
        directionalLight.setColor((1, 1, 1, 1))
        directionalLight.setSpecularColor((1, 1, 1, 1))
        base.render.setLight(base.render.attachNewNode(ambientLight))
        base.render.setLight(base.render.attachNewNode(directionalLight))

    #procedure spawnBases
    def spawnBases(self):
        '''
        Create bases/outposts across the map based on environment mesh nodes
        Store in self.bases list
        '''
        pass

    #procedure spawnEnemies
    def spawnEnemies(self):
        '''
        Every few ticks generate new enemies from hostile bases
        '''
        pass
    #procedure captureBase
    def captureBase(self):
        '''
        Function to be called when player reaches center of base and attempts side conversion
        If successful base becomes player controlled and reinforceable
        '''
        pass

    #procedure spawnFriendly
    def spawnFriendly(self, friendly, location):
        '''
        Spawn friendly unit of type friendly (rifle, runner, tank, helo, turret)
        '''
        pass


    #procedure class deconstructor
    def __del__(self):
        '''
        Cleanly deletes all objects created by this scene
        '''
        #delete all items in cleanup
        for i in range(len(base.cleanup)):
            garbage=base.cleanup.pop()
            del garbage





#app = mainGame()
#app.run()
