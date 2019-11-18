from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from direct.fsm.FSM import FSM
from direct.showbase.DirectObject import DirectObject

from game import mainGame
from panda3d.core import TextNode

#FSM = finite state machine, used to switch between states
#on the application level this will be between menu and the actual game
class MenuFSM(FSM):
    def __init__(self):
        FSM.__init__(self, 'mainApp')
        self.defaultTransitions = {
            'Menu' : [ 'Game' ],
            'Game' : ['Menu']
            }
        global base
        #create instance of showBase to be used for the rest of the application
        base=ShowBase()

        #create objects
        self.menu=mainMenu()

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
        print('exiting')
        self.menu.visible(False)
    def enterGame(self):
        men=mainGame()




class mainMenu():
    def __init__(self):
        #ShowBase.__init__(self)
        # Add some text
        bk_text = "This is my Demo"

        self.frameMain=DirectFrame(
            frameSize=(base.a2dLeft, base.a2dRight, base.a2dBottom, base.a2dTop)
        )

        # Add button
        self.makeButton("OK",0,["Menu-Start"])
        #b = DirectButton(text=("OK", "click!", "rolling over", "disabled"), scale=.05, command=base.messenger.send, extraArgs=["Menu-Start"])

        self.textObject = OnscreenText(text=bk_text, pos=(0.95, -0.95),
                                  scale=0.07, fg=(1, 0.5, 0.5, 1), align=TextNode.ACenter, mayChange=1)

    # Callback function to set  text
    def setText(self):
        bk_text = "Button Clicked"
        self.textObject.setText(bk_text)
    def makeButton(self, text, vertPos, eventArgs):
        b = DirectButton(
            text=text,
            scale=.05,
            pos=(0,0,vertPos),
            command=base.messenger.send,
            extraArgs=eventArgs)
        b.reparentTo(self.frameMain)

    def visible(self,show=True):
        if show:
            self.frameMain.show()
        else:
            self.frameMain.hide()


myFSM = MenuFSM()
