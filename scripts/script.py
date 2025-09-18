import pandas as pd

from src.constants import HEADERS, P4_MOUSE_REFERENCE_ID, P56_MOUSE_REFERENCE_ID, P4_CONVERSION, P56_CONVERSION
from typing import Callable, Any
'''
A file of commonly reusable scripts
'''

def split_section_ids(section_ids: list, chunk_size: int = 100) -> list[list]:
    '''
    Split array of section id's into a 2d array of sections of 100 for AMBA queries
    '''
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

def strip_experiments(file: str, new_path: str) -> None:
    '''
    Strips the '-' and section_dataset_ids numbers from gene names
    '''
    df = pd.read_csv(file)

    l = [x.rsplit("-", 1)[0] for x in df.columns]
    df.columns = l
    print(df.columns)
    df.to_csv(new_path, index=False)

def strip_gene(column: str):
    '''
    Strips the '-' and returns the gene name and section_dataset_id
    '''
    return column.rsplit("-", 1)[1]    

def count_missing_expressions(file: str, missing: str) -> None:
    '''
    Counts missing expressions
    '''
    df = pd.read_csv(file)
    print(df.drop(columns=HEADERS))

    match missing:
        case "na":
            print(df.isna().sum().sum())
        case "-1":
            pass
        case _:
            pass

def ccf_to_microns(mouse: int, x: int, y: int, z: int) -> list[int]:
    '''
    Based on the mouse, it converts ccf to microns and returns a list of X,Y,Z coordinates

    [0] = X
    [1] = Y
    [2] = Z
    '''
    if mouse == P4_MOUSE_REFERENCE_ID:
        return [x*P4_CONVERSION, y*P4_CONVERSION, z*P4_CONVERSION]
    
    elif mouse == P56_MOUSE_REFERENCE_ID:
        return [x*P56_CONVERSION, y*P56_CONVERSION, z*P56_CONVERSION]
    
def microns_to_ccf(mouse: int, x: int, y: int) -> list[int]:
    if mouse == P4_MOUSE_REFERENCE_ID:
        return [x/P4_CONVERSION, y/P4_CONVERSION]
    
    elif mouse == P56_MOUSE_REFERENCE_ID:
        return [x/P56_CONVERSION, y/P56_CONVERSION]

def file_to_list(file: str, type: Callable[[str], Any] = str) -> list:
    '''
    Takes in a text file
    Casts to the type provided
    
    returns an array of the text files contents.
    '''
    arr = []
    with open(file, "r") as file:
        arr = [type(line) for line in file]
    return arr

def length(file: str) -> int:
    '''
    Takes in a path to a csv file

    returns the length of the file
    '''
    return len(pd.read_csv(file))

def read(file: str) -> pd.DataFrame:
    return pd.read_csv(file)
