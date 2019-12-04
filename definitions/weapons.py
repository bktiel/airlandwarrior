from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import Vec3

from templates import weapon, bullet

global base

class M1X_M2(weapon):
    '''
    Browning 50 cal truncated for M1X use
    '''
    #take an owning nodepath
    #take a joint, load model onto joint
    #establish DPS and other characteristics
    #class constructor
    #Actor nodepath, JOINT nodepath -> weapon class rendered @ joint
    def __init__(self, owner, joint):
        self.model=base.loader.loadModel("models/m1xMG")
        self.damage = 1
        self.owner=owner    #the reason owner is specified is because projectiles will be fired towards that mesh's 'headgun' joint
        self.range=500
        self.ammo={
            'magSize':5,
            'reserve':20,
            'currentMag':5
        }
        # audio
        self.firingNoise=''
        self.reloadNoise=''
        # time to reload
        self.reloadTime=0
        # time that must pass between shots
        self.fireRate=0.1
        self.lastFired=0
        # boolean whether an instance is reloading - cannot fire if so
        self.isReloading=False

        #parent to joint
        self.model.reparentTo(joint)

        # get length of object
        min,max=self.model.getTightBounds()
        self.length=abs(max.getY()-min.getY())+1
        self.height = abs(max.getZ() - min.getZ()) + 1
        # this will be the Y offset for the firing solution

        #DEBUG
        owner.selectedWeapon=self
        print(owner.selectedWeapon)
    #procedure fire
    def fire(self):
        '''
        if owner is a player:
            Create projectile, play noise, decrement ammo counter
            Projectile goes towards joint owner.headgun
        otherwise just create projectile aimed at owner.target
        '''

        #check if time since last fired > firerate
        timeNow=globalClock.getFrameTime()
        if (timeNow-self.lastFired) < self.fireRate:
            # if difference is SMALLER than firerate, don't do anything - exit
            return

        #initialize variables
        targetVector=None
        startPos=None
        if self.owner.isPlayer:
            #get player headgun
            targetVector=base.render.getRelativeVector(self.owner.headgun,Vec3(0,1,0))

        #start pos should always be self.length from pos. Will experiment with
        # https://discourse.panda3d.org/t/calculating-forward-vector-from-hpr/6261/2
        startPos=base.render.getRelativePoint(self.model,Vec3(0,-self.length,-self.height/2))

        #create projectile at set offset in front of weapon
        bullet(
            startPos,
            targetVector,
            3,
            480,
            400
        )
        #record in lastFired
        self.lastFired=timeNow

class TOWPod(weapon):
    '''
    TOW missile pod
    '''
    def __init__(self):
        weapon.__init__(self)


###class for infantry rifle
class carbine(weapon):
    #constructor
    def __init__(self, owner, joint):
        self.owner=owner
        self.lastFired=0
        # time that must pass between shots
        self.fireRate=0.1
        self.ammo={
            'magSize':5,
            'reserve':20,
            'currentMag':5
        }
        #load model and render
        self.model = base.loader.loadModel("models/gun")
        self.model.reparentTo(joint)
        #for offset on firing solution
        min,max=self.model.getTightBounds()
        self.length=abs(max.getY()-min.getY())+1
        self.height = abs(max.getZ() - min.getZ()) + 1

    def fire(self):
        timeNow = globalClock.getFrameTime()
        if (timeNow - self.lastFired) < self.fireRate:
            # if difference is SMALLER than firerate, don't do anything - exit
            return
        #targetVector will be owner's target if AI

        #targetVector = base.render.getRelativeVector(self.owner.target, Vec3(0, 1, 0))
        startPos=base.render.getRelativePoint(self.model,Vec3(0,self.length,-self.height/2))
        targetVector=(self.owner.target.getPos() - startPos)
        targetVector.normalize()

        #create projectile at set offset in front of weapon
        bullet(
            startPos,
            targetVector,
            3,
            480,
            400
        )
        #record in lastFired
        self.lastFired=timeNow
