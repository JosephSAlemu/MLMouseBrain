import cv2
import re
import os
import csv
import numpy as np
import pandas as pd
from PIL import Image as pil, ImageDraw
from src.constants import DENSITY, CHUNK_HEADERS_V3
from src.voxel.voxel import Box
from typing import NewType
from src.utils.validation import is_valid

class Image():
    def __init__(self):
        pass

    def get_seed_voxels (self) -> None:
        '''
        Retrieves all the seed voxels
        '''
    
    def measure_gene_expression_density(self, box: Box, section_img_path: str, density: int) -> int:
        '''
        measures the gene expression given a Box and a section_image
        '''
        image = cv2.imread(section_img_path)
        
        height, width = image.shape[:2]

        if box.x_min < 0 or box.y_min < 0 or box.x_max > width or box.y_max > height:
            return -1

        image_box = image[box.y_min:box.y_max, box.x_min:box.x_max]

        expressed_mask = np.any(image_box > 0, axis=2)

        expressed_count = np.count_nonzero(expressed_mask)

        gene_expression = expressed_count / (density*density)
        return gene_expression
    

    def create_file(self, chunk_path: str, section_img_dir: str, dir_path: str, file_name: str = "mChunk", resolution: int = 50) -> None:
        '''
        Measures and creates a new chunk file with the corresponding gene_expression measurement.

        Args:
          chunk_path: Chunk File Path
          section_image_dir: Binarized Image Directory Path
          dir_path: Directory Path
          file_name: Name Of File 
          resolution: Resolution of the box to measure gene expression density

        Returns:
          None

        Modify this method to change the chunk file in place
        '''
        df = pd.read_csv(chunk_path)
        file_no = re.findall(r'\d+', chunk_path)[-1]
        file_name = f"{file_name}_{file_no}.csv"
        new_path = os.path.join(dir_path, file_name)

        with open(new_path, mode="w", newline="") as new_file:
            writer = csv.writer(new_file)
            writer.writerow(CHUNK_HEADERS_V3)
            for row in df.itertuples(index=False):
                box = Box(row.Seed_x, row.Seed_y, resolution)
                section_img = f"{row.Section_Image}.jpg"
                section_img_path = os.path.join(section_img_dir, section_img)
                gene_density = self.measure_gene_expression_density(box, section_img_path, resolution)
            
                arr = list(row) + [gene_density]
                writer.writerow(arr)
    
    def draw_box(self, section_image: str) -> None:
        '''
        Given a section image and coordinates, display an image 
        '''
        if not is_valid(section_image):
            img = pil.open(section_image)
            rect = ImageDraw.Draw(img)
            rect.rectangle([(500, 500), (600, 600)], outline='red', width=3)
            img.save("image.jpg")