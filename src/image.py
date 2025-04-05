import cv2
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
import time
from matplotlib.patches import Rectangle
from filter import (get_all_chunks, group_data, get_section_dataset_ids)
from validation import is_valid_image
from constants import DENSITY
import matplotlib.image as mpimg




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

    p4_file = pd.read_csv(r"./Datasets/Outputs/P4_Section_Data.csv")

    voxel_chunks = get_all_chunks()
    # You have to loop through each dataset_id
    # For each section dataset id, you need to loop through the number of valid section image id's.
    for incrementor in range(1):
        
        lst = list(map(int, p4_file.iloc[incrementor]["Images"].strip("{}").split(", ")))
        # Second loop for all the section images associated with the section_dataset_id
        for ind in range(len(lst)):
            section_image = lst[ind]

            #x_coords = []
            #y_coords =[]
            # NP arrange
            points = []

            #Basically get all the section images with a specific id across all chunks (ALL TOTAL SECTION IMAGES) and store their points.
            for file in voxel_chunks:
                for row in file['Section_Image']:
                    new_row = json.loads(row.replace("\'","\""))
                    for ind in range(len(new_row)):
                        id = new_row[ind]['image_sync']['section_image_id']
                        id = int(id)
                        if id == section_image:
                            print("match")
                            points.append((   (new_row[ind]['image_sync']['x']) , (new_row[ind]['image_sync']['y'])  ))

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

            print(valid_boxes)
            seed_points = [((p[0][0]+p[0][1])//2, (p[1][0]+p[1][1])//2) for p in valid_boxes]

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
            plt.title(f"{p4_file.iloc[incrementor]["Gene"]}: {section_image}")
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

    voxel_chunks = get_all_chunks()

        # Second loop for all the section images associated with the section_dataset_id

            #x_coords = []
            #y_coords =[]
            # NP arrange
    points = []

            #Basically get all the section images with a specific id across all chunks (ALL TOTAL SECTION IMAGES) and store their points.
    for file in voxel_chunks:
        for row in file['Section_Image']:
            new_row = json.loads(row.replace("\'","\""))
            for ind in range(len(new_row)):
                id = new_row[ind]['image_sync']['section_image_id']
                id = int(id)
                if id == section_image_id:
                    points.append((   (new_row[ind]['image_sync']['x']) , (new_row[ind]['image_sync']['y'])  ))

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
    return(valid_boxes)
        


def test() -> None:
    file = pd.read_csv(r"./Datasets/Outputs/P4_Section_Data.csv")
    #converts string to a list of integers
    row = file.loc[file["Gene"] == "Tcf21"]
    print(row["Images"][0])


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


def calculate_density(gene: str) -> None:
    '''
    This function takes in a gene (section_dataset_id) and does the following:
    1. retrieve the section image id's attached to that section_dataset_id
    2. downloads the binarized section images using their id's
    3. retrieve all valid boxes from a function (currently called plot function)
    4. use those box coordinates as bounds and measure density in each valid box.
    '''
    density_measurements = []

    p4_file = pd.read_csv(r"Datasets\Outputs\P4_Section_Data.csv")
    row = p4_file.loc[p4_file["Gene"] == gene]

    lst = list(map(int, row["Images"][0].strip("{}").split(", ")))
    for section_image_id in lst:
        #load image if not present. If present, does nothing.
        binarized_image(section_image_id)
        image = cv2.imread(rf"./Datasets/SectionImages/{section_image_id}.jpg")

        height, width, channels = image.shape
        print(f"height:{height} width:{width} channels:{channels}")

        boxes = get_valid_boxes(section_image_id)

        #Reminder: ( (min_x,max_x),(min_y,max_y) )
        for box in boxes:
            start_points = (box[0][0],box[1][0])
            end_points = (box[0][1],box[1][1])

            expressed = 0

            print(f"coord are {box}")
            print(f"start_x is {start_points[0]} end_x is {end_points[0]}")
            print(f"start_y is {start_points[1]} end_y is {end_points[1]}")
    
            for x in range(start_points[0], end_points[0]):
                for y in range(start_points[1], end_points[1]):
                    # Get the BGR values of the pixel
                    b, g, r = image[y,x]
                    # Print the coordinates and color values of the pixel

                    if b > 0 or g > 0 or r > 0:
                        #print(f"Pixel at ({x}, {y}): B={b}, G={g}, R={r}")
                        expressed+=1
            density_measurements.append(expressed/DENSITY)


            #filename = "result.jpg"

            #cv2.imwrite(filename, image)
    print(density_measurements)
    print(len(density_measurements))


def timing() -> None:
    start_time = time.perf_counter()
    calculate_density("Tcf21")
    end_time = time.perf_counter()
    execution_time = end_time - start_time

    print(f"Execution time: {execution_time} seconds")


plot()