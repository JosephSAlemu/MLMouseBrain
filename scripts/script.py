import pandas as pd

def split_section_ids(section_ids: list, chunk_size: int = 100) -> list[list]:
    """
    Split array of section id's into a 2d array of sections of 100 for AMBA queries
    """
    length = len(section_ids)
    if length <= 100:
        return [section_ids]
    
    result = []
    arr = []
    length = len(section_ids)
    for ind in range(length):
        if ind != 0 and ind%100 == 0:
            result.append(arr)
            arr = []
        if ind == length-1:
            arr.append(section_ids[ind])
            result.append(arr)
            arr = []
        arr.append(section_ids[ind])

    return result

def strip_experiments(path: str, new_path: str) -> None:
    df = pd.read_csv(path)

    l = [x.rsplit("-", 1)[0] for x in df.columns]
    df.columns = l
    print(df.columns)
    df.to_csv(new_path, index=False)

def find_common_voxels(path: str, other_path: str, ignore: list[str], ignore_other: list[str]) -> None:
    df = pd.read_csv(path)
    other_df = pd.read_csv(other_path)

    df