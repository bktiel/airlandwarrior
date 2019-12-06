#definitions for actors
from direct.showbase.MessengerGlobal import messenger
from direct.showbase.ShowBase import ShowBase, CollisionHandlerEvent, LVector3f, Vec3, NodePath
from direct.showbase.ShowBaseGlobal import globalClock
from direct.actor.Actor import Actor
from direct.task.TaskManagerGlobal import taskMgr

import helper

# all collision stuff
from panda3d.core import CollisionNode, CollideMask, CollisionSphere, CollisionRay, BitMask32, CollisionHandlerQueue, \
    LVector3

#presume use of global showbase object
global base

class entity(Actor):
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
        Actor.__init__(self)
        DEFAULT_HEALTH=50

        #reference base for later
        self.base = base

        # set health
        self.health=DEFAULT_HEALTH
        self.damagedSound=base.loader.loadSfx("sounds/oof.ogg")

        # speed
        self.speed=10
        self.turnSpeed=5
        # gravity -- is touching ground?
        self.isGrounded=False
        # creates actor object using constructor and parents to passed renderer
        self.loadModel(model)
        self.renderer = base.render
        self.reparentTo(self.renderer)
        # put at specified location
        self.setPos(pos)
        # store dimensions for later
        # https://discourse.panda3d.org/t/getting-the-height-width-and-length-of-models-solved/6504
        minimum, maximum = self.getTightBounds()
        # make sure all numbers are positive for best (any) results
        self.bounds = [abs(num) for num in (minimum - maximum)]
        self.width, self.length, self.height = self.bounds[0], self.bounds[1], self.bounds[2]


        # COLLISION PROPERTIES
        # create collision ray that is height of model pointing down (will detect ground collisions)

        self.groundRay = CollisionRay()
        self.groundRay.setOrigin(0,0,1000)
        self.groundRay.setDirection(0,0,-1)
        self.groundCol = CollisionNode('groundRay')
        self.groundCol.addSolid(self.groundRay)
        self.groundCol.setFromCollideMask(BitMask32.bit(0))
        self.groundCol.setIntoCollideMask(BitMask32.allOff())
        self.groundColNode = self.attachNewNode(self.groundCol)
        base.cTrav.addCollider(self.groundColNode, base.groundHandler)

        #and another one for everything else
        self.mainCol = CollisionNode('actorCollision' + str(id(self)))
        # create collision sphere as solid for this collision node
        self.mainCol.addSolid(CollisionSphere(0, 0, self.height / 2, self.height / 2))
        # specify valid collisions for collision node
        self.mainCol.setFromCollideMask(CollideMask.bit(0))
        self.mainCol.setIntoCollideMask(CollideMask.bit(1)) # accepts incoming objects with collideMask bit(1)
        # attach collision node to actor
        self.cNode = self.attachNewNode(self.mainCol)
        # show
        #self.cNode.show()
        # make instance collision traverser aware of this collision node, tell it how to handle (with pusher)
        base.cTrav.addCollider(self.cNode, base.pusher)
        # add collision to pusher collision handler; tell pusher which node to associate with which actor IOT push
        base.pusher.addCollider(self.cNode, self, base.drive.node())

        # add to base.entities (since all allies/enemies created through this constructor, makes sense
        base.entities.append(self)
        # add as client of entity collision handler
        # base.cTrav.addCollider(self.cNode,base.entityCollisionHandler)

        #add to cleanup for deletion later
        base.cleanup.append(self)

        #store reference to self
        #https://discourse.panda3d.org/t/inheriting-from-nodepath/10886/4
        self.mainCol.setPythonTag("owner",self)

        # TODO if no initial collision, enforce gravity until collision
        #taskMgr.add(self.doGravity, "entityGravity")

    #procedure update
    #do all actions that must be done for this object every frame - called from game loop
    def updateState(self):
        #by default do gravity for all entities
        self.doGravity()
        return

    #procedure entityGravity
    # drops entity by gravity if isGrounded is not true (set True by collision with ground)
    def doGravity(self):
        dt = globalClock.getDt()
        #gravity - if not grounded, make it so
        if not self.isGrounded:
            self.setZ(self.getZ() - 50 * dt)
            return
        else:
            entries = []
            for entry in base.groundHandler.getEntries():
                if entry.getFromNodePath().getParent() == self \
                        or entry.getIntoNodePath().getParent() == self:
                    entries.append(entry)
            if (len(entries) > 0) and (entries[0].getIntoNode().getName() == "terrain"):
                self.setZ(entries[0].getSurfacePoint(base.render).getZ()+2)

    #procedure add Damage
    #float dmg -> decrement self.health
    def addDamage(self, sender, dmg):
        '''
        Adds a specified amount to this entity
        Can be negative or positive
        If self.health < 0 call delete self
        '''
        #get shooter for scoring purposes
        shooter=sender.owner
        # TODO make pretty death
        self.health-=dmg
        if self.damagedSound is not None:
            self.damagedSound.play()
        if self.health <= 0:
            #if shooter was player, add to score
            if shooter is base.player:
                if shooter.team is self.team:
                    base.player.score-=15
                else:
                    base.player.score+=15
            #if player, end game
            if self is base.player:
                messenger.send('Leave-Game')
            self.kill()

    #procedure kill
    # destroys object, but fancy-like
    def kill(self):
        self.pose('death',0)
        taskMgr.add(self.deleteTask,'deleteTask')

    #procedure deleteTask
    #destroys object after five seconds of being in death state
    def deleteTask(self,task):
        if task.time<5.0:
            return task.cont
        else:
            self.delete()
            return task.done

    #procedure class deconstructor
    def delete(self):
        '''
        Class destructor
        Destroy an object cleanly from instance
        '''
        #also remove from base.entities
        if self in base.entities:
            base.entities.remove(self)

        # remove pythontag from collision
        self.mainCol.clearPythonTag("owner")
        # remove collision node from global collider
        base.cTrav.removeCollider(self.cNode)
        #destroy actor
        if not self.is_empty():
            self.hide()
            self.cleanup()
            #self.detachNode()
            del self

    #class deconstructor
    def __del__(self):
        self.removeNode()



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
        self.turnSpeed=120
        self.team=0

        # extra player specific stuff
        # store mouseX, mouseY
        self.lastMouseX, self.lastMouseY = None, None
        # isMobile used to determine if animation currently playing - default to false
        self.isMobile = False
        # isPlayer used to determine if a player
        self.isPlayer = False
        # camera init
        self.setPlayer()

        self.health=600
        self.damagedSound=None

        # initial loadout
        self.weapons=[]
        # store player's selected weapon
        self.selectedWeapon=None
        #taskMgr.add(self.move,"playerMoveTask")
        base.entities.append(self)

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
            cameraBone = self.exposeJoint(None, "modelRoot", "camera")
            self.camera.reparentTo(cameraBone)
            #get position of camera joint relative to the actor itself
            relPoint=self.getRelativePoint(cameraBone, cameraBone.getPos())
            print(relPoint)
            self.camera.setPos(relPoint)
            self.camera.setHpr(0,90,0)

            self.neck=self.controlJoint(None, "modelRoot", "neck")
            self.head = self.controlJoint(None, "modelRoot", "head")
            # set camera to be 10 behind and 15% above
            #self.camera.setPos(self.getX(), self.getY()+3, self.getZ()+self.height)
            #self.camera.lookAt(self.getX(), self.getY(), self.getZ()+self.height)

            #set up player headgun (this is where most projectiles will be aimed)
            self.headgun=self.exposeJoint(None, "modelRoot", "headgun")

    #task move
    def updateState(self):
        '''
        Called every frame - if w,a,s,d pressed, move self accordingly
        If mouse location different and not in a menu, rotate actor by delta radians
        Adjust camera to keep up with move
        '''
        # call parent
        entity.updateState(self)
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
                self.loop("walk", restart=0)
                self.isMobile=True
            # for every direction that is true, move object that way
            # do the same with the camera
            if self.keyMap["forward"]:
                self.setY(self, - self.speed * dt)
                # camera too..
                #self.camera.setY(self.camera.getY() - 25 * dt)
            if self.keyMap["back"]:
                self.setY(self, + self.speed * dt)
                #self.camera.setY(self.camera.getY() + 25 * dt)

            if self.keyMap["left"]:
                #self.setX(self, + 100 * dt)
                self.setH(self.getH() + self.turnSpeed * dt)
                #counter movement of torso
                self.neck.setR(self.neck.getR() - self.turnSpeed * dt)
            if self.keyMap["right"]:
                #self.setX(self, - 100 * dt)
                self.setH(self.getH() - self.turnSpeed * dt)
                self.neck.setR(self.neck.getR() + self.turnSpeed * dt)

            # lastly if attempting move simulate gravity as well
            #self.setZ(self.getZ() - 50 * dt)
        else:
            self.isMobile=False
            #otherwise stop walk animation
            self.stop()
        #check if shooting, if so, shoot
        if self.keyMap['firing']:
            self.shoot()
        #return task.cont

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
        #self.setH(self.getH() - dx * 60)

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
        #playerAngle = (360-self.getH())%360
        #now rotate
        #self.camera.setPos(player.getPos()+rotateVector(camOffset,playerAngle))
        #self.camera.lookAt(self.getX(), self.getY(), self.getZ() + self.height / 2)

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
        pass
        #self.removeEpstein()



class vehicle(player):
    '''
    Base class for vehicles
    Bipedal characters can inherit directly from entity but vehicle handling demands special attention
    '''
    pass

class bullet():
    #tuple pos, tuple target, float damage, float speed, float range, float accuracy -> bullet
    def __init__(self, sender, pos, dir, damage, speed, range, accuracy=1):
        #bullets have a speed, a model, and a damage. Both should be parameters
        #range as well
        self.start=pos
        self.sender=sender
        self.accuracy=accuracy
        self.direction=dir.normalized()
        self.damage=damage
        self.tasks=[]
        self.speed=speed
        self.range=range
        self.model=base.loader.loadModel('models/bullet')
        self.model.reparentTo(base.render)
        self.model.setPos(pos)

        #self.target=target
        #create collision sphere
        #TODO account for larger bullet sizes
        cs = CollisionSphere(0, 0, 0, 1)
        self.mainCol=CollisionNode('cNode')
        #set up circular reference so collision volume knows parent
        self.mainCol.setPythonTag('owner',self)
        self.mainCol.setIntoCollideMask(CollideMask.bit(1)) # send objects with intoCollideMask bit 1. Relates to most entities
        self.cNode=self.model.attachNewNode(self.mainCol)
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
        self.tasks.append(taskMgr.add(self.accelerate, "bulletAccelerateTask"))

    #task: accelerate
    def accelerate(self, task):
        """
        Task moves bullet forward until it hits an object or range is met
        """
        #range is decremented each tick
        #check to make sure not 0
        if self.range <=0:
            #if range has ran out kill task and this object
            self.delete()
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

    #class deconstructor
    def delete(self):
        self.model.hide()
        #clear tasks
        for task in self.tasks:
            taskMgr.remove(task)
        #clear collision
        self.mainCol.clearPythonTag("owner")
        #remove object
        self.model.removeNode()

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



