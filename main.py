from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task import Task
from direct.actor.Actor import Actor
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import PandaNode, NodePath, Camera, TextNode
from direct.interval.IntervalGlobal import Sequence
#all collision stuff
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerQueue, CollisionRay, CollideMask


class mainGame(ShowBase):
    '''
    mainGame class is the actual instance of the panda application, inherits from ShowBase
    it contains functions and methods to control flow - creation of menus, loading levels
    gameplay logic should go elsewhere
    '''
    def __init__(self):
        '''
        class construct
        :param self:
        :return:
        '''
        ShowBase.__init__(self)
        self.makeEnviron("example")

        #handle collisions
        #collision traversal 'traverses' instances of collides
        self.cTrav=CollisionTraverser()

        charles= entity("panda", self, (0, 40, 300))
        charles.gravity=True


    def makeEnviron(self,envModel):
        '''
        creates environment of specified name and parents to renderer
        :param envModel:
        :return:
        '''
        self.environment=self.loader.loadModel("models/"+envModel)
        self.environment.reparentTo(self.render)
        self.environment.setPos(0, 0, -20)

class entity():
    '''
    Base class for any characters
    Contains methods for movement, collision, model loading
    '''
    #NodePath model, ShowBase caller, tuple Pos -> class construction
    def __init__(self, model, instance, pos):
        '''
        constructor for entity. attaches model to calling instance renderer
        '''

        self.gravity=False
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
        self.groundRay = CollisionRay()
        self.groundRay.setOrigin(0, 0, self.height)
        self.groundRay.setDirection(0, 0, -1)
        #create panda3d collision node that will contain collision ray
        self.groundCol = CollisionNode('actorRay')
        self.groundCol.addSolid(self.groundRay)
        #specify valid collisions for collision node
        self.groundCol.setFromCollideMask(CollideMask.bit(0))
        self.groundCol.setIntoCollideMask(CollideMask.allOff())
        #attach collision node to actor
        self.groundColNode = self.actor.attachNewNode(self.groundCol)
        #create container for all valid collisions
        self.groundHandler = CollisionHandlerQueue()
        #finally, attach the ground collision node and a place to store collisions to the traverser
        instance.cTrav.addCollider(self.groundColNode, self.groundHandler)
        self.groundColNode.show()
        instance.cTrav.showCollisions(self.renderer)
        #add collision task to global task manager for this entity
        taskMgr.add(self.collide, "collideTask")

    #task: collides
    #None -> None
    def collide(self,task):
        '''
        Tasks are procedures that run every frame once they are called
        collide() checks for any collisions and adjusts actor as applicable
        '''
        #democode for gravity
        dt = globalClock.getDt()
        if self.gravity is True:
            self.actor.setZ(self.actor.getZ()-20*dt)
        #create list from all collisions detected by collisions container
        entries = list(self.groundHandler.getEntries())
        #sort entries by the Z value (height) of their collision
        entries.sort(key=lambda x: x.getSurfacePoint(self.renderer).getZ())
        #if actor is inside terrain, adjust Z so it is above the terrain
        print(entries)
        if len(entries) > 0 and entries[0].getIntoNode().getName() == "terrain":
            #get Z of the collision detected with terrain, set Z of actor above it
            #this way actor always stays above terrain
            self.actor.setZ(entries[0].getSurfacePoint(self.renderer).getZ())
        else:
            self.actor.setPos(self.actor.getPos())

        return task.cont

class vehicle(entity):
    '''
    Base class for vehicles
    Bipedal characters can inherit directly from entity but vehicle handling demands special attention
    '''
    pass


app=mainGame()
app.run()