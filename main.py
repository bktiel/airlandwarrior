from direct.showbase.ShowBase import ShowBase, CollisionHandlerPusher, Point3
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task import Task
from direct.actor.Actor import Actor
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import PandaNode, NodePath, Camera, TextNode
from direct.interval.IntervalGlobal import Sequence
#all collision stuff
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerQueue,\
    CollisionRay, CollideMask, CollisionSphere,CollisionHandlerPusher


class mainGame(ShowBase):
    '''
    mainGame class is the actual instance of the panda application, inherits from ShowBase
    it contains functions and methods to control flow - creation of menus, loading levels
    gameplay logic should go elsewhere
    '''
    def __init__(self):
        '''
        class construct
        '''
        #initialize
        ShowBase.__init__(self)


        #handle collisions
        #collision traversal 'traverses' instances of collides
        self.cTrav=CollisionTraverser()
        self.pusher=CollisionHandlerPusher()

        #load environment
        self.makeEnviron("example")

        charles= entity("panda", self, (0, 60, -20))

    def makeEnviron(self,envModel):
        '''
        creates environment of specified name and parents to renderer
        '''
        self.environment=self.loader.loadModel("models/"+envModel)
        self.environment.reparentTo(self.render)
        self.environment.setPos(0, 0, -10)

class entity():
    '''
    Base class for any characters
    Contains methods for movement, collision, model loading
    '''
    #NodePath model, ShowBase caller, tuple Pos -> class construction
    def __init__(self, model: str, instance: ShowBase, pos: tuple) -> None:
        '''
        constructor for entity. attaches model to calling instance renderer
        '''
        #creates actor object using constructor and parents to passed renderer
        self.actor = Actor(model)
        self.renderer = instance.render
        self.actor.reparentTo(self.renderer)
        #put at specified location
        self.actor.setPos(pos)
        #store dimensions for later
        #https://discourse.panda3d.org/t/getting-the-height-width-and-length-of-models-solved/6504
        minimum, maximum = self.actor.getTightBounds()
        #make sure all numbers are positive for best (any) results
        self.bounds = [abs(num) for num in (minimum - maximum)]
        self.width, self.length, self.height = self.bounds[0], self.bounds[1], self.bounds[2]

        #COLLISION PROPERTIES
        #create collision ray that is height of model pointing down (will detect ground collisions)
        self.mainCol = CollisionNode('actorCollision'+str(id(self)))
        #create collision sphere as solid for this collision node
        self.mainCol.addSolid(CollisionSphere(0, 0, self.height/2, self.height/2))
        #specify valid collisions for collision node
        self.mainCol.setFromCollideMask(CollideMask.bit(0))
        self.mainCol.setIntoCollideMask(CollideMask.allOff())
        #attach collision node to actor
        self.cNode = self.actor.attachNewNode(self.mainCol)
        #show
        self.cNode.show()
        #make instance collision traverser aware of this collision node, tell it how to handle (with pusher)
        instance.cTrav.addCollider(self.cNode, instance.pusher)
        #add collision to pusher collision handler; tell pusher which node to associate with which actor IOT push
        instance.pusher.addCollider(self.cNode, self.actor, instance.drive.node())

        #if no initial collision, enforce gravity until collision
    def destroy(self):
        '''
        Destroy an object cleanly from instance
        '''
        self.actor.delete()

class player(entity):
    '''
    player is a playable entity.
    it has movement methods to manipulate actor based on key input
    it has a camera task to keep camera in third person perspective
    '''
    def __init__(self, model, instance, pos):
        '''
        class constructor
        calls parent constructor to set up model, renderer, position
        initializes camera to focus on player character
        sets up key mappings w: forward, s: back, a: left, d: right
        sets mouse mode to relative
        '''
        entity.__init__(self, model, instance, pos)
        #extra player specific stuff

    def move(self,task):
        '''
        Called every frame - if w,a,s,d pressed, move self.actor accordingly
        If mouse location different and not in a menu, rotate actor by delta radians
        Adjust camera to keep up with move
        '''
class vehicle(entity):
    '''
    Base class for vehicles
    Bipedal characters can inherit directly from entity but vehicle handling demands special attention
    '''
    pass


app=mainGame()
app.run()