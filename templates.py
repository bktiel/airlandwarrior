#definitions for actors
from direct.showbase.ShowBase import ShowBase, CollisionHandlerEvent, LVector3f, Vec3, NodePath
from direct.showbase.ShowBaseGlobal import globalClock
from direct.actor.Actor import Actor
from direct.task.TaskManagerGlobal import taskMgr
import helper
# all collision stuff
from panda3d.core import CollisionNode, CollideMask, CollisionSphere



#presume use of global showbase object
global base
class entity():
    '''
    Base class for any characters
    Contains methods for movement, collision, model loading
    '''
    #procedure class constructor
    # NodePath model, ShowBase caller, tuple Pos -> class construction
    def __init__(self, model: str, base: ShowBase, pos: tuple) -> None:
        '''
        constructor for entity. attaches model to calling instance renderer
        also stores size definitions and creates basic collision object
        '''
        DEFAULT_HEALTH=50


        #reference base for later
        self.base = base

        # set health
        self.health=DEFAULT_HEALTH
        # speed
        self.speed=10

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
        self.mainCol.setIntoCollideMask(CollideMask.allOn())
        # attach collision node to actor
        self.cNode = self.actor.attachNewNode(self.mainCol)
        # show
        self.cNode.show()
        # make instance collision traverser aware of this collision node, tell it how to handle (with pusher)
        base.cTrav.addCollider(self.cNode, base.pusher)
        # add collision to pusher collision handler; tell pusher which node to associate with which actor IOT push
        base.pusher.addCollider(self.cNode, self.actor, base.drive.node())

        #add to cleanup for deletion later
        base.cleanup.append(self)

        # TODO if no initial collision, enforce gravity until collision

    #procedure add Damage
    #float dmg -> decrement self.health
    def addDamage(self, dmg):
        '''
        Adds a specified amount to this entity
        Can be negative or positive
        If self.health < 0 call delete self
        '''
        # TODO make pretty death
        self.health+=dmg
        if self.health <= 0:
            del self

    #procedure class deconstructor
    def __del__(self):
        '''
        Class destructor
        Destroy an object cleanly from instance
        '''
        #destroy actor
        self.actor.hide()
        self.actor.remove_node()
        self.actor.delete()
        #remove collision node from global collider
        base.cTrav.removeCollider(self.cNode)


class player(entity):
    '''
    player is a playable entity.
    it has movement methods to manipulate actor based on key input
    it has a camera task to keep camera in third person perspective
    '''

    # procedure class constructor
    # NodePath model, ShowBase caller, tuple Pos -> class construction
    def __init__(self, model, base, pos):
        '''
        class constructor
        calls parent constructor to set up model, renderer, position
        initializes camera to focus on player character
        sets mouse mode to relative
        '''
        entity.__init__(self, model, base, pos)
        # self turnSpeed and Speed
        self.speed=70
        self.turnSpeed=60

        # extra player specific stuff
        # store mouseX, mouseY
        self.lastMouseX, self.lastMouseY = None, None
        # isMobile used to determine if animation currently playing - default to false
        self.isMobile = False
        # isPlayer used to determine if a player
        self.isPlayer = False
        # camera init
        self.setPlayer()

        # initial loadout
        self.weapons=[]
        # store player's selected weapon
        self.selectedWeapon=None
        taskMgr.add(self.move,"playerMoveTask")

        #test values for m1X (no other playertypes at this time)
        #-10 prevents from looking too high (clips into pelvis)
        #32 keeps from going too low and making gaps in model visible
        self.traversalLimits=(-10,32)

    # procedure setPlayer
    # bool -> player assignment/not
    def setPlayer(self,state=True):
        '''
        method called to set an entity as the player
        if state=true, set camera to focus on this entity
        '''
        if state:
            # set to player
            self.isPlayer=True
            # store scene camera as property of this entity (since scene camera should be on the object)
            self.camera = base.camera
            self.keyMap= base.keyMap
            # expose camera bone from the model
            cameraBone = self.actor.exposeJoint(None, "modelRoot", "camera")
            self.camera.reparentTo(cameraBone)
            #get position of camera joint relative to the actor itself
            relPoint=self.actor.getRelativePoint(cameraBone, cameraBone.getPos())
            print(relPoint)
            self.camera.setPos(relPoint)
            self.camera.setHpr(0,90,0)

            self.neck=self.actor.controlJoint(None, "modelRoot", "neck")
            self.head = self.actor.controlJoint(None, "modelRoot", "head")
            # set camera to be 10 behind and 15% above
            #self.camera.setPos(self.actor.getX(), self.actor.getY()+3, self.actor.getZ()+self.height)
            #self.camera.lookAt(self.actor.getX(), self.actor.getY(), self.actor.getZ()+self.height)

            #set up player headgun (this is where most projectiles will be aimed)
            self.headgun=self.actor.exposeJoint(None, "modelRoot", "headgun")

    #task move
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
        if (self.keyMap["forward"] or self.keyMap["back"] or self.keyMap["left"] or self.keyMap["right"]):
            #isMobile tracks whether object is moving or not for other functions

            #TODO: direction specific animations
            #for now just loop walking
            if not self.isMobile:
                self.actor.loop("walk", restart=0)
                self.isMobile=True
            # for every direction that is true, move object that way
            # do the same with the camera
            if self.keyMap["forward"]:
                self.actor.setY(self.actor, - self.speed * dt)
                # camera too..
                #self.camera.setY(self.camera.getY() - 25 * dt)
            if self.keyMap["back"]:
                self.actor.setY(self.actor, + self.speed * dt)
                #self.camera.setY(self.camera.getY() + 25 * dt)

            if self.keyMap["left"]:
                #self.actor.setX(self.actor, + 100 * dt)
                self.actor.setH(self.actor.getH() + self.turnSpeed * dt)
                #counter movement of torso
                self.neck.setR(self.neck.getR() - self.turnSpeed * dt)
            if self.keyMap["right"]:
                #self.actor.setX(self.actor, - 100 * dt)
                self.actor.setH(self.actor.getH() - self.turnSpeed * dt)
                self.neck.setR(self.neck.getR() + self.turnSpeed * dt)

            # lastly if attempting move simulate gravity as well
            self.actor.setZ(self.actor.getZ() - 50 * dt)
        else:
            self.isMobile=False
            #otherwise stop walk animation
            self.actor.stop()
        #check if shooting, if so, shoot
        if self.keyMap['firing']:
            self.shoot()
        return task.cont

    #procedure updateCamera
    # none -> none
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
        #self.actor.setH(self.actor.getH() - dx * 60)

        #rotate just neck by delta x
        self.neck.setR(self.neck.getR()-dx*60)
        #rotate head for up down
        #set constraints for this
        if self.traversalLimits[0] < self.head.getP() - dy * 60 < self.traversalLimits[1]:
            self.head.setP(self.head.getP() - dy * 60)

        #update camera to keep up
        #test - vertical shaking while moving
        #self.camera.setPos(-2, 30, self.height*1.05)
        #project vector from model and put camera there
        #camOffset=(0, -30,self.height)
        #rotate vector
        #first need to get angle (getH is cumulative degrees, not ideal for rotation)
        #playerAngle = (360-self.actor.getH())%360
        #now rotate
        #self.camera.setPos(player.getPos()+rotateVector(camOffset,playerAngle))
        #self.camera.lookAt(self.actor.getX(), self.actor.getY(), self.actor.getZ() + self.height / 2)

    # procedure player.shoot
    def shoot(self):
        '''
        Fire primary weapon
        '''
        #fire selected weapon
        self.selectedWeapon.fire()

        #https://discourse.panda3d.org/t/calculating-forward-vector-from-hpr/6261/2
        #targetVector=base.render.getRelativeVector(self.headgun,Vec3(0,1,0))

        #bullet(
        #    base.render.getRelativePoint(self.headgun,Vec3(0,2,0)),
        #    targetVector,
        #    3,
        #    480,
        #    400
        #)



    #class deconstructor
    def __del__(self):
        entity.__del__(self)
        self.actor.removeEpstein()


class vehicle(player):
    '''
    Base class for vehicles
    Bipedal characters can inherit directly from entity but vehicle handling demands special attention
    '''
    pass

class bullet():
    #tuple pos, tuple target, float damage, float speed, float range, float accuracy -> bullet
    def __init__(self, pos, dir, damage, speed, range, accuracy=1):
        #bullets have a speed, a model, and a damage. Both should be parameters
        #range as well
        self.start=pos
        self.accuracy=accuracy
        self.direction=dir.normalized()
        self.damage=damage
        self.speed=speed
        self.range=range
        self.model=base.loader.loadModel('models/bullet')
        self.model.reparentTo(base.render)
        self.model.setPos(pos)

        #self.target=target
        #create collision sphere
        #TODO account for larger bullet sizes
        cs = CollisionSphere(0, 0, 0, 1)
        self.cNode=self.model.attachNewNode(CollisionNode('cNode'))
        self.cNode.node().addSolid(cs)
        #create collider handler, if one doesn't already exist
        try:
            # attempt to add to global collision traverser
            base.cTrav.addCollider(self.cNode, base.bulletCollider)
        except AttributeError:
            base.bulletCollider=CollisionHandlerEvent()
            # create event called 'bulletCollision' on hit
            base.bulletCollider.addInPattern('bulletCollision')
        finally:
            # retry
            base.cTrav.addCollider(self.cNode, base.bulletCollider)

        #rotate model such that it follows the passed direction argument vector
        self.model.setHpr(
            helper.vectorToHPR(dir)
        )

        #assign direction based on rotation
        #THIS TOOK WAY TOO MUCH EFFORT TO FIGURE OUT
        #normVec here is the model nodepath taking the passed argument vector (dir)
        #belonging to another node (base.render)
        #and adjusting it to its local coordinate space - what would this vector look like from
        #self.model's perspective. Then it is normalized and assigned.
        normVec=self.model.getRelativeVector(base.render,dir)
        normVec.normalize()
        self.direction=normVec

        #normVec=base.render.getRelativeVector(self.model,Vec3(0,1,0))
        #print(self.model.getHpr())
        #print(normVec)


        #start task to move forward at speed
        taskMgr.add(self.accelerate, "bulletAccelerateTask")

    #task: accelerate
    def accelerate(self, task):
        """
        Task moves bullet forward until it hits an object or range is met
        """
        #range is decremented each tick
        #check to make sure not 0
        if self.range <=0:
            #if range has ran out kill task and this object
            self.model.removeNode()
            return task.done

        #otherwise proceed, move object and decrement range
        dt=globalClock.getDt()

        #distVec=min((self.start-self.target),(self.target-self.start))
        #distVec=distVec.normalized()
        #print(distVec)
        #print(self.direction)
        #take normalized direction vector and apply to transform
        self.model.setFluidX(self.model, self.direction[0] * self.speed * dt)
        self.model.setFluidY(self.model, self.direction[1] * self.speed * dt)
        self.model.setFluidZ(self.model, self.direction[2] * self.speed * dt)
        self.range-=(self.speed*dt)
        return task.cont

class weapon():
    '''
    weapon class is any weapon used by any character/vehicle in world
    class contains model, projectile, range, noise, and mag size
    '''
    # passed targetJoint to attach to
    def __init__(self,targetJoint):
        # weapons are more than just data - each weapon has a 3D representation that must be loaded in and rendered
        # properties that specify model, texture, sound are specified as defaults to be switched by children
        self.model=base.loader.loadModel("models/example")
        self.damage = 1
        self.range=10
        self.ammo={
            'magSize':5,
            'reserve':20,
            'currentMag':5
        }
        self.firingNoise=''
        self.reloadNoise=''
        self.reloadTime=0
        self.isReloading=False #boolean whether an instance is reloading - cannot fire if so

        #make visible and attach
        self.model.reparentTo(targetJoint)
    # procedure reload
    def reload(self):
        '''
        Reload self.ammo['currentMag'] from available ammo
        '''
        # if greater than 0 action is possible
        # also make sure that not doubling up on action - should not be isReloading either
        if not self.isReloading and self.ammo['reserve']>0:
            self.isReloading=True
            self.ammo['currentMag']+=min(self.ammo['reserve'],self['magSize'])
            self.ammo['reserve']-=self.ammo['currentMag']
        else:
            #TODO notify reload failed and user needs ammmmmoooo
            pass
    #procedure fire
    def fire(self):
        '''
        Firing behavior defined here. Each weapon should typically check for ammo,
        decrement, and then perform some kind of behavior
        A basic gun makes just a raycast, an effect, and then does self.damage to first entity in collision
        '''
        pass



