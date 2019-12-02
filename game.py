from random import randint, randrange, uniform

from direct.gui.OnscreenImage import OnscreenImage, TransparencyAttrib
from direct.gui.DirectFrame import DirectFrame
from direct.showbase.ShowBase import ShowBase, Point3, WindowProperties, Vec3F, DirectionalLight, AmbientLight
# all collision stuff
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerPusher, CollisionHandlerQueue, \
    CollisionRay, CollideMask, CollisionSphere, CollisionHandlerPusher
#custom classes
from templates import player
from definitions.weapons import *
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

        #handle bullet collisions
        # accept this event and pass it to method bulletCollided
        base.accept('bulletCollision', bulletCollided)

        # self.render references base.render
        self.render=base.render

        #cleanup is list that saves items to destroy on mission end
        base.cleanup=[]

        # load environment
        self.makeEnviron("example")

        # load GUI
        self.makeGUI()

        #set up player and camera
        #set mouse mode to relative
        base.disableMouse()
        setMouseMode(1)

        self.player = player("models/m14", base, (0, 200, -60))

        locationJoint=self.player.actor.exposeJoint(None, "modelRoot", "frontWeaponPod")
        print((locationJoint.getParent()))

        M1X_M2(self.player,locationJoint)
        #gunModel=base.loader.loadModel("models/m1xMG")
        #gunModel.reparentTo(locationJoint)


        #load gameplay logic
        self.playerScore=0

        self.spawnBases()
        self.spawnEnemies()



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

    #procedure make GUI
    def makeGUI(self):
        '''
        Creates GUI controls and renders on screen
        Health, targeting reticle, ammunition, weapon display, score
        store results in self.playerGUI
        '''
        # TODO GUI logic for player
        self.playerGUI=DirectFrame(
            frameSize=(base.a2dLeft, base.a2dRight, base.a2dBottom, base.a2dTop),
            frameColor=(0,0,0,0)    #make completely transparent
        )
        reticle=OnscreenImage(image='images/reticle.png',scale=(0.5,1,.25))
        reticle.setTransparency(TransparencyAttrib.MAlpha)
        reticle.reparentTo(self.playerGUI)

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
        self.render.getChildren().detach()
        #delete all items in cleanup
        for i in range(len(base.cleanup)):
            garbage=base.cleanup.pop()
            del garbage


#app = mainGame()
#app.run()
