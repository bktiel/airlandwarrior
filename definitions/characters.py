from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import CollisionSphere, CollisionNode, CollisionHandlerQueue, CollisionRay, CollisionCapsule, \
    CollisionBox, CollideMask

from helper import pointInCircle, vectorToHPR
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
    def __init__(self,base,location,team):
        #assign what we know off the bat
        self.model="models/rifleman"
        self.viewRange=200  #used by application to determine what character can 'see'
        self.contacts=[]    #stores nearby objects
        self.target=None    #stores target
        self.team=team
        #make call to parent with this model
        entity.__init__(self, self.model, base, location)
        #add rifle to the rifleman, as one does
        self.weaponNode=self.exposeJoint(None, "modelRoot", "weaponNode")
        self.weapon=carbine(self, self.weaponNode)
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

        #clear current contacts to get new ones
        self.contacts.clear()
        #clear current target for the same reason
        self.target=None
        # get all objects within viewRange
        for item in base.entities:
            #sanity check
            if item.is_empty():
                base.entities.remove(item)
                continue
            if item is self:
                continue
            #otherwise retrieve other pos
            otherPos=item.getPos()
            if pointInCircle(self.getPos(),self.viewRange,otherPos) and item.team != self.team:
                #if within viewRange, it is a valid contact
                self.contacts.append(item)
        #if there are valid contacts
        if len(self.contacts)>0:
            #sort to get nearest
            # built in panda function compareTo apparently does what I need
            # seems to rate similarity but works for my purposes
            self.contacts.sort(key=lambda otherItem: self.getPos().compareTo(otherItem.getPos()))
            #target this object
            self.target=self.contacts[0]
            #little bit of vector math, get vector to target, normalize and convert to rotation
            newVec=self.target.getPos()-self.getPos()
            newVec.normalize()
            newVec=vectorToHPR(newVec)
            #now if currentHPR doesn't match add H until it does
            self.setH(newVec[0])
            self.attack()
        else:
            #if not attacking anything, default to high ready
            self.pose("highReady", 0)

    #procedure rifleman.attack
    #act of rifleman shooting. While shooting, can't do anything else
    def attack(self):
        self.weapon.fire()
        if self.weapon.isReloading != False:
            if self.getCurrentAnim() != "reload":
                self.play("reload")
        else:
            if self.getCurrentAnim() != "firing":
                self.loop("firing", restart=0)



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