from direct.task.TaskManagerGlobal import taskMgr
from panda3d.ai import AICharacter
from panda3d.core import CollisionSphere, CollisionNode, CollisionHandlerQueue, CollisionRay, CollisionCapsule, \
    CollisionBox, CollideMask, LVector3f

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
        #TODO chosen model currently depends on team - 0 is friendly, 1 is enemy
        if team==0:
            self.model = "models/friend_rifleman"
        elif team==1:
            self.model="models/enemy_rifleman"
        self.viewRange=400  #used by application to determine what character can 'see'
        self.contacts=[]    #stores nearby objects
        self.target=None    #stores target
        self.goal=None      #stores movement goal (if any)
        self.team=team
        #make call to parent with this model
        entity.__init__(self, self.model, base, location)
        #add rifle to the rifleman, as one does
        self.weaponNode=self.exposeJoint(None, "modelRoot", "weaponNode")
        self.weapon=carbine(self, self.weaponNode)
        self.pose("highReady",0)

        #add AI to this object
        #mass 60, movement force 0.05, max force 25
        self.ai=AICharacter(str(self), self, 30, 0.05, 25)
        base.AIworld.addAiChar(self.ai)
        self.AiBehaviors=self.ai.getAiBehaviors()
        #load navmesh
        self.AiBehaviors.initPathFind(base.navmesh)
        #add all structures
        for building in base.structures:
            #this is super aggressive so disable for now..
            #self.AiBehaviors.addStaticObstacle(building)
            pass

    #procedure: updateState
    #overrides entity.updateState
    #things that need to be executed every frame for this character object
    def updateState(self):

        # if health below 0 is dead
        if self.health<=0:
            self.AiBehaviors.removeAi("pathfollow")
            self.mainCol.clearSolids()
            return
        entity.updateState(self)
        timeNow = globalClock.getFrameTime()
        #rifleman should always stand upright.
        self.setP(0)
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
            #TODO currently drop everything to shoot at something if in range
            self.AiBehaviors.pauseAi("pathfollow")
            #sort to get nearest
            # built in panda function compareTo apparently does what I need
            # seems to rate similarity but works for my purposes
            self.contacts.sort(key=lambda otherItem: self.getPos().compareTo(otherItem.getPos()))
            #target this object
            self.target=self.contacts[0]
            #little bit of vector math, get vector to target, normalize and convert to rotation
            newVec=self.getPos()-self.target.getPos()
            newVec.normalize()
            newVec=vectorToHPR(newVec)
            #now if currentHPR doesn't match add H until it does
            self.setH(newVec[0])
            self.attack()
        elif self.weapon.isReloading != False:
            if timeNow >= self.weapon.isReloading:
                self.weapon.isReloading = False
                self.weapon.ammo['currentMag'] = self.weapon.ammo['magSize']
        elif self.goal is not None:
            self.setGoal(self.goal)
        elif self.goal is None:
            #if not moving or attacking anything, default to high ready
            self.pose("highReady", 0)

        #handle movement if there is a goal and not shooting anyone
        if self.goal is not None and self.target is None and self.weapon.isReloading is False:
            self.move()

    #procedure rifleman.attack
    #act of rifleman shooting. While shooting, can't do anything else
    def attack(self):
        self.weapon.fire()
        #this is False because isReloading stores the start time of the reload
        if self.weapon.isReloading != False:
            if self.getCurrentAnim() != "reload":
                self.play("reload")
        else:
            if self.getCurrentAnim() != "firing":
                self.loop("firing")

    #procedure setGoal
    #sets a location target for this character to move to
    def setGoal(self,goal):
        self.goal=goal
        # go to a specific area
        self.AiBehaviors.pathFindTo(self.goal)

    #procedure move
    #if en route to a location, play walking animation
    def move(self):
        #set position every move
        self.set_prev_transform(self.getTransform(base.render))
        #if completed set to none, reset animations
        if self.AiBehaviors.behaviorStatus("pathfollow") == "done":
            self.goal=None
            self.pose("highReady", 0)
            return
        dt = globalClock.getDt()

        if self.getCurrentAnim() != "walk":
            self.loop("walk")






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