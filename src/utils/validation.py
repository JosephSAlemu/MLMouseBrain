import os
from scripts.script import length, read

def is_valid_image(path: str) -> bool:
    '''
    Given a path to an image, determine if the image is corrupt (redownload), already exists (skip), or doesn't exist (download).

    True = redownload or download image
    False = skip image
    '''
    if os.path.exists(path):
        with open(path, 'rb') as f:
            check_chars = f.read()[-2:]
        if check_chars != b'\xff\xd9':
            print(f"{path} is errored")
            return True
        return False
    return True

def is_valid_chunk(path: str, expected_size: int) -> bool | str:
    '''
    Given a path to a chunk file and expected size of a chunk file, determine if we can skip, redo, or create that file.

    True = modify or create
    False = skip
    '''
    if os.path.exists(path):
        temp = read(path)
        length = len(temp)
        if length != expected_size:
            print(f"{path} exists but incomplete")
            os.remove(rf"{path}")
            return True
        print(f"path exists {path}")
        return False
    return True

def is_valid(path: str) -> bool:
    '''
    Given a path, determine if it already exists

    True = You can create the file/dir.
    False = You can't create the file/dir.
    '''
    return not os.path.exists(path)

def path_exists(path: str) -> bool:
    '''
    Given a path, determine if it already exists

    True = You can create the file/dir.
    False = You can't create the file/dir.
    '''
    return os.path.exists(path)

def chunk_exists(path: str, expected_size: int) -> bool | str:
    '''
    Given a path to a chunk file and expected size of a chunk file, determine if we can skip, redo, or create that file.

    True = skip
    False = modify or create
    '''
    
    if os.path.exists(path) and os.path.getsize(path) > 0:
        lngth = length(path)
        if lngth != expected_size:
            print(f"{path} exists but incomplete")
            os.remove(rf"{path}")
            return False
        print(f"path exists {path}")
        return True
    return False
