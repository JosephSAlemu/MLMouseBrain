import csv
import requests
import os
import pandas as pd
from src.constants import (
    P4_MOUSE_REFERENCE_ID,
    P56_MOUSE_REFERENCE_ID,
    CHUNK_HEADERS,
    HEADERS_V4,
    CHUNK_HEADERS_V2,
    CHUNK_HEADERS_V4,
    P4_CONVERSION,
    P56_CONVERSION,
)
from src.query import QueryBuilder
from src.enums.actions import Action
from src.utils.validation import is_valid_image, path_exists, chunk_exists
from scripts.script import (
    file_to_list,
    split_section_ids,
    get_file_number,
    ccf_to_microns,
    microns_to_ccf,
    read,
)


class Api:

    def __init__(self, mouse: int = None):
        self.mouse = mouse
        self.query = QueryBuilder()

    def download_section_images(self) -> None:
        pass

    def start_ref_to_img(
        self,
        voxels_path: str,
        section_ids_path: str,
        dir_path: str,
        headers: list[str],
        thread_chunk_size: tuple = None,
        file_name: str = "Chunk",
    ) -> None:
        """
        Given the voxel path, section_id, path, and the file_name call reference_to_image()
        """
        self.query.reference_to_image()

        section_ids = file_to_list(section_ids_path, int)
        section_ids = split_section_ids(section_ids)

        full_path = os.path.join(dir_path, file_name)

        df = read(voxels_path)

        if thread_chunk_size is not None:
            start, stop = thread_chunk_size
            df = df.iloc[start:stop]

        if headers == CHUNK_HEADERS_V2:
            for row in df.itertuples():
                new_path = f"{full_path}_{row.Index}.csv"
                self.reference_to_image(
                    row.X, row.Y, row.Z, headers, section_ids, new_path
                )

        elif headers == CHUNK_HEADERS_V4:
            df.rename(columns={"Structure-ID": "structure"}, inplace=True)
            for row in df.itertuples():
                new_path = f"{full_path}_{row.Index}.csv"
                self.reference_to_image(
                    row.X, row.Y, row.Z, headers, section_ids, new_path, row.structure
                )

    def start_img_to_ref(
        self,
        chunk_path: str,
        dir_path: str,
        headers: list[str],
        thread_chunk_size: tuple = None,
        file_name: str = "Voxel",
    ) -> None:
        """
        Given the voxel path, section_id, path, and the file_name call image_to_reference()
        """
        self.query.image_to_reference()

        df = read(chunk_path)

        if thread_chunk_size is not None:
            start, stop = thread_chunk_size
            df = df.iloc[start:stop]

        full_path = os.path.join(dir_path, file_name)

        if headers == HEADERS_V4:
            df.rename(columns={"Structure-ID": "structure"}, inplace=True)
            for row in df.itertuples():
                new_path = f"{full_path}_{get_file_number(chunk_path)}.csv"
                self.image_to_reference(
                    row.Section_Image,
                    row.Seed_x,
                    row.Seed_y,
                    headers,
                    new_path,
                    row.structure,
                )

    def start_download_binarized(
        self, voxels_path: str, dir_path: str, thread_chunk_size: tuple = None
    ) -> None:
        """
        Given the voxel path, section_id, path, and the file_name call download_binarized_image()
        """
        df = read(voxels_path)
        if thread_chunk_size is not None:
            start, stop = thread_chunk_size
            df = df.iloc[start:stop]

        for row in df.itertuples():
            self.download_binarized_image(row.Section_Image, dir_path)

    def reference_to_image(
        self,
        X: int,
        Y: int,
        Z: int,
        headers: list[str],
        section_ids: list[list],
        new_path: str,
        structure_id: int = None,
    ) -> None:
        """
        Reference-To-Image call based on Allen Mouse Developing Brain Atlas (AMDBA).

        Converts from the mouse reference space to the target images for the section data sets
        """
        m_X, m_Y, m_Z = ccf_to_microns(self.mouse, X, Y,Z)

        if not chunk_exists(new_path, len(section_ids)):

            with open(new_path, mode="w", newline="") as new_file:
                writer = csv.writer(new_file)
                writer.writerow(headers)

                for image_ids in section_ids:
                    query = self.query.url
                    images = ",".join(map(str, image_ids))
                    query = query.format(
                        reference_id=P56_MOUSE_REFERENCE_ID,
                        X=m_X,
                        Y=m_Y,
                        Z=m_Z,
                        image_ids=images,
                    )

                    response = requests.get(query)

                    if response.status_code == 200:
                        for data in response.json()["msg"]:
                            data = data["image_sync"]
                            if structure_id:
                                arr = [structure_id, X, Y, Z]
                            else:
                                arr = [X, Y, Z]

                            arr += [
                                int(data["section_data_set_id"]),
                                int(data["section_image_id"]),
                                int(data["x"]),
                                int(data["y"]),
                            ]
                            writer.writerow(arr)
                    else:
                        print(f"ISSUE WITH QUERY {query}")

    def image_to_reference(
        self,
        section_image_id: int,
        X: int,
        Y: int,
        headers: list[str],
        new_path: str,
        structure_id: int = None,
    ) -> tuple | None:
        """
        Image-To-Reference call based on Allen Mouse Developing Brain Atlas (AMDBA).

        Converts from section image, x coordinate, and y coordinate to voxel coordinates in the mouse reference space
        """
        if not path_exists(new_path):
            with open(new_path, mode="w", newline="") as new_file:
                writer = csv.writer(new_file)
                writer.writerow(headers)
                query = self.query.url
                query = query.format(
                    section_image_id=section_image_id, x_coord=X, y_coord=Y
                )
                response = requests.get(query)
                if response.status_code == 200:
                    data = response.json()["msg"]["image_to_reference"]
                    x,y,z = microns_to_ccf(self.mouse, int(data["x"]),int(data["y"]), int(data["z"]))
                    arr = [structure_id, x, y, z]
                    writer.writerow(arr)
                else:
                    print(f"ISSUE WITH QUERY {query}")

    def download_binarized_image(self, section_image_id: int, dir_path: str) -> None:
        """
        Given a section_image_id and the directory you want to save the image to, the function downloads a binarized version of the section_image
        """
        self.query.binarized_section_image()
        query = self.query.url.format(image_id=section_image_id)

        new_path = os.path.join(dir_path, f"{section_image_id}.jpg")

        while is_valid_image(new_path):
            response = requests.get(query, stream=True)
            response.raise_for_status()
            with open(new_path, "wb") as file:
                for chunk in response:
                    file.write(chunk)
