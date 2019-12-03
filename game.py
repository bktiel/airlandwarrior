from random import randint, randrange, uniform

from direct.filter.CommonFilters import CommonFilters
from direct.gui.OnscreenImage import OnscreenImage, TransparencyAttrib
from direct.gui.DirectFrame import DirectFrame
from direct.showbase.ShowBase import ShowBase, Point3, WindowProperties, Vec3F, DirectionalLight, AmbientLight, \
    NodePath, PandaNode, LightRampAttrib, PointLight, Shader, SamplerState, CollisionHandlerEvent
# all collision stuff
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerQueue, \
    CollisionRay, CollideMask, CollisionSphere, CollisionHandlerPusher
#custom classes
from templates import player
from definitions.weapons import *
from definitions.characters import *
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

        base.pusher.addInPattern('entityCollision')
        #base.entityCollisionHandler=CollisionHandlerEvent()
        # add catch-all handler
        #base.entityCollisionHandler.addInPattern('entityCollision')

        # handle entity collisions
        # pass to entityCollided
        base.accept('entityCollision', entityCollided)
        # handle bullet collisions
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

        self.player = player("models/m14", base, (0, 300, -10))
        enemy=rifleman(base,(30,200,-20))


        locationJoint=self.player.exposeJoint(None, "modelRoot", "frontWeaponPod")
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
        self.environment.reparentTo(base.render)
        self.environment.setPos(0, 0, -10)
        #add to cleanup list
        base.cleanup.append(self.environment)

        #ambientLight = AmbientLight("ambientLight")
        #ambientLight.setColor((.3, .3, .3, 1))
        #directionalLight = DirectionalLight("directionalLight")
        #directionalLight.setColor((1, 1, 1, 1))
        #directionalLight.setSpecularColor((1, 1, 1, 1))
        #base.render.setLight(base.render.attachNewNode(ambientLight))
        #base.render.setLight(base.render.attachNewNode(directionalLight))

        # Enable a 'light ramp' - this discretizes the lighting,
        # which is half of what makes a model look like a cartoon.
        # Light ramps only work if shader generation is enabled,
        # so we call 'setShaderAuto'.
        tempnode = NodePath(PandaNode("temp node"))
        tempnode.setAttrib(LightRampAttrib.makeSingleThreshold(0.5, 0.4))
        tempnode.setShaderAuto()
        # add to cleanup
        base.cleanup.append(tempnode)
        base.cam.node().setInitialState(tempnode.getState())

        self.separation = 1 # Pixels
        filterok = base.filters.setCartoonInk(separation=self.separation)
        if (filterok == False):
            print("not good enough GPU")
            exit()
        base.accept("v", base.bufferViewer.toggleEnable)
        #plightnode = DirectionalLight("point light")
        plightnode = PointLight("point light")
        plightnode.setAttenuation((1, 0, 0))
        plight = base.render.attachNewNode(plightnode)
        plight.node().setScene(base.render)
        plight.node().setShadowCaster(True, 512, 512)
        plight.setPos(0, 190, 300)
        print(plight.getHpr())
        plight.lookAt(self.environment)
        print(plight.getHpr())
        alightnode = AmbientLight("ambient light")
        alightnode.setColor((0.8, 0.8, 0.8, 1))
        alight = base.render.attachNewNode(alightnode)
        base.render.setLight(alight)
        base.render.setLight(plight)

        base.cleanup.append(alight)
        base.cleanup.append(plight)


        #load skybox
        skybox = base.loader.loadModel("models/skybox.bam")
        skybox.reparent_to(base.render)
        skybox.set_scale(20000)

        skybox_texture = base.loader.loadTexture("models/tex/sky.png")
        skybox_texture.set_minfilter(SamplerState.FT_linear)
        skybox_texture.set_magfilter(SamplerState.FT_linear)
        skybox_texture.set_wrap_u(SamplerState.WM_repeat)
        skybox_texture.set_wrap_v(SamplerState.WM_mirror)
        skybox_texture.set_anisotropic_degree(16)
        skybox.set_texture(skybox_texture)

        skybox_shader = Shader.load(Shader.SL_GLSL, "skybox.vert.glsl", "skybox.frag.glsl")
        skybox.set_shader(skybox_shader)

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
        #clear all lights
        base.render.clearLight()

        #clear shader effect
        base.filters.delCartoonInk()

        #delete all items in cleanup
        base.render.getChildren().detach()
        for garbage in base.cleanup:
            #garbage=base.cleanup.pop()
            garbage.remove_node()

            del garbage



#app = mainGame()
#app.run()
