from enum import Enum, auto

class Action(Enum):

    GET_IMAGE_IDS = auto()

    REANALYSIS = auto()

    RETRIEVE_VOXELS = auto()

    RETRIEVE_IMAGES = auto()

    CREATE_FILES = auto()

    CREATE_DATAFRAME = auto()

    BINARY_DILATION = auto()

    GET_SEED_PIXELS = auto()

    SECTION_IMAGE = auto()

    BINARIZED_SECTION_IMAGE = auto()

    VOXELS = auto()

    GENES = auto()