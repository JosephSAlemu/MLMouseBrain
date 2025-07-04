from enum import Enum, auto

class Inequality(Enum):
    
    LESS_THAN = auto()
    
    GREATER_THAN = auto()

    LESS_THAN_EQUAL = auto()
    
    GREATER_THAN_EQUAL = auto()

    EQUAL_TO = auto()