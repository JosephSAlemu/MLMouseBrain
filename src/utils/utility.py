import pandas as pd
from enums.Inequality import Inequality
class Utility():
    '''
    Class that holds functions that perform data filtering, feature reduction, etc.
    '''
    def __init__(self, file: str = None):
        self.file = file
        pass
    
    def filter_column(self, column: str, threshold: str | int | None, equality: Inequality) -> None:
        #df = pd.read_csv(self.file)
        match equality:
            case Inequality.LESS_THAN:
                print(Inequality.LESS_THAN)

            case Inequality.GREATER_THAN:
                print(Inequality.GREATER_THAN)

            case Inequality.LESS_THAN_EQUAL:
                print(Inequality.LESS_THAN_EQUAL)

            case Inequality.GREATER_THAN_EQUAL:
                print(Inequality.GREATER_THAN_EQUAL)

            case Inequality.EQUAL_TO:
                print(Inequality.EQUAL_TO)

