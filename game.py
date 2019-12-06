import random
from random import randint, randrange, uniform

from direct.filter.CommonFilters import CommonFilters
from direct.gui.OnscreenImage import OnscreenImage, TransparencyAttrib
from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase, Point3, WindowProperties, Vec3F, DirectionalLight, AmbientLight, \
    NodePath, PandaNode, LightRampAttrib, PointLight, Shader, SamplerState, CollisionHandlerEvent
# all collision stuff
from panda3d.ai import AIWorld, AICharacter
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerQueue, \
    CollisionRay, CollideMask, CollisionSphere, CollisionHandlerPusher, TextNode
#custom classes
from templates import player
from definitions.weapons import *
from definitions.characters import *
from helper import *

global base
global mission
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
        mission=self
        self.nextValidSpawn=0
        # handle collisions
        # collision traversal 'traverses' instances of collides
        base.cTrav = CollisionTraverser()   #switched to base
        base.pusher = CollisionHandlerPusher()  #switched to base

        base.pusher.addInPattern('entityCollision')
        base.groundHandler=CollisionHandlerQueue()
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

        mission.CAPTURE_TIME=15 #time to capture single flag
        mission.CAPTURE_RADIUS=300 #radius that needs to be controlled to cap flag

        #cleanup is list that saves items to destroy on mission end
        base.cleanup=[]
        # entities is list of all entities in gamespace. Used for applying gravity etc
        base.entities=[]
        # also keep a running list of all structures
        base.structures=[]

        #setup for AI
        base.AIworld = AIWorld(base.render)

        # load environment
        self.makeEnviron("example")

        #background music
        self.music=base.loader.loadSfx("sounds/dramatic.ogg")
        self.music.setLoop(True)
        self.music.play()

        # load GUI
        self.makeGUI()

        #set up player and camera
        #set mouse mode to relative
        base.disableMouse()
        setMouseMode(1)

        #find nodes in environment and store on game object
        self.team0Node = self.environment.find("**/team0")
        self.team0BaseNode = self.environment.find("**/team0base")
        self.team1Node = self.environment.find("**/team1")
        self.team1BaseNode = self.environment.find("**/team1base")

        #load occlusion nodes from environment
        #format in blender:
        #occlusion planes all parented to base level 'occluders' empty
        #occlusion planes named 'occluder#'
        occluder_nodes = self.environment.findAllMatches('**/occluders/+OccluderNode')
        for occluder_nodepath in occluder_nodes:
            base.render.setOccluder(occluder_nodepath)
            occluder_nodepath.node().setDoubleSided(True)

        #for now will attempt to load up to 12 flags, and reject entries that don't work
        #TODO: dynamically load based on amount of flag nodes found
        #also may change capture time depending on flag
        self.flags=[]
        self.outposts=[]
        for i in range (12):
            thisFlag=self.environment.find("**/flag"+str(i))
            #only append if found successfully
            if thisFlag.error_type == 0:
                self.flags.append(thisFlag)
                thisFlag.setPythonTag('lastCapture',None) #last capture attempt
                thisFlag.setPythonTag('lastCaptureTeam',None)   #last team that tried to cap

        #spawn player
        newPos=(self.team0Node.getX(),self.team0Node.getY(),self.team0BaseNode.getZ()+20)
        self.player = player("models/m15", base, self.team0Node.getPos())
        self.player.setScale(2)

        #standing=rifleman(base,self.team0Node.getPos(),0)
        #running = rifleman(base, self.team0Node.getPos(), 0)
        #soldat = rifleman(base, self.team0Node.getPos(), 0)
        #instancee=base.render.attachNewNode('blast')
        #instancee.setX(instancee.getX()+200)
        #instance=soldat.instanceTo(instancee)
        #instancee.setX(instancee.getX()-180)
        #enemy = rifleman(base, (20, 300, 0),1)


        #friendly = rifleman(base, self.team0Node.getPos(), 0)
        #friendly.setGoal(self.flags[1])


        locationJoint=self.player.exposeJoint(None, "modelRoot", "frontWeaponPod")
        print((locationJoint.getParent()))

        M1X_M2(self.player,locationJoint)


        #load gameplay logic

        # update all entities
        taskMgr.add(self.updateEntities, "updateEntitiesTask")
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
        base.navmesh="models/" +envModel+".navmesh.csv"
        self.environment.reparentTo(base.render)
        self.environment.setPos(0, 0, -10)
        #add to cleanup list
        base.cleanup.append(self.environment)

        # FROM PANDA3D DOCUMENTATION
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
        self.playerGUI.HP= OnscreenText(text="HEALTH", pos=(0.95, 0.8),
                                       scale=0.2, fg=(0, 0, 90, 1), align=TextNode.ACenter, mayChange=1)
        self.playerGUI.HP.reparentTo(self.playerGUI)

    #procedure updateEntities
    #task applies logic to all registered entities every frame
    def updateEntities(self,task):
        base.AIworld.update()
        timeNow = globalClock.getFrameTime()
        for item in base.entities:
            if item.is_empty():
                base.entities.remove(item)
                continue
            #call to overrideable updateState method
            item.updateState()

        #update player HP
        if self.playerGUI.HP.text != str(self.player.health):
            self.playerGUI.HP.text=str(self.player.health)

        #spawn entities
        if timeNow>=self.nextValidSpawn:
            self.spawnEnemies()


        #self.checkOutposts()


        return task.cont


    #procedure spawnBases
    def spawnBases(self):
        '''
        Create bases/outposts across the map based on environment mesh nodes
        Store in self.bases list
        '''
        #place HQs
        baseNode = base.loader.loadModel("models/hq")
        baseNode.reparentTo(base.render)
        baseNode.setPos(self.team0BaseNode.getPos())
        baseNode.setScale(4.5)
        #base.structures.append(baseNode)

        baseNode = base.loader.loadModel("models/hq")
        baseNode.reparentTo(base.render)
        baseNode.setPos(self.team1BaseNode.getPos())
        baseNode.setScale(4.5)
        baseNode.setH(self.team1BaseNode.getH())
        #base.structures.append(baseNode)

        #spawn bases on flags
        for i,flag in enumerate(self.flags):
            newBase=base.loader.loadModel("models/outpost")
            newBase.reparentTo(base.render)
            #newBase.setScale(flag.getScale())
            newBase.setPos(flag.getPos())
            #store base in flags array
            self.outposts.append(newBase)
            base.structures.append(newBase)

            #set initial team of each flag
            self.flags[i].setPythonTag('team', None)

    #procedure spawnEnemies
    def spawnEnemies(self):
        '''
        Every few ticks generate new enemies from hostile bases
        '''
        timeNow = globalClock.getFrameTime()
        self.nextValidSpawn=timeNow+random.randint(4,11)
        #actually spawns entities for both sides from respective HQs
        if len(base.entities)<12:
            #randomly choose which team to spawn more for
            team=random.randint(0,1)
            unit=None
            if team == 0:
                unit = rifleman(base, self.team0Node.getPos(), 0)
            else:
                unit = rifleman(base, self.team1Node.getPos(), 1)
            # set goal to random point around flag
            flagTarget = random.randint(0, len(self.flags) - 1)
            # find reasonable inner and outer radius
            inner=self.outposts[flagTarget].getBounds().getRadius()/2
            # outer is 1.2x the inner
            outer = 1.1 * inner
            #find random point in this circle
            x, y = randomPointInCircle(self.outposts[flagTarget].getPos(), outer, inner)
            flagTarget = (x, y, 0)
            dest = base.loader.loadModel("models/basic")
            dest.setPos(flagTarget)
            dest.reparentTo(base.render)
            unit.setGoal(flagTarget)


    #procedure checkOutposts
    def checkOutposts(self):
        '''
        Checks all outposts for entities and starts conversion process
        '''
        #check all flags for capture state
        #there must be objects of team # exclusively in capture zone for capture_time
        for flag in self.flags:
            isCapturing=True
            lastTeam=None
            lastCapture=flag.getPythonTag('lastCapture')
            lastCaptureTeam=flag.getPythonTag('lastCaptureTeam')
            flagTeam=flag.getPythonTag('team')
            # check for base.entities and see if any are in the circle created by capture radius
            for troop in base.entities:
                if pointInCircle(flag.getPos(),mission.CAPTURE_RADIUS,troop.getPos()):
                    if (lastTeam != None) and lastTeam !=troop.team:
                        #if multiple teams in zone all capture attempts aborted
                        isCapturing=False
                        flag.setPythonTag('lastCapture',None)
                        flag.setPythonTag('lastCaptureTeam',None)
                        break
                    else:
                        #otherwise add to capturezone
                        lastTeam=troop.team
            #if still isCapturing at this point all troops in the capture zone are on the same team
            #first check if capture attempt already in progress
            if isCapturing and flagTeam != lastTeam:
                timeNow = globalClock.getFrameTime()
                # check if enough time has elapsed to confer ownership
                if (lastCapture != None and lastCaptureTeam == lastTeam) \
                        and timeNow >= (lastCapture+flag.capture_time):
                    #if all these criteria true, give flag to team
                    flag.setPythonTag('team',lastTeam)
                    flag.setPythonTag('lastCapture', None)
                    flag.setPythonTag('lastCaptureTeam', None)
                # if flag.lastCapture IS none, start a capture
                elif flag.lastCaptureTeam == None:
                    flag.setPythonTag('lastCapture', lastTeam)
                    flag.setPythonTag('lastCaptureTeam', timeNow)
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
    def delete(self):
        '''
        Cleanly deletes all objects created by this scene
        '''
        self.playerGUI.removeNode()
        #clear all lights
        base.render.clearLight()

        #clear tasks created through course of gameloop
        taskMgr.remove("updateEntitiesTask")

        #clear shader effect
        base.filters.delCartoonInk()

        #delete all items in cleanup
        for garbage in base.cleanup:
            # check if actor type, if so, cleanup
            if isinstance(garbage,entity):
                continue
            else:
                garbage.removeNode()
                del garbage
        # clear entities list
        base.entities.clear()
        # clear cleanup list
        base.cleanup.clear()
        # last alibis
        base.render.getChildren().detach()




#app = mainGame()
#app.run()
