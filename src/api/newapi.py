import csv
import requests
import os
import pandas as pd
from src.constants import P4_MOUSE_REFERENCE_ID, P56_MOUSE_REFERENCE_ID, CHUNK_HEADERS, CHUNK_HEADERS_V2, P4_CONVERSION, P56_CONVERSION
from src.query import QueryBuilder
from src.enums.actions import Action
from src.utils.validation import is_valid_chunk, is_valid_image
from scripts.script import file_to_list, split_section_ids, ccf_to_microns

class Api():

    def __init__(self, mouse: int = None):
        self.mouse = mouse
        self.query = QueryBuilder()
    
    def download_section_images(self) -> None:
        pass

    def start_ref_to_img(self, voxels_path: str, section_ids_path: str, dir_path: str, thread_chunk_size: tuple = None, file_name: str = "Chunk") -> None:
        '''
        Given the voxel path, section_id, path, and the file_name call the reference_to_image api
        '''
        self.query.reference_to_image()

        section_ids = file_to_list(section_ids_path, int)
        section_ids = split_section_ids(section_ids)
        
        full_path = os.path.join(dir_path, file_name)
        
        df = pd.read_csv(voxels_path)

        if thread_chunk_size is not None:
            start, stop = thread_chunk_size
            df = df.iloc[start:stop]

        for row in df.itertuples():
            new_path = f"{full_path}_{row.Index}.csv"
            self.reference_to_image(row.X, row.Y, row.Z, section_ids, new_path)            
            

    def reference_to_image(
        self,
        X: int,
        Y: int,
        Z: int,
        section_ids: list,
        new_path: int,
    ) -> None:
        '''
        Reference-To-Image call based on Allen Mouse Developing Brain Atlas (AMDBA).

        Converts from the mouse reference space to the target images for the section data sets 
        '''
        m_X, m_Y, m_Z = ccf_to_microns(mouse=self.mouse, x=X, y=Y, z=Z)

        if is_valid_chunk(new_path, len(section_ids)):
                
            with open(new_path, mode="a", newline="") as new_file:
                writer = csv.writer(new_file)
                writer.writerow(CHUNK_HEADERS_V2)

                for image_ids in section_ids:
                    query = self.query.url
                    images = ','.join(map(str, image_ids))
                    query = query.format(reference_id=P56_MOUSE_REFERENCE_ID, X=m_X, Y=m_Y, Z=m_Z, image_ids=images)

                    response = requests.get(query)

                    if response.status_code == 200:
                        for data in response.json()['msg']:
                            data = data['image_sync']
                            arr = [X,Y,Z]
                            arr += [int(data['section_data_set_id']), int(data['section_image_id']), int(data['x']), int(data['y'])]

                            writer.writerow(arr)
                    else:
                        print(f"ISSUE WITH QUERY {query}")

    
    def image_to_reference(
    self,
    section_image_id: int, 
    X: int, 
    Y: int,
    new_path: str
    ) -> tuple | None:
        '''
        Image-To-Reference call based on Allen Mouse Developing Brain Atlas (AMDBA).

        Converts from section image, x coordinate, and y coordinate to voxel coordinates in the mouse reference space
        '''
        query = QueryBuilder()
        self.query = query.image_to_reference()

        match mouse:
            case _:
                pass


        try:
            response = session.get(url)
            response.raise_for_status()
            data = f"{response.json()}"
            data = data.replace("'", '"')
            data = data.replace("True", "true")
            data = json.loads(data)
            voxel = data["msg"]["image_to_reference"]
            x, y, z = voxel["x"] / 160, voxel["y"] / 160, voxel["z"] / 160
            # print(f"after division: x = {x} y = {y},z = {z}")
            return (x, y, z)
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def download_binarized_image(self, section_image_id: int, dir_path: str) -> None:
        '''
        Given a section_image_id and the directory you want to save the image to, the function downloads a binarized version of the section_image
        '''
        self.query.binarized_section_image()
        print(self.query.url)
        query = self.query.url.format(image_id = section_image_id)

        new_path = os.path.join(dir_path, f"{section_image_id}.jpg")
        
        while is_valid_image(new_path):
            response = requests.get(query, stream=True)
            response.raise_for_status()
            with open(new_path, "wb") as file:
                for chunk in response:
                    file.write(chunk)