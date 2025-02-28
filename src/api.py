import pandas as pd
import requests
import json
import csv
import os
#from filter import filter_data


count = 0

voxel = 0

headers = [
"X","Y","Z"
]

def api_calls() -> None:
    ...



def download_section_images() -> None:

    file = pd.read_csv(r"./Datasets/Outputs/Chunks/P4_Chunk_0.csv")
    #print(len(file['Section_Image']))
    trues = 0
    falses = 0
    i = 0
    for row in file['Section_Image']:
        new_row = json.loads(row.replace("\'","\""))
        for chunk in new_row:
            section_image = chunk['image_sync']['section_image_id']
            if is_valid_image(int(section_image)):
                image = open(rf"./Datasets/SectionImages/{section_image}.jpg", "wb")
                url = rf"http://api.brain-map.org/api/v2/image_download/{section_image}?view=expression"
                response = requests.get(url).content
                image.write(response)
                image.close()
                

def is_valid_image(section_image: int) -> bool:
    path = rf"./Datasets/SectionImages/{section_image}.jpg"
    if os.path.exists(path):
        return False
    return True


def structure_to_image() -> None:
    global count
    file = pd.read_csv(r'C:\Users\jojoa\Downloads\Motorola_Research\ExcelScript\Datasets\Outputs\NewDenC_Microns.csv')

    #max = len(file['X'])
    while count <= len(file['X']):
        fifty_chunk(file['X'][count], file['Y'][count], file['Z'][count])
        count+=1
   
def chunk(X: int, Y: int, Z: int ) -> None:
    global count
    global voxel
    list = []
    chunk_headers = [
        "Voxel", "Section_Image"
    ]
    if is_valid_path():
        created_file = rf"./Datasets/Outputs/Chunks/P4_Chunk_{count}.csv"
        with open(r'./Datasets/Inputs/section_dataset_ids_reference_6_sagittal.txt') as file, open(created_file, mode ="a", newline="") as new_file:
            writer = csv.writer(new_file)
            writer.writerow(chunk_headers)
            
            for line in file:
                if len(list) == 100:
                    url = f"http://api.brain-map.org/api/v2/reference_to_image/10.json?x={X}&y={Y}&z={Z}&section_data_set_ids={','.join(map(str, list))}"
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = f"{response.json()['msg']}"
                        writer.writerow([count, data])
                        list = []
                    else:
                        print(f"ISSUE WITH QUERY {url}")
                else:
                    list.append(int(line))
            url = f"http://api.brain-map.org/api/v2/reference_to_image/10.json?x={X}&y={Y}&z={Z}&section_data_set_ids={','.join(map(str, list))}"
            response = requests.get(url)
            data = f"{response.json()['msg']}"
            writer.writerow([count, data])
            list = []
            
            voxel+=1

def fifty_chunk(X: int, Y: int, Z: int ) -> None:
    global count
    global voxel
    counter = 0
    list = []
    chunk_headers = [
        "Voxel", "Section_Image"
    ]
    if is_valid_path():
        created_file = rf"./Datasets/Outputs/Test/P4_Chunk_{count}.csv"
        with open(r'./Datasets/Inputs/section_dataset_ids_reference_6_sagittal.txt') as file, open(created_file, mode ="a", newline="") as new_file:
            writer = csv.writer(new_file)
            writer.writerow(chunk_headers)
            
            for line in file:
                if len(list) == 50:
                    url = f"http://api.brain-map.org/api/v2/reference_to_image/10.json?x={X}&y={Y}&z={Z}&section_data_set_ids={','.join(map(str, list))}"
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = f"{response.json()['msg']}"
                        writer.writerow([count, data])
                        list = []
                    else:
                        print(f"ISSUE WITH QUERY {url}")
                    break
                else:
                    list.append(int(line))
                    counter+=1
            
            voxel+=1
    print(f"done {counter}")

def is_valid_path() -> bool:
    global count
    path = rf"./Datasets/Outputs/Test/P4_Chunk_{count}.csv"
    print(path)
    if os.path.exists(path):
        return False
    return True



def multiply_coordinate_for_microns() -> None:
    """
    takes all the p-56 voxel coordinates and converts them to microns by multiplying them by 200

    Then, it runs it through the API

    """
    file = pd.read_csv(r'C:\Users\jojoa\Downloads\Motorola_Research\ExcelScript\Datasets\Inputs\NewDenC.csv')
    file['X'] = file['X'] * 200
    file['Y'] = file['Y'] * 200
    file['Z'] = file['Z'] * 200
    
    file.to_csv(r'C:\Users\jojoa\Downloads\Motorola_Research\ExcelScript\Datasets\Outputs\NewDenC_Microns.csv', index = False)

def image_to_structure(p5_voxel: int) -> None:
    """
    takes all the p-4 section images associated with a p-56 voxels [1465 voxels]

    p5_voxel values: 0 to 1464 (inclusive)

    """

    data = filter_data(p5_voxel)
    #r"./Datasets/Outputs
    file = f"./Datasets/Outputs/New_result{p5_voxel}.csv"
    with open(file, mode ="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for mouse in data:
            x = mouse['image_sync']['x']
            y = mouse['image_sync']['y']
            section_image = mouse['image_sync']['section_image_id']
            url = f"http://api.brain-map.org/api/v2/image_to_reference/{section_image}.json?x={x}&y={y}"
            response = requests.get(url)
            if response.status_code == 200:
                data = f"{response.json()}"
                data = data.replace("'", '"')
                data = data.replace("True", "true")
                data = json.loads(data)
                voxel = data['msg']['image_to_reference']
                x,y,z = voxel['x']/160, voxel['y']/160, voxel['z']/160
                writer.writerow([x, y, z])
            else:
                print(f"Failed to fetch data: {response.status_code}")

structure_to_image()