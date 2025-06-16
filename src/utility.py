class Utility():
    '''
    Class that holds functions that perform data filtering, feature reduction, etc.
    '''
    def __init__(self, file: str = None):
        self.file = file
        pass
    
    def filter_column(self, column: str, threshold: , equality: enums) -> None:
        df = pd.read_csv(self.file)
        match equality:
            case 
        result = df.loc[df[column] > threshold]