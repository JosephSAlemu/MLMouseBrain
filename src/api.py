import pandas as pd
import requests
import json
import csv
from filter import filter_data

def api_calls() -> None:
    ...

def structure_to_image():
    ...
    
def image_to_structure(p5_voxel: int) -> None:
    """
    takes all the p-4 section images associated with a p-56 voxels [1465 voxels]

    p5_voxel values: 0..1464

    """
    
    data = filter_data(p5_voxel)
    print(len(data))
    headers = [
        "X","Y","Z"
    ]
    file = f"./result{p5_voxel}.csv"
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
                x,y,z = voxel['x'], voxel['y'], voxel['z']
                writer.writerow([x, y, z])
            else:
                print(f"Failed to fetch data: {response.status_code}")


image_to_structure(2)
image_to_structure(3)
image_to_structure(4)
image_to_structure(5)
image_to_structure(6)
image_to_structure(7)
image_to_structure(8)
image_to_structure(9)