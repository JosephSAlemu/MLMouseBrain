import numpy as np
import cv2
from src.constants import DENSITY
from src.voxel.voxel import Box
from typing import NewType

class Image():
    def __init__(self):
        pass

    def get_seed_voxels (self,) -> None:
        '''
        Retrieves all the seed voxels
        '''
    
    def measure_gene_expression_density(box: Box, section_image_path: str) -> int:
        '''
        measures the gene expression given a Box and a section_image
        '''
        image = cv2.imread(section_image_path)
        
        height, width = image.shape[:2]

        if box.x_min < 0 or box.y_min < 0 or box.x_max > width or box.y_max > height:
            return -1

        image_box = image[box.y_min:box.y_max, box.x_min:box.x_max]

        expressed_mask = np.any(image_box > 0, axis=2)

        expressed_count = np.count_nonzero(expressed_mask)

        gene_expression = expressed_count / DENSITY
        return gene_expression
    
    




