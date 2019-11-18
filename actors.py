#definitions for actors
from direct.showbase.ShowBase import ShowBase, CollisionHandlerPusher, Point3, WindowProperties, Vec3F
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task import Task
from direct.actor.Actor import Actor
from direct.task.TaskManagerGlobal import taskMgr
# all collision stuff
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerQueue, \
    CollisionRay, CollideMask, CollisionSphere, CollisionHandlerPusher

global base
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

        #create node at front of actor to track rotation
        #self.front = NodePath(PandaNode("front"))
        #self.front.reparentTo(self.actor)
        #self.front.setY(self.actor.getY()+2)

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
            self.camera = base.camera
            self.keyMap= base.keyMap
            self.camera.reparentTo(self.actor)
            # set camera to be 10 behind and 15% above
            self.camera.setPos(self.actor.getX(), self.actor.getY() + 50, self.actor.getZ()+self.height)
            self.camera.lookAt(self.actor.getX(), self.actor.getY(), self.actor.getZ()+self.height)

    def move(self, task):
        '''
        Called every frame - if w,a,s,d pressed, move self.actor accordingly
        If mouse location different and not in a menu, rotate actor by delta radians
        Adjust camera to keep up with move
        '''
        # get time since last frame (multiply by distance to get actual distance to displace
        dt = globalClock.getDt()

        #update camera (also updates model using mouselook)
        self.updateCamera()

        # check if there is any movement
        if (True in self.keyMap.values()):
            #isMobile tracks whether object is moving or not for other functions
            self.isMobile=True
            # for every direction that is true, move object that way
            # do the same with the camera
            if self.keyMap["forward"]:
                self.actor.setY(self.actor, - 100 * dt)
                # camera too..
                #self.camera.setY(self.camera.getY() - 25 * dt)
            if self.keyMap["back"]:
                self.actor.setY(self.actor, + 100 * dt)
                #self.camera.setY(self.camera.getY() + 25 * dt)
            if self.keyMap["left"]:
                self.actor.setX(self.actor, + 100 * dt)
                #self.camera.setH(self.camera.getH() + 200 * dt)
            if self.keyMap["right"]:
                self.actor.setX(self.actor, - 100 * dt)
                #self.camera.setH(self.camera.getH() - 200 * dt)

            # lastly if attempting move simulate gravity as well
            self.actor.setZ(self.actor.getZ() - 50 * dt)
        else:
            self.isMobile=False
        return task.cont

    def updateCamera(self):
        '''
        update camera for player depending on mouse transform
        '''
        # rotate model by mouse transform
        # first retrieve mouse watcher from base application
        mw = self.base.mouseWatcherNode

        # make sure actually have mouse control
        hasMouse = mw.hasMouse()
        if hasMouse:
            #if mouse is inside, get x and y
            x, y = mw.getMouseX(), mw.getMouseY()
            if self.lastMouseX is not None:
                # get difference from last mouse to now
                if self.base.mouseMode is 1:
                    # if in mouseMode 1 (relative), position of cursor resets to center
                    # so what's reported by getMouseX,Y is already the delta from center
                    dx, dy = x, y
                else:
                    dx, dy = x - self.lastMouseX, y - self.lastMouseY
            else:
                # no data to compare with yet
                dx, dy = 0, 0
            self.lastMouseX, self.lastMouseY = x, y
        else:
            x, y, dx, dy = 0, 0, 0, 0

        # if in relative mode reset mouse to center
        if self.base.mouseMode is 1:
            self.base.win.movePointer(0,
                                      int(self.base.win.getProperties().getXSize() / 2),
                                      int(self.base.win.getProperties().getYSize() / 2))
            #reset lastMouse to 0,0 since everything will be relative from center
            self.lastMouseX, self.lastMouseY = 0, 0

        #rotate model by delta X
        self.actor.setH(self.actor.getH()-dx*60)
        #update camera to keep up
        #test - vertical shaking while moving
        self.camera.setPos(-2, 30, self.height*.75)
        #project vector from model and put camera there
        #camOffset=(0, -30,self.height)
        #rotate vector
        #first need to get angle (getH is cumulative degrees, not ideal for rotation)
        #playerAngle = (360-self.actor.getH())%360
        #now rotate
        #self.camera.setPos(player.getPos()+rotateVector(camOffset,playerAngle))
        #self.camera.lookAt(self.actor.getX(), self.actor.getY(), self.actor.getZ() + self.height / 2)


class vehicle(entity):
    '''
    Base class for vehicles
    Bipedal characters can inherit directly from entity but vehicle handling demands special attention
    '''
    pass