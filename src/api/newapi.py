import requests
from constants import P4_MOUSE_REFERENCE_ID
from query import QueryBuilder
from enums.actions import Action


class Api():
    def __init__(self, file: str = None):
        self.file = file
    
    def download_section_images(self) -> None:
        Builder = QueryBuilder()
        Builder.section_image()
        print(Builder.query.format(image = ))

    def reference_to_image(
        X: int,
        Y: int,
        Z: int,
        mouse: int,
        section_ids: list,
        counter: int,
        file_num: int,
        gene: str = None,
    ) -> None:
        section_id_chunks = split_section_ids(section_ids)
        if mouse == P56_MOUSE_REFERENCE_ID:

            # Have a line where you convert this to microns
            X, Y, Z = float(X), float(Y), float(Z)
            X, Y, Z = X * 200, Y * 200, Z * 200
            image_ids = []
            if is_valid_chunk("Chunked", counter):
                created_file = rf"./Datasets/Outputs/Chunked/P4_Chunk_{counter}.csv"
                with open(
                    r"./Datasets/Inputs/section_dataset_ids_reference_6_sagittal.txt"
                ) as file, open(created_file, mode="a", newline="") as new_file:
                    writer = csv.writer(new_file)
                    writer.writerow(CHUNK_HEADERS)

                    image_ids = []

                    for line in file:
                        if len(image_ids) == 100:
                            url = f"http://api.brain-map.org/api/v2/reference_to_image/10.json?x={X}&y={Y}&z={Z}&section_data_set_ids={','.join(map(str, image_ids))}"
                            response = requests.get(url)
                            if response.status_code == 200:
                                data = f"{response.json()['msg']}"
                                writer.writerow([counter, data])
                                image_ids.append(line)
                            else:
                                print(f"ISSUE WITH QUERY {url}")
                        else:
                            image_ids.append(int(line))

                    url = f"http://api.brain-map.org/api/v2/reference_to_image/10.json?x={X}&y={Y}&z={Z}&section_data_set_ids={','.join(map(str, image_ids))}"
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = f"{response.json()['msg']}"
                        writer.writerow([counter, data])
                        image_ids = []
                    else:
                        print(f"ISSUE WITH QUERY {url}")

        elif mouse == P4_MOUSE_REFERENCE_ID:
            # Reference to Micron conversion
            X, Y, Z = float(X), float(Y), float(Z)
            n_X, n_Y, n_Z = X * 160, Y * 160, Z * 160

            if is_valid_chunk("Fill_Negatives", counter):
                created_file = (
                    rf"./Datasets/Outputs/Fill_Negatives/{file_num}/P4_Chunk_{counter}.csv"
                )
                with open(created_file, mode="a", newline="") as new_file:
                    writer = csv.writer(new_file)
                    writer.writerow(CHUNK_HEADERS_V2)
                    for image_ids in section_id_chunks:
                        url = f"http://api.brain-map.org/api/v2/reference_to_image/{mouse}.json?x={n_X}&y={n_Y}&z={n_Z}&section_data_set_ids={','.join(map(str, image_ids))}"
                        response = requests.get(url)
                        if response.status_code == 200:
                            result = response.json()["msg"]
                            for data in result:
                                data = data["image_sync"]
                                section_dataset = data["section_data_set_id"]
                                image = data["section_image_id"]
                                seed_x = data["x"]
                                seed_y = data["y"]
                                writer.writerow(
                                    [X, Y, Z, section_dataset, image, seed_x, seed_y]
                                )

                        else:
                            print(f"ISSUE WITH QUERY {url}")
    


if __name__ == "__main__":
    ob = Api()
    ob.download_section_images()