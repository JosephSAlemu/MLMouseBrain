class QueryBuilder():
    def __init__(self):
        self.query = "http://api.brain-map.org/api/v2/"
    
    def section_image(self)-> None:
        self.query +="image_download/{}?view=expression"