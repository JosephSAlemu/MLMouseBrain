import csv
import requests
from src.constants import P4_MOUSE_REFERENCE_ID, P56_MOUSE_REFERENCE_ID, CHUNK_HEADERS, CHUNK_HEADERS_V2, P4_CONVERSION, P56_CONVERSION
from src.query import QueryBuilder
from src.enums.actions import Action
from scripts.script import split_section_ids, ccf_to_microns
from src.utils.validation import is_valid_chunk

class Api():

    def __init__(self, file: str = None, mouse: str = None):
        self.file = file
        self.mouse = mouse
        self.query = None
    
    def download_section_images(self) -> None:
        pass

    def reference_to_image(
        self,
        mouse: int,
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
        url = QueryBuilder()
        url.reference_to_image()
        self.query = url.query

        section_id_chunks = split_section_ids(section_ids)

        m_X, m_Y, m_Z  = ccf_to_microns(mouse=mouse, x=X, y=Y, z=Z)

        if is_valid_chunk(new_path, len(section_id_chunks)):
                
            with open(new_path, mode="a", newline="") as new_file:
                writer = csv.writer(new_file)
                writer.writerow(CHUNK_HEADERS_V2)

                for image_ids in section_id_chunks:
                    query = self.query
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
                        print(f"ISSUE WITH QUERY {url}")

    
    def image_to_reference(
    self,
    mouse: int,
    section_image_id: int, 
    X: int, 
    Y: int,
    
    ) -> tuple | None:
        '''
        takes in the section image for a gene and the centroid coordinates for the bin in that section image

        divides all the coordinates by 160 to get the reference space coordinates

        returns the result of that query as tuple of the voxel coordinates
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