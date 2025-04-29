import pandas as pd
import requests
import json
import csv
import os
import paramiko
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv, dotenv_values
from filter import group_data
from constants import SIZE, headers
from validation import is_valid_voxel, is_valid_chunk


#for retrying requests
session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=1,  # 1s, 2s, 4s, 8s, 16s delays
    status_forcelist=[502, 503, 504],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("http://", adapter)
session.mount("https://", adapter)

#Number of p-56 voxels, size of the NewDenC file, the number of p4 chunks
load_dotenv()
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



def image_to_reference(section_image_id: int, x_coord: int, y_coord:int) -> tuple | None:
    """
    takes in the section image for a gene and the centroid coordinates for the bin in that section image

    divides all the coordinates by 160 to get the reference space coordinates

    returns the result of that query as tuple of the voxel coordinates
    """
    
    
    url = f"http://api.brain-map.org/api/v2/image_to_reference/{section_image_id}.json?x={x_coord}&y={y_coord}"
    try:
        response = session.get(url)
        response.raise_for_status()
        data = f"{response.json()}"
        data = data.replace("'", '"')
        data = data.replace("True", "true")
        data = json.loads(data)
        voxel = data['msg']['image_to_reference']
        x,y,z = voxel['x']/160, voxel['y']/160, voxel['z']/160
        #print(f"after division: x = {x} y = {y},z = {z}")
        return (x, y, z)        
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

def upload_file(file_path: str, file_name: str) -> None:
    """
    Uploads the gene files with voxels to remote linux server
    """
    # Establishing SSH client for the source server
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(os.getenv("DOMAIN"), username=os.getenv("USERNAME"), password=os.getenv("PASSWORD"))

    client_sftp = client.open_sftp()

    dest_path = os.getenv("DEST_PATH")
    client_sftp.put(file_path, os.path.join(dest_path, file_name).replace("\\","/"))
    


    client.close()
    client_sftp.close()

def retrieve_files() -> None:
    """
    Retreves all the gene files in the remote linux server and puts it into New_Voxels directory
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(os.getenv("DOMAIN"), username=os.getenv("USERNAME"), password=os.getenv("PASSWORD"))

    sftp = client.open_sftp()
    files = []

    local_path = "Datasets/Outputs/New_Voxels"
    remote_path = os.getenv("DEST_PATH")

    for f in sftp.listdir(remote_path):
        remote = os.path.join(remote_path, f)
        local = os.path.join(local_path, f)

        sftp.get(remote, local) 
    

def directories() -> None:
    path = r"./Datasets/Outputs/New_Voxels"
    directory = os.fsencode(path)
  
    for file in os.listdir(directory):
        file_name = os.fsdecode(file)
        file_path = f"{path}/{file_name}"
        upload_file(file_path, file_name)
        

retrieve_files()


