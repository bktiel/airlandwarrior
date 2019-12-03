from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import CollisionSphere, CollisionNode, CollisionHandlerQueue, CollisionRay, CollisionCapsule, \
    CollisionBox, CollideMask

from templates import entity,player,vehicle
from definitions.weapons import *

global base
#define characters

class rifleman(entity):
    '''
    Basic rifleman
    '''
    #class constructor
    #mostly similar to entity
    def __init__(self,base,location):
        #assign what we know off the bat
        self.model="models/rifleman"
        self.viewRange=400
        #make call to parent with this model
        entity.__init__(self, self.model, base, location)
        #add rifle to the rifleman, as one does
        self.weaponNode=self.exposeJoint(None, "modelRoot", "weaponNode")
        carbine(self, self.weaponNode)
        self.pose("highReady",0)

        #make collision sphere as 'radar' of sorts
        radarNode = CollisionNode('radar')
        self.contacts=CollisionHandlerQueue()
        cs=CollisionSphere(0,0,0,self.viewRange/2)
        #radarNode.setFromCollideMask(CollideMask.bit(3))
        radarNode.setIntoCollideMask(CollideMask.bit(3))
        self.radar=self.attachNewNode(radarNode)
        self.radar.node().addSolid(cs)
        #self.radar.show()
        base.cTrav.addCollider(self.radar,self.contacts)



       # taskMgr.add(self.orders,'riflemanOrdersTask')

    def orders(self,task):
        return task.cont

class tank(vehicle):
    '''
    Basic tank
    '''
    pass

class helo(vehicle):
    '''
    Helicopter gunship
    '''
    pass

class turret(entity):
    '''
    Defensive turret
    '''
    pass