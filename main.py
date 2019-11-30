from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from direct.fsm.FSM import FSM
from direct.showbase.DirectObject import DirectObject
from helper import *

from game import mainGame
from panda3d.core import TextNode


class MenuFSM(FSM):
    '''
    FSM = finite state machine, used to switch between states
    on the application level this will be between menu and the actual game
    each state is defined by <name>start and <name>exit as functions under the FSM class
    state change is prompted by the Showbase.messenger class, which generates events that FSM can self.accept

    MenuFSM handles switch between main menu interface and actual game (mission)
    '''
    #procedure class constructor
    def __init__(self):
        '''
        Defines transitions and sets up state machine for use by creating showBase instance
        and requesting first application screen
        '''
        # call to base class to cover all bases
        FSM.__init__(self, 'mainApp')
        #define allowable transitions
        self.defaultTransitions = {
            'Menu' : [ 'Game' ],
            'Game' : ['Menu']
            }
        global base
        #create instance of showBase to be used for the rest of the application
        base=ShowBase()

        #set window size
        winsize=WindowProperties()
        winsize.setSize(1024,600)
        base.win.requestProperties(winsize)

        #create objects
        self.menu=None
        self.mission=None
        #request first menu, and then run showBase (starts app)
        self.request('Menu')
        base.run()
    def enterMenu(self):
        #listen for Menu Start and request Game state if it is sent
        self.accept("Menu-Start", self.request, ['Game'])
        #if menu instance doesn't exist, create
        if self.menu is None:
            self.menu=mainMenu()
        #show menu
        self.menu.visible(True)
    def exitMenu(self):
        #make menu invisible
        self.menu.visible(False)
    def enterGame(self):
        #if there is no mission, create one
        if self.mission is None:
            self.mission=mainGame()
        #accept ESC to go back to menu
        self.accept("escape", self.request,['Menu'])
    def exitGame(self):
        #delete mission
        if self.mission is not None:
            del self.mission
            self.mission = None
        #set mouse mode
        setMouseMode(0)





class mainMenu():
    #procedure class constructor
    def __init__(self):
        '''
        Creates main menu GUI with level select
        '''
        # Add some text
        bk_text = "Demo"

        #create frame that covers entire frame - all controls will be parented to so it can be hidden all at once
        self.frameMain=DirectFrame(
            frameSize=(base.a2dLeft, base.a2dRight, base.a2dBottom, base.a2dTop)
        )


        # Add button
        self.makeButton("START DEMO",0,["Menu-Start"])
        #b = DirectButton(text=("OK", "click!", "rolling over", "disabled"), scale=.05, command=base.messenger.send, extraArgs=["Menu-Start"])

        #more buttons and objects to come for this GUI
        self.textObject = OnscreenText(text=bk_text, pos=(0.95, -0.95),
                                  scale=0.07, fg=(1, 0.5, 0.5, 1), align=TextNode.ACenter, mayChange=1)

    # procedure setTest
    # none -> none
    def setText(self):
        bk_text = "Button Clicked"
        self.textObject.setText(bk_text)
    # function makeButton
    # string text, float vertPos, string eventArgs -> DirectButton on frame
    def makeButton(self, text, vertPos, eventArgs):
        b = DirectButton(
            text=text,
            scale=.3,
            pos=(0,0,vertPos),
            command=base.messenger.send,
            extraArgs=eventArgs)
        b.reparentTo(self.frameMain)

    #procedure mainmenu.visible
    def visible(self,show=True):
        '''
        hides or shows main menu (useful for state manager)
        '''
        if show:
            self.frameMain.show()
        else:
            self.frameMain.hide()

# create instance of state manager
# constructor handles the rest
myFSM = MenuFSM()
