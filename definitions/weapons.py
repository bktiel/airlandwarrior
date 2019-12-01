from templates import weapon

class M1X_M2(weapon):
    '''
    Browning 50 cal truncated for M1X use
    '''
    def __init__(self):
        weapon.__init__(self)

    #procedure fire
    def fire(self):
        '''
        Create raycast from barrel of m2 for distance of range
        '''

class TOWPod(weapon):
    '''
    TOW missile pod
    '''
    def __init__(self):
        weapon.__init__(self)
