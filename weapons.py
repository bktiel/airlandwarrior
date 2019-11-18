class weapon():
    '''
    weapon class is any weapon used by any character/vehicle in world
    class contains model, projectile, range, noise, and mag size
    '''
    def __init__(self):
        pass

class M2(weapon):
    '''
    Browning 50 cal
    '''
    def __init__(self):
        weapon.__init__(self)

class TOWPod(weapon):
    '''
    TOW missile pod
    '''
    def __init__(self):
        weapon.__init__(self)
