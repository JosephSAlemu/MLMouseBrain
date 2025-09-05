class SeedPixel():
    '''
    a class that represents a seed pixel
    '''
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

class Box():
    '''
    A class that represents the box around a seedpixel on a 2D ISH image
    '''
    def __init__(self, seed_pixel: SeedPixel):
        self.x_min = None
        self.x_max = None
        self.y_min = None
        self.y_max = None
        self.seed_pixel = seed_pixel
    
    def create_box(self, resolution: int):
        size = resolution//2
        self.x_min, self.x_max = self.seed_pixel.x-size, self.seed_pixel.x+size
        self.y_min, self.y_max = self.seed_pixel.y-size, self.seed_pixel.y+size
