class Box():
    '''
    A class that represents an nxn box around a seedpixel (x,y)
    '''
    def __init__(self, x: int, y: int, resolution: int):
        self.x_min = None
        self.x_max = None
        self.y_min = None
        self.y_max = None
        self.create_box(x, y, resolution)


    
    def create_box(self, x: int, y:int, resolution: int):
        size = resolution//2
        self.x_min, self.x_max = x-size, x+size
        self.y_min, self.y_max = y-size, y+size
