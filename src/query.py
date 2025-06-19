class QueryBuilder():
    def __init__(self):
        self.query = "http://api.brain-map.org/api/v2"

    def reset_query(self) -> None:
        self.query = "http://api.brain-map.org/api/v2"
        return self

    @reset_query
    def section_image(self) -> None:
        self.query += "/image_download/{image_id}"

    @reset_query 
    def binarized_section_image(self) -> None:
        self.section_image()
        self.query += "?view=expression"
    
    @reset_query
    def reference_to_image(self) -> None:
        self.reset_query()
        self.query += "/reference_to_image/{reference_id}.json?x={X}&y={Y}&z={Z}&section_data_set_ids={image_ids}"
    
    @reset_query
    def image_to_reference(self) -> None:
        self.query += "/image_to_reference/{section_image_id}.json?x={x_coord}&y={y_coord}"
    
if __name__ == "__main__":
    ob = QueryBuilder()
    ob.section_image()
    print(ob.query)

    ob.binarized_section_image()
    print(ob.query)