class QueryBuilder():
    def __init__(self):
        self.url = "http://api.brain-map.org/api/v2"

    def reset_url(func):
        def wrapper(self, *args, **kwargs):
            self.url = "http://api.brain-map.org/api/v2"
            return func(self, *args, **kwargs)
        return wrapper
    
    @reset_url
    def section_image(self) -> None:
        self.url += "/image_download/{image_id}"
        
    @reset_url
    def binarized_section_image(self) -> None:
        self.section_image()
        self.url += "?view=expression"
    
    @reset_url
    def reference_to_image(self) -> None:
        self.url += "/reference_to_image/{reference_id}.json?x={X}&y={Y}&z={Z}&section_data_set_ids={image_ids}"
    
    @reset_url
    def image_to_reference(self) -> None:
        self.url += "/image_to_reference/{section_image_id}.json?x={x_coord}&y={y_coord}"


