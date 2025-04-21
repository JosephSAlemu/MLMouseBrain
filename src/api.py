import pandas as pd
import requests
import json
import csv
from filter import group_data
from constants import SIZE, headers
from validation import is_valid_voxel, is_valid_chunk

#Number of p-56 voxels, size of the NewDenC file, the number of p4 chunks

def api_calls() -> None:
    count = 0
    file = pd.read_csv(r'./Datasets/Outputs/NewDenC_Microns.csv')

    #max = len(file['X'])
    while count < len(file['X']):
        reference_to_image(file['X'][count], file['Y'][count], file['Z'][count], count)
        count+=1


def download_section_images() -> None: 
    test = set()
    count = 0
    while count < SIZE:
        file = pd.read_csv(rf"./Datasets/Outputs/Chunks/P4_Chunk_{count}.csv")
        for row in file['Section_Image']:
            new_row = json.loads(row.replace("\'","\""))
            for chunk in new_row:
                section_image = chunk['image_sync']['section_image_id']
                test.add(section_image)
        count+=1
    print(f"{test}\n")
    print(f"{len(test)} Section Images to Download.")


def reference_to_image(X: int, Y: int, Z: int, count: int) -> None:
    list = []
    chunk_headers = [
        "Voxel", "Section_Image"
    ]
    if is_valid_chunk("Chunked", count):
        created_file = rf"./Datasets/Outputs/Chunked/P4_Chunk_{count}.csv"
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
                        list.append(line)
                    else:
                        print(f"ISSUE WITH QUERY {url}")
                else:
                    list.append(int(line))
            url = f"http://api.brain-map.org/api/v2/reference_to_image/10.json?x={X}&y={Y}&z={Z}&section_data_set_ids={','.join(map(str, list))}"
            response = requests.get(url)
            if response.status_code == 200:
                data = f"{response.json()['msg']}"
                writer.writerow([count, data])
                list = []
            else:
                print(f"ISSUE WITH QUERY {url}")

def fifty_chunk(X: int, Y: int, Z: int, count: int) -> None:
    counter = 0
    list = []
    chunk_headers = [
        "Voxel", "Section_Image"
    ]
    ""
    if is_valid_chunk("Test", count):
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
         
    print(f"done {counter}")


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



def image_to_reference(p5_voxel: int) -> None:
    """
    takes all the p-4 section images associated with a p-56 voxels [1465 voxels]

    divides all the coordinates by 160 to get the reference space coordinates

    p5_voxel values: 0 to 1464 (inclusive). [0,1464]
    """
    
    print(p5_voxel)
    #r"./Datasets/Outputs
    if is_valid_voxel(p5_voxel):

        created_file = rf".\Datasets\Outputs\Voxels\P4_Voxel_{p5_voxel}.csv"

        print(p5_voxel)
        data = group_data(p5_voxel)

        with open(created_file, mode ="a", newline="") as file:

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
    else:
        print("Bug")


