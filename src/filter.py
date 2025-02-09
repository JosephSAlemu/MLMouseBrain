import pandas as pd

import json
def get_dataset_id() -> None:
    dataset = pd.read_csv("Datasets\Inputs\P4_section_images_cleaned.csv")
    temp = dataset["Section Image"]
    res = set()
    for j in temp:
        hold = j.split(",")
        for i in hold:
            id = i.split("\'")
            if id[1] == 'data_set_id':
                res.add(id[3])
    res = list(res)
    print(res)
    with open(r"./result.txt", mode="w") as ff:
        ff.write('\n'.join(str(i) for i in res))

# Take the dataset, filter out the id, x, and y -> put through the image to reference API.
# Pray the voxels in the reference space are touching each other for each chunk.
# If they do touch each other, then we can just use one image per chunk lowering are computational cost by a lot.
def filter_data(voxel: int) -> list[dict]:
    # Input the path of the csv file with the 21 chunks and ten p-56 voxels.
    dataset = pd.read_csv("[Insert_File_Path]")
    temp = dataset["Section Image"]
    offset = voxel * 21
    end = offset + 20
    result = []
    while offset <= end:
        j = temp[offset]
        j = j.replace("\'","\"")

        try:
            j = json.loads(j)
            result.extend(j)
            offset+=1
        except Exception as e:
            offset+=1

    return result
        
        



def get_unique_structures() -> None:
    structures = pd.read_csv("Datasets\Outputs\P4_Complete_Brain.csv")
    print(structures['structure_name'].unique())
