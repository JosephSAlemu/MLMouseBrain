import os
import pandas as pd


def is_valid_image(section_image: int) -> bool:
    path = rf"./Datasets/SectionImages/{section_image}.jpg"
    if os.path.exists(path):
        return False
    return True


def is_valid_chunk(path: str, count:int) -> bool:
    path = rf"./Datasets/Outputs/{path}/P4_Chunk_{count}.csv"
    if os.path.exists(path):
        temp = pd.read_csv(rf"{path}")
        if len(temp) != 21:
            print(f"{path} Exists. Length: {len(temp)}")
            os.remove(rf"{path}")
            return True
        print(f"path exists {path}")
        return False
    return True

def is_valid_p4_voxel_gene(gene: str) -> bool:
    """
    checks if the file is
    """
    path = rf"./Datasets/Outputs/New_Voxels/{gene}.csv"
    if os.path.exists(path):
        return False
    return True

def is_valid_voxel(count: int) -> bool:
    """
    deprecated method
    """
    path = rf".\Datasets\Outputs\Voxels\P4_Voxel_{count}.csv"
    path_exists = os.path.exists(path)
    if path_exists:
        print("Existing path")
        return False
    elif not path_exists and not is_valid_chunk("Chunked", count):
        print("Valid path")
        return True
    else:
        print("idk how the hell this happened")
