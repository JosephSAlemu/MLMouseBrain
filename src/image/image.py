
class Image():
    def __init__(self):
        pass

    def get_seed_voxels (self,) -> None:
        '''
        Retrieves all the seed voxels
        '''
    
    def measure_gene_expression_density(x_min: int, x_max: int, y_min: int, y_max: int, section_image_id: str) -> int:
        '''
        measures the gene expression given a 
        
        '''

        """
        measure a the density for a section image given a section_image_id, x_min & x_max for the width, and a y_min & y_max for the height

        if the mins is less than zero or the max-1 (where range stops) is greater than the image, then return None
        """
        image = cv2.imread(f"./Datasets/SectionImages/{section_image_id}.jpg")
        
        height, width = image.shape[:2]

        print(height, width, x_min, x_max, y_min, y_max, section_image_id)
        if x_min < 0 or y_min < 0 or x_max > width or y_max > height:
            return None

        # Extract the region of interest (ROI)
        roi = image[y_min:y_max, x_min:x_max]

        # Create a boolean mask of pixels where any channel is non-zero
        expressed_mask = np.any(roi > 0, axis=2)

        # Count the number of "expressed" pixels
        expressed_count = np.count_nonzero(expressed_mask)

        # Calculate density
        gene_expression = expressed_count / DENSITY
        return gene_expression
