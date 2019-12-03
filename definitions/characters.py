from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import CollisionSphere, CollisionNode, CollisionHandlerQueue, CollisionRay, CollisionCapsule, \
    CollisionBox, CollideMask

from helper import pointInCircle
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
        self.viewRange=200  #used by application to determine what character can 'see'
        #make call to parent with this model
        entity.__init__(self, self.model, base, location)
        #add rifle to the rifleman, as one does
        self.weaponNode=self.exposeJoint(None, "modelRoot", "weaponNode")
        carbine(self, self.weaponNode)
        self.pose("highReady",0)

        #make collision sphere as 'radar' of sorts
        #radarNode = CollisionNode('radar')
        #self.radarQueue=CollisionHandlerQueue()
        #cs=CollisionSphere(0,0,0,self.viewRange/2)
        #radarNode.setFromCollideMask(CollideMask.bit(3))
        #radarNode.setIntoCollideMask(CollideMask.bit(3))
        #self.radar=self.attachNewNode(radarNode)
        #self.radar.node().addSolid(cs)
        #self.radar.show()
        #base.cTrav.addCollider(self.radar,self.radarQueue)

        #taskMgr.add(self.update,'riflemanUpdateTask')

    #procedure: updateState
    #overrides entity.updateState
    #things that need to be executed every frame for this character object
    def updateState(self):
        #first get all collisions from radarQueue handler
        #for entry in self.radarQueue.getEntries():
        #    victim=entry.getIntoNodePath()
        #    victimParent=victim.getPythonTag('owner')
        #    if 'terrain' not in victim.name \
        #    and (victim.parent != self.radar.parent)\
        #    and (victimParent != None):
        #        print(entry)
        entity.updateState(self)

        # get all objects within viewRange
        for item in base.entities:
            #sanity check
            if item is self: continue
            #otherwise retrieve other pos
            otherPos=item.getPos()
            if pointInCircle(self.getPos(),self.viewRange,otherPos):
                pass

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