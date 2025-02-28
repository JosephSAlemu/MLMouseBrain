import cv2
import json
import numpy as np
import matplotlib.pyplot as plt
from filter import get_all_chunks


def test() -> None:
    #If the voxels are within for 25 microns of each other do a Parawise Distance. Distance Matrix between

    #Density = number of nonblack pixels over 0 /all pixels (#pixels). 

    #Grab gene from section_dataset_id

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

    voxel_chunks = get_all_chunks()
    #section_images = get_section_images()

    section_image = int(101081691)

    #x_coords = []
    #y_coords =[]
    # NP arrange
    points = []

    for file in voxel_chunks:
        for row in file['Section_Image']:
            new_row = json.loads(row.replace("\'","\""))
            for ind in range(len(new_row)):
                id = new_row[ind]['image_sync']['section_image_id']
                id = int(id)
                if id == section_image:
                    print("match")
                    points.append( (   (int(new_row[ind]['image_sync']['x'])) , (int(new_row[ind]['image_sync']['y']))   ) )
    
    print(points)
    x_min = min(p[0] for p in points)
    x_max = max(p[0] for p in points)
    y_min = min(p[1] for p in points)
    y_max = max(p[1] for p in points)

    grid_x = np.arange(x_min - 25, x_max + 25, 50)
    grid_y = np.arange(y_min - 25, y_max + 25, 50)

    grid_points = [(x, y) for x in grid_x for y in grid_y]

    plot_width = (x_max - x_min) / 50  # Number of 50-inch segments in x
    plot_height = (y_max - y_min) / 50  # Number of 50-inch segments in y
    figsize_scale = 0.5  # Adjust this value to control overall figure size

    figsize = ((plot_width * figsize_scale)+50, plot_height * figsize_scale)  # Scale dynamically
    # Plot the grid points
    plt.figure(figsize=figsize)  # Set figure size
    plt.scatter(*zip(*points), marker='s', color='red', s=10, label="Given Points")

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
    plt.axis("equal")  # Fix aspect ratio to ensure correct spacing
    plt.show()

    # Print grid points
    print("Grid Points:", grid_points)







def draw_voxel_square() -> None:


    image = cv2.imread(r"./Datasets/SectionImages/SectionImage.jpg")
    window_name = "saggital slice"

    height, width, channels = image.shape
    print(f"height:{height} width:{width} channels:{channels}")

    x,y = int(7803.933909331148), int(3415.78197917279)

    start_point = (x-25, y-25)
    end_point =  (x+25, y+25)

    color = (255, 0, 0)
    thickness = 3

    image = cv2.rectangle(image, start_point, end_point, color, thickness)

    density = 2500

    for x in range(width):
        for y in range(height):
            # Get the BGR values of the pixel
            b, g, r = image[y,x]
            # Print the coordinates and color values of the pixel
            if b >= 150 or g >= 150 or r >= 150:
                print(f"Pixel at ({x}, {y}): B={b}, G={g}, R={r}")


    #filename = "result.jpg"

    #cv2.imwrite(filename, image)



test()