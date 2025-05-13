import cv2
import csv
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
import time
import ast
import os
import paramiko
from typing import Type
from matplotlib.patches import Rectangle
from math import modf
from filter import (get_all_chunks, group_data, get_section_dataset_ids, read_chunk_files, create_sub_voxel_dataframe)
from validation import (is_valid_image, is_valid_p4_voxel_gene)
from constants import DENSITY, P4_MOUSE_REFERENCE_ID
from api import (image_to_reference, upload_file, directories, reference_to_image)
import matplotlib.image as mpimg


"""p4_image_coords = pd.read_csv(r"Datasets/Outputs/P4_Image_Coords.csv")
p4_file = pd.read_csv(r"Datasets/Outputs/P4_Section_Data.csv")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(os.getenv("DOMAIN"), username=os.getenv("USERNAME"), password=os.getenv("PASSWORD"), compress=True)

sftp = client.open_sftp()"""
def plot() -> None:

    '''
    1. Start with left most and top most seed pixel. (mainly top most location)
    2. Find next closest pixel that's atleast 50 microns along the x axis.
    3. go all the way across to the right most pixel
    4. then you go down 50 microns and then move to the left
    5. then you go all the way to left on the x axis that's atleast 50 microns away
    6. So on so forth until you reach the bottom most right or bottom most left 
    7. Have a buffer of possibly 5 pixels to find any actual seed pixels.

    or

    1. get the seed pixel locations and calculate any overlapping seed values
    2. Then calculate density afterwards

    or
    1. take the extrema of the x and y and divide that rectangle into 50 um bins, and then any bin with a seed pixel is one that you count.

    2. the y values of the top-most and bottom-most seed pixels and the x values of the left-most and right-most seed pixels

    '''



    # You have to loop through each dataset_id
    # For each section dataset id, you need to loop through the number of valid section image id's.
    for incrementor in range(1):
        
        lst = list(map(int, p4_file.iloc[incrementor]["Images"].strip("{}").split(", ")))
        print(lst)
        # Second loop for all the section images associated with the section_dataset_id
        for ind in range(len(lst)):
            section_image_id = lst[ind]

            #x_coords = []
            #y_coords =[]
            # NP arrange
            points = []

            row = p4_image_coords.loc[p4_image_coords["Image"] == section_image_id]
            row = row["Coordinates"].iloc[0]
            print(row)
            row = ast.literal_eval(row)
            for coord in row:
                points.append(coord)


            if len(points) > 1:
                x_min = min(p[0] for p in points)
                x_max = max(p[0] for p in points)
                y_min = min(p[1] for p in points)
                y_max = max(p[1] for p in points)

            else:
                x_min = x_max = points[0][0]
                y_min = y_max = points[0][1]
                x_min-=25
                y_min-=25
                x_max+=25
                y_max+=25

            print(f"ymin = {y_min}, ymax = {y_max}, xmin = {x_min}, xmax = {x_max}")

            grid_x = np.arange(x_min, x_max+50, 50)
            grid_y = np.arange(y_min, y_max+50, 50)

            _, ax = plt.subplots()


            print(f"X bins: {len(grid_x)}\n\n")
            print(f"Y bins: {len(grid_y)}\n")

            # Keep track of of the x coordinates and y coordinates in a tuple of tuples
            # For example ((xmin,xmax),(ymin,ymax))
            # Check which x tuple and y tuple a seed point falls into.

            boxes = []

            for i in range(1, len(grid_x)):
                min_x, max_x = int(grid_x[i-1]) , int(grid_x[i])
                for i in range(1, len(grid_y)):
                    min_y, max_y = int(grid_y[i-1]) , int(grid_y[i])
                    boxes.append( ((min_x,max_x),(min_y,max_y)) )
                
            # Take the seed pixels and check that their coordinates falls within the bounds of a box.
            # If a seed pixel falls in the bounds of a box, then put those coords in a new array (valid_boxes)
            # From that valid_boxes array, calculate the density from each tuple of tuples.


            # Binary search for coordinate since they are ordered.
            # Append the result, the int index of the answer, in the array
            valid_boxes = set()
            #Check if points length > 1 otherwise binary search doesn't work.
            if len(points) > 1:
                for seed in points:
                    index = binary_search(boxes, len(grid_y)-1, seed)
                    dilated = binary_dilation(boxes, len(grid_y)-1, index)
                    valid_boxes.update(dilated)
            else:
                valid_boxes.update(boxes)
            print(valid_boxes)
            seed_points = [((p[0][0]+p[0][1])/2, (p[1][0]+p[1][1])/2) for p in valid_boxes]

            plt.scatter(*zip(*points), marker='s', color='red', s=10, label="Seed Points")
            if len(points) > 1:
                plt.scatter(*zip(*seed_points), marker='s', color='blue', s=10, label="Dilated Points")

            # Draw grid lines
            for x in grid_x:
                plt.axvline(x, color='gray', alpha=0.5)
            for y in grid_y:
                plt.axhline(y, color='gray', alpha=0.5)

            # Labels and settings
            plt.xlabel("X-axis (Micron)")
            plt.ylabel("Y-axis (Micron)")
            plt.xticks(grid_x, rotation=45)  # Show ticks at grid positions
            plt.yticks(grid_y)
            plt.grid(True, which='both', linewidth=0.5)
            plt.legend()
            plt.axis("equal")  
            plt.title(f"{p4_file.iloc[incrementor]['Gene']}: {section_image_id}")
            plt.show(block=False)
            plt.pause(0.1)
            # Fix aspect ratio to ensure correct spacing
            # Print grid points
            #print("Grid Points:", grid_points)

            #VERIFY THAT THE DILATION WORKED BY ADDING BLUE POINTS TO THE CENTER OF EVERY BOX POST DILATION
    plt.show()


def get_valid_boxes(section_image_id: str) -> list[tuple,tuple]:
    '''
    Takes in a section_image_id
    retrieves the section_dataset_id associated with the gene
    finds all the section images associated with that section_dataset_id
    finds all the seed pixels
    binary dilates all the seed pixels
    has an array of all the valid boxes.
    '''


        # Second loop for all the section images associated with the section_dataset_id

            #x_coords = []
            #y_coords =[]
            # NP arrange
    points = []
    row = p4_image_coords.loc[p4_image_coords["Image"] == section_image_id]
    row = row["Coordinates"].iloc[0]
    #print(row)
    row = ast.literal_eval(row)
    for coord in row:
        points.append(coord)

    #print(points)
    

    if len(points) > 1:
        x_min = min(p[0] for p in points)
        x_max = max(p[0] for p in points)
        y_min = min(p[1] for p in points)
        y_max = max(p[1] for p in points)

    else:
        x_min = x_max = points[0][0]
        y_min = y_max = points[0][1]
        x_min-=25
        y_min-=25
        x_max+=25
        y_max+=25

    grid_x = np.arange(x_min, x_max+50, 50)
    grid_y = np.arange(y_min, y_max+50, 50)

            # Keep track of of the x coordinates and y coordinates in a tuple of tuples
            # For example ((xmin,xmax),(ymin,ymax))
            # Check which x tuple and y tuple a seed point falls into.

    boxes = []

    for i in range(1, len(grid_x)):
        min_x, max_x = int(grid_x[i-1]) , int(grid_x[i])
        for i in range(1, len(grid_y)):
            min_y, max_y = int(grid_y[i-1]) , int(grid_y[i])
            boxes.append( ((min_x,max_x),(min_y,max_y)) )
                
            # Take the seed pixels and check that their coordinates falls within the bounds of a box.
            # If a seed pixel falls in the bounds of a box, then put those coords in a new array (valid_boxes)
            # From that valid_boxes array, calculate the density from each tuple of tuples.


            # Binary search for coordinate since they are ordered.
            # Append the result, the int index of the answer, in the array
    valid_boxes = set()
            #Check if points length > 1 otherwise binary search doesn't work.
    if len(points) > 1:
        for seed in points:
            index = binary_search(boxes, len(grid_y)-1, seed)
            dilated = binary_dilation(boxes, len(grid_y)-1, index)
            valid_boxes.update(dilated)
    else:
        valid_boxes.update(boxes)

    return(valid_boxes)
        

def binarized_image(section_image: int) -> None:
    '''
    download the binarized image if it's not present
    '''
    
    if is_valid_image(section_image):
        path = rf"./Datasets/SectionImages/{section_image}.jpg"
        url = rf"http://api.brain-map.org/api/v2/image_download/{section_image}?view=expression"
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(path, "wb") as file:
            for chunk in response:
                file.write(chunk)


def retrieve_binarized_image(section_image: int) -> None:
    """
    Retreves all the gene files in the remote linux server and puts it into New_Voxels directory
    """


    local_path = "Datasets/SectionImages"
    remote_path = os.getenv("IMAGE_DEST_PATH")

    file = f"{section_image}.jpg"
    
    remote = os.path.join(remote_path, file)
    local = os.path.join(local_path, file)

    sftp.get(remote, local)


def binary_search(boxes: list[(tuple,tuple)], section: int, seed: tuple) -> int:
    '''
    Given a list of box coordinates (a tuple of tuples), return the index where the seed pixel fits in

    if you find an index where the x coordinate fits, find which indexes of the array where the x value stays the same but the y value differs.
    '''
    low, high = 0, len(boxes)-1
    x_ind = -1
    ans_ind = -1
    while low <= high:
        middle = (low+high)//2
        if boxes[middle][0][0] > seed[0]:
            high = middle - 1
        elif boxes[middle][0][1] < seed[0]:
            low = middle + 1
        elif boxes[middle][0][0] <= seed[0] and boxes[middle][0][1] >= seed[0]:
            x_ind = middle
            low = high+1

    subset = x_ind//section
    low, high = subset*section, ((subset+1)*section)-1
    while low <= high:
        middle = (low+high)//2
        if boxes[middle][1][0] > seed[1]:
            high = middle - 1
        elif boxes[middle][1][1] < seed[1]:
            low = middle + 1
        elif boxes[middle][1][0] <= seed[1] and boxes[middle][1][1] >= seed[1]:
            ans_ind = middle
            low = high +1

    return ans_ind


def binary_dilation(boxes: list[(tuple,tuple)], section: int, index: int, ) -> list[(tuple,tuple)]:
    '''
    Takes the list of boxes, section (number of y axis so we can jump like C 2d Arrays), and seed index (index)

    For each seed box coordinate, make each box within a 7x7 radius a valid box that we count density from
    '''

    index_box = []
    dilated_boxes = []
    seed_box = boxes[index]
    index_box.append(index)
    dilated_boxes.append(boxes[index])
    # Check 4 on the right. Ensure it doesn't pass boundaries.
    for i in range(1,4):
        up = index+i
        down = index-i
        #right = index+(section*i)
        #left = index-(section*i)

        if up < len(boxes) and boxes[up][0] == seed_box[0]:
            index_box.append(up)
            dilated_boxes.append(boxes[up])

        if down > -1 and boxes[down][0] == seed_box[0]:
            index_box.append(down)
            dilated_boxes.append(boxes[down])

    for seed in index_box:
        for i in range(1,4):
            right = seed+(section*i)
            left = seed-(section*i)
            
            if right < len(boxes) and boxes[right][1] == boxes[seed][1]:
                dilated_boxes.append(boxes[right])

            if left > -1 and boxes[left][1] == boxes[seed][1]:
                dilated_boxes.append(boxes[left])

    return dilated_boxes


def calculate_density_and_voxels(gene: str) -> None:
    '''
    Purpose: It takes P4 section images + seed pixels -> P4 Voxel + P4

    This function takes in a gene and does the following:
    1. retrieve the section images id's associated with that gene
    2. downloads the binarized section images using their id's
    3. retrieve all valid boxes/bins from a function (binary dilation)
    4. convert each bin to a voxel while also measuring the density in that bin.
    5. assign voxel to density measured in a bin on a genes section image
    '''

    headers = [
        "Image",
        "Bin",
        "X",
        "Y",
        "Z",
        "Density_2500"
    ]
    path = fr"./Datasets/Outputs/New_Voxels/{gene}.csv"
    with open(path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)

        row = p4_file.loc[p4_file["Gene"] == gene]

        lst = list(map(int, row.iloc[0]["Images"].strip("{}").split(", ")))
        for section_image_id in lst:
            #load image if not present. If present, does nothing.
            binarized_image(section_image_id)
            image = cv2.imread(f"./Datasets/SectionImages/{section_image_id}.jpg")
            
            #width = x
            #height = y
            height, width, channels = image.shape

            boxes = get_valid_boxes(section_image_id)            


            #Reminder: ( (min_x,max_x),(min_y,max_y) )
            for box in boxes:
                x_min, x_max = box[0][0], box[0][1]
                y_min, y_max = box[1][0], box[1][1]
                gene_expression = measure_density(x_min, x_max, y_min, y_max, image)

                if gene_expression is None:
                    #if the points are out of bounds of the image itself, skip this bin.
                    writer.writerow([section_image_id, box, "error", "error", "error", "error"])

                else:
                    centroid_x = (x_min+x_max)/2
                    centroid_y = (y_min+y_max)/2
                    voxel = image_to_reference(section_image_id, centroid_x, centroid_y)
                    x,y,z = voxel
                    writer.writerow([section_image_id, box, x, y, z, gene_expression])

    upload_file(path, f"{gene}.csv")


def bin_voxels() -> None:
    """
    Takes in a gene name as a string.

    Opens the file and retrieves the voxels.

    Bin all the voxels in all the files in the genes they belong to.

    Bins are a 9x9 grid based on the x and y value.

                         ___________
              n.0-n.33  |___|___|___|
    (X Coord) n.34-n.66 |___|___|___|
              n.67-n.99 |___|___|___|
                        n.0  n.34 n.67 
                        -    -    -
                        n.33 n.66 n.69
                          (Y Coord)

    ALSO binned on the rounded z coordinate binned
        
    """

    headers = [
        "X",
        "Y",
        "Z",
        "Density_2500"
    ]
    file = pd.read_csv("Datasets/Outputs/P4_Section_Data.csv")
    for gene in file["Gene"]:
        gene_file = pd.read_csv(f"Datasets/Outputs/New_Voxels/{gene}.csv")
        with open(f"Datasets/Outputs/Binned_Voxels/{gene}.csv", "w", newline="") as new_file:
            writer = csv.writer(new_file)
            writer.writerow(headers)
            values = {}

            for _,row in gene_file.iterrows():
                x = row["X"]
                y = row["Y"]
                z = row["Z"]
                density = row["Density_2500"]
                image = row["Image"]
                if x != "error":
                    x = float(x)
                    y = float(y)
                    z = float(z)
                    density = float(density)
                    x_rem,x_num = modf(x)
                    y_rem,y_num = modf(y)
                    new_z = round(z)
                    coords = None
                    if x_rem < .34:
                        new_x = x_num
                        if y_rem < .34:
                            new_y = y_num

                        elif y_rem >= .34 and y_rem <.67:
                            new_y = y_num + .34

                        elif y_rem >= .67:
                            new_y = y_num + .67
                            
                        coords = (new_x, new_y, new_z)
                        if coords not in values:
                            values[coords] = []
                        og_coords = (x,y,z,density)
                        values[coords].append(og_coords)

                    elif x_rem >= .34 and x < .67:
                        new_x = x_num+.34
                        if y_rem < .34:
                            new_y = y_num
                    
                        elif y_rem >= .34 and y_rem <.67:
                            new_y = y_num + .34
                        
                        elif y_rem >= .67:
                            new_y = y_num + .67
                            
                        coords = (new_x, new_y, new_z)
                        if coords not in values:
                            values[coords] = []
                        og_coords = (x,y,z,density)
                        values[coords].append(og_coords)

                    elif x_rem >= .67:
                        new_x = x_num+.67
                        if y_rem < .34:
                            new_y = y_num
                        
                        elif y_rem >= .34 and y_rem <.67:
                            new_y = y_num + .34
                        
                        elif y_rem >= .67:
                            new_y = y_num + .67

                        coords = (new_x, new_y, new_z)
                        if coords not in values:
                            values[coords] = []
                        og_coords = (x,y,z,density)
                        values[coords].append(og_coords)
            values = average_voxels(values)
            print(values)
            for key,value in values.items():
                writer.writerow([key[0], key[1], key[2], value])


def average_voxels(binned_voxels:dict) -> dict:
    """
    Iterate over the values for each key in binned_voxel

    density = length of tuple -1

    (53.67, 30.67, 20): [(53.963118106190564, 30.997476532337647, 20.406354464995584, 0.0), (53.93815451183082, 30.683001395965636, 20.409561177057633, 0.1852)]
    
    """

    return_dict = {}
    for key, value in binned_voxels.items():
        print(key)
        density = 0
        for voxel in value:
            density+= voxel[len(voxel)-1]

            print(density)
        density = density/len(value)
        return_dict[key] = density
    return return_dict


def fill_negative_density(file_num: int, start: int, stop: int) -> None:
    """
    takes in a file_num for the P4 Section Laptop file and a start/stop for threads

    Purpose: for each 7535 voxels x 259 genes (gene splits), divide 7535 by n for m voxels for n threads.
    Example: for the p4_section_laptop_1, we may have split 7535 by 11 (threads) to get 11 calls to this method of 685 voxels each for the same file.
    """
    # open the voxel master file and the p4_Section_laptop file
    # for each voxel, iterate over the genes in each p4_Section_laptop file
    # if the value is -1, put that section_id from the p4_Section_laptop file into the array
    p4_laptop = pd.read_csv(f"Datasets/Outputs/P4_Section_Laptop{file_num}.csv")

    voxel = pd.read_csv("Datasets/Outputs/P4_50_NewDenS.csv")

    section_ids = []

    while start <= stop:
        index = voxel.index[start]
        for _, gene in p4_laptop.iterrows():
            if voxel.loc[index, gene["Gene"]] == -1:
                section_ids.append(gene["Section_Dataset_Id"])
        # Run through API here
        X = voxel.loc[index, "X"]
        Y = voxel.loc[index, "Y"]
        Z = voxel.loc[index, "Z"]
        reference_to_image(X, Y, Z, P4_MOUSE_REFERENCE_ID, section_ids, start, file_num)
        section_ids = []
        start+=1


def measure_density(x_min: int, x_max: int, y_min: int, y_max: int, image: Type[cv2]) -> int | None:
    """
    measure a the density for a section image given a section_image_id, x_min & x_max for the width, and a y_min & y_max for the height

    if the mins is less than zero or the max-1 (where range stops) is greater than the image, then return None
    """
    
    height, width, channels = image.shape
    print(f"height: {height} width: {width}")

    if x_min < 0 or y_min < 0 or x_max-1 > width or y_max-1 > height:
        return None
    
    expressed = 0
    for x in range(x_min, x_max):
        for y in range(y_min, y_max):
            b, g, r = image[y,x]

            if b > 0 or g > 0 or r > 0:
                expressed+=1

    gene_expression = expressed/DENSITY
    return gene_expression
    

def get_expressions(file_num: int, start: int, stop: int) -> dict:
    """
    takes start and stop for threads.
    7535
    
    returns a dictionary of
    key: voxels coordinates (x,y,z)
    value: an array of gene name and gene expression value (gene, gene_expression)

    if the point is in the bounds of the image and a density can be measured put it in
    """


    chunks = {}

    file = pd.read_csv(f"Datasets/Outputs/Fill_Negatives/laptops/P4_Voxel_Laptop{file_num}.csv")
    while start <= stop:
        print(start)
        key = ast.literal_eval(file.loc[start, "Voxel"])
        print(key)
        val = ast.literal_eval(file.loc[start, "Section_Data"])
        chunks[key] = val
        start+=1
    # Now download the image and then
    print(len(chunks))
    result = {}
    for key, value in chunks.items():
        result[key] = []
        print(f"\n\n{key}\n\n")
        for section in value:
            gene = section[0]
            section_image_id = section[1]
            X = section[2]
            Y = section[3]
            x_min, x_max = X-25, X+25
            y_min, y_max = Y-25, Y+25
            print(((x_min, x_max),(y_min, y_max)))
            binarized_image(section_image_id)
            
            image = cv2.imread(rf"./Datasets/SectionImages/{section_image_id}.jpg")

            gene_expression = measure_density(x_min, x_max, y_min, y_max, image)

            print(gene_expression)
            if gene_expression is None:
                print(f"error on {key}: {section}")
            else:
                result[key].append((gene, gene_expression))
            
    #fill the rest of the headers with the rest of the columns values
    path = f"Datasets/Outputs/Fill_Negatives/dataframes/P4_50_NewDenS_Laptop{file_num}.csv"

    create_sub_voxel_dataframe(path)

    dataframe = pd.read_csv(path)
    """
    iterate over key value pairs of the dictionary, 
    """
    for coordinate, expression in result.items():
        X = coordinate[0]
        Y = coordinate[1]
        Z = coordinate[2]
        gene = expression[0]
        gene_expression = expression[1]

        X_col = dataframe["X"] == X
        Y_col = dataframe["Y"] == Y
        Z_col = dataframe["Z"] == Z
        coords = X_col & Y_col & Z_col

        dataframe.loc[coords, gene] = gene_expression

    dataframe.to_csv(path, index=False)


def execute() -> None:
    """
    Deprecated method
    """
    #directories()
    file = pd.read_csv(rf"./Datasets/Outputs/P4_Section_Laptop{number}.csv")
    for gene in file["Gene"]:
        if is_valid_p4_voxel_gene(gene):
            calculate_density_and_voxels(gene)

