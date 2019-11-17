from direct.showbase.ShowBase import ShowBase, CollisionHandlerPusher, Point3
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task import Task
from direct.actor.Actor import Actor
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import PandaNode, NodePath, Camera, TextNode
from direct.interval.IntervalGlobal import Sequence
# all collision stuff
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerQueue, \
    CollisionRay, CollideMask, CollisionSphere, CollisionHandlerPusher


class mainGame(ShowBase):
    '''
    mainGame class is the actual instance of the panda application, inherits from ShowBase
    it contains functions and methods to control flow - creation of menus, loading levels
    '''

    def __init__(self):
        '''
        class construct
        '''
        # initialize
        ShowBase.__init__(self)

        # set keybinds
        self.setKeybinds()

        # handle collisions
        # collision traversal 'traverses' instances of collides
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()

        # load environment
        self.makeEnviron("example")

        charles = entity("panda", self, (0, 60, -20))
        mike = player("panda", self, (0, 90, -20))

    def makeEnviron(self, envModel):
        '''
        creates environment of specified name and parents to renderer
        '''
        self.environment = self.loader.loadModel("models/" + envModel)
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
        self.keyMap = {
            "forward": 0, "left": 0, "back": 0, "right": 0}
        # set up instance to accept keypresses and adjust booleans in keyMap
        # for instance, if pressing D, keyMap["right"] is true - we should be attempting move right with player object
        self.accept("w", self.setKey, ["forward", True])
        self.accept("a", self.setKey, ["left", True])
        self.accept("s", self.setKey, ["back", True])
        self.accept("d", self.setKey, ["right", True])
        # if key is lifted set dict movement entries to false
        self.accept("w-up", self.setKey, ["forward", False])
        self.accept("a-up", self.setKey, ["left", False])
        self.accept("s-up", self.setKey, ["back", False])
        self.accept("d-up", self.setKey, ["right", False])

    # procedure setKey
    def setKey(self, key, value):
        '''
        Instance contains a dictionary that will store what actions to store with what keys
        This function is necessary as it is the action performed on self.accept in self.setKeyBinds
        :return:
        '''
        self.keyMap[key] = value


class entity():
    '''
    Base class for any characters
    Contains methods for movement, collision, model loading
    '''

    # NodePath model, ShowBase caller, tuple Pos -> class construction
    def __init__(self, model: str, base: ShowBase, pos: tuple) -> None:
        '''
        constructor for entity. attaches model to calling instance renderer
        '''
        #reference base for later
        self.base = base
        # creates actor object using constructor and parents to passed renderer
        self.actor = Actor(model)
        self.renderer = base.render
        self.actor.reparentTo(self.renderer)
        # put at specified location
        self.actor.setPos(pos)
        # store dimensions for later
        # https://discourse.panda3d.org/t/getting-the-height-width-and-length-of-models-solved/6504
        minimum, maximum = self.actor.getTightBounds()
        # make sure all numbers are positive for best (any) results
        self.bounds = [abs(num) for num in (minimum - maximum)]
        self.width, self.length, self.height = self.bounds[0], self.bounds[1], self.bounds[2]

        # COLLISION PROPERTIES
        # create collision ray that is height of model pointing down (will detect ground collisions)
        self.mainCol = CollisionNode('actorCollision' + str(id(self)))
        # create collision sphere as solid for this collision node
        self.mainCol.addSolid(CollisionSphere(0, 0, self.height / 2, self.height / 2))
        # specify valid collisions for collision node
        self.mainCol.setFromCollideMask(CollideMask.bit(0))
        self.mainCol.setIntoCollideMask(CollideMask.allOff())
        # attach collision node to actor
        self.cNode = self.actor.attachNewNode(self.mainCol)
        # show
        self.cNode.show()
        # make instance collision traverser aware of this collision node, tell it how to handle (with pusher)
        base.cTrav.addCollider(self.cNode, base.pusher)
        # add collision to pusher collision handler; tell pusher which node to associate with which actor IOT push
        base.pusher.addCollider(self.cNode, self.actor, base.drive.node())

        # if no initial collision, enforce gravity until collision

    def __del__(self):
        '''
        Class destructor
        Destroy an object cleanly from instance
        '''
        # self.actor.delete()


class player(entity):
    '''
    player is a playable entity.
    it has movement methods to manipulate actor based on key input
    it has a camera task to keep camera in third person perspective
    '''

    def __init__(self, model, base, pos):
        '''
        class constructor
        calls parent constructor to set up model, renderer, position
        initializes camera to focus on player character
        sets mouse mode to relative
        '''
        entity.__init__(self, model, base, pos)
        # extra player specific stuff
        # store mouseX, mouseY
        self.lastMouseX, self.lastMouseY = None, None
        # isMobile used to determine if animation currently playing - default to false
        self.isMobile = False
        # camera init
        self.setPlayer()

        taskMgr.add(self.move,"playerMoveTask")

    # procedure setPlayer
    def setPlayer(self,state=True):
        '''
        method called to set an entity as the player
        if state=true, set camera to focus on this entity
        '''
        if state:
            # store scene camera as property of this entity (since scene camera should be on the object)
            self.base.disableMouse()
            self.camera = self.base.camera
            print("e")
            self.keyMap=self.base.keyMap
            # set camera to be 10 behind and 15% above
            self.camera.setPos(self.actor.getX(), self.actor.getY() + 30, self.actor.getZ()+self.height)
            self.camera.lookAt(self.actor.getX(), self.actor.getY(), self.actor.getZ()+self.height/2)

    def move(self, task):
        '''
        Called every frame - if w,a,s,d pressed, move self.actor accordingly
        If mouse location different and not in a menu, rotate actor by delta radians
        Adjust camera to keep up with move
        '''
        # get time since last frame (multiply by distance to get actual distance to displace
        dt = globalClock.getDt()

        #rotate model by mouse transform


        # check if there is any movement
        if (True in self.keyMap.values()):
            print("move detected")
            # for every direction that is true, move object that way
            # do the same with the camera
            if self.keyMap["forward"]:
                self.actor.setY(self.actor.getY() - 100 * dt)
                # camera too..
                #self.camera.setY(self.camera.getY() - 25 * dt)
            if self.keyMap["back"]:
                self.actor.setY(self.actor.getY() + 100 * dt)
                #self.camera.setY(self.camera.getY() + 25 * dt)
            if self.keyMap["left"]:
                self.actor.setX(self.actor.getX() + 100 * dt)
                #self.camera.setH(self.camera.getH() + 200 * dt)
            if self.keyMap["right"]:
                self.actor.setX(self.actor.getX() - 100 * dt)
                #self.camera.setH(self.camera.getH() - 200 * dt)

            # lastly if attempting move simulate gravity as well
            self.actor.setZ(self.actor.getZ() - 50 * dt)
            #self.camera.setZ(self.camera.getZ() - 10 * dt)
            #update camera
            self.camera.setPos(self.actor.getX(), self.actor.getY() + 30, self.actor.getZ()+self.height)
        return task.cont

class vehicle(entity):
    '''
    Base class for vehicles
    Bipedal characters can inherit directly from entity but vehicle handling demands special attention
    '''
    pass


app = mainGame()
app.run()
