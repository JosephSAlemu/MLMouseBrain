from enum import Enum

class Action(Enum):

    GET_IMAGE_IDS = 0

    REANALYSIS = 1

    RETRIEVE_VOXELS = 3

    RETRIEVE_IMAGES = 4

    CREATE_FILES = 5

    CREATE_DATAFRAME = 6

    BINARY_DILATION = 7

    GET_SEED_PIXELS = 8

    SECTION_IMAGE = 9

    BINARIZED_SECTION_IMAGE = 10


class Inequality(Enum):
    
    LESS_THAN = 0
    
    GREATER_THAN = 1

    LESS_THAN_EQUAL = 2
    
    GREATER_THAN_EQUAL = 3

    EQUAL_TO = 4