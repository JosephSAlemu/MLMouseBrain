import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from enums.inequality import Inequality
from enums.dimensions import Dimensions
from constants import HEADERS
from collections.abc import Callable
from collections import Counter, defaultdict
from scipy.stats import zscore

class Utility():
    '''
    Class that holds functions that perform data filtering, feature reduction, plotting etc.
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
    
    def filter_all(self, dimension: Dimensions, threshold: str | int | None, equality: Inequality) -> None:
        '''
        filters all rows, columns, or both ows an columns based on the threshold provided

        creates a new CSV file for the result
        '''
        match dimension:
            case Dimensions.ROW:
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

            case Dimensions.COLUMN:
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

            case Dimensions.BOTH:
                match equality:
                    case Inequality.LESS_THAN:
                        df = pd.read_csv(self.file)
                        gene_cols = df.columns.difference(HEADERS)

                        mask = (df[gene_cols] == 0) | (df[gene_cols] == -1)

                        bad_ratio_row = mask.sum(axis=1) / len(gene_cols)
                        bad_ratio_col = mask.sum(axis=0) / df.shape[0]

                        clean_gene_cols = bad_ratio_col[bad_ratio_col < 0.9].index.tolist()

                        final_cols = HEADERS + clean_gene_cols

                        df_clean = df.loc[bad_ratio_row < 0.9, final_cols].copy()

                        # Final result
                        df_clean.to_csv("./Datasets/Outputs/P4_50_RE_CLN_NewDenS.csv", index=False)
                    case Inequality.GREATER_THAN:
                        print(Inequality.GREATER_THAN)

                    case Inequality.LESS_THAN_EQUAL:
                        print(Inequality.LESS_THAN_EQUAL)

                    case Inequality.GREATER_THAN_EQUAL:
                        print(Inequality.GREATER_THAN_EQUAL)

                    case Inequality.EQUAL_TO:
                        print(Inequality.EQUAL_TO)

    def retrieve_voxel_frequencies(self, coordinate: str) -> tuple[float, list]:
        '''
        retrieves the voxel coordinate and it's assigned gene expression

        Why? -> We want to see the distribution and mean of the gene expressions and then normalize them
        '''
        values = None
        if coordinate == "X" or coordinate == "Y" or coordinate == "Z":
            df = pd.read_csv(self.file)
            values = list(set(df[coordinate].astype(float)))
            values.sort()
            my_dict = dict([(i,[]) for i in values])
            print(my_dict)
            for _, row in df.iterrows():
                key = float(row[coordinate])
                if key in my_dict:
                    my_dict[key].extend(row[3:])

            return my_dict
            
        else:
            raise ValueError(f"invalid coordinate: {coordinate}")
    
    def plot(self, func: Callable[[str], dict], parameter: str) -> None:
        my_dict = func(parameter)

        for key, values in my_dict.items():
            _, ax = plt.subplots()
            plt.hist(values, bins="auto")
            plt.xlabel(f"gene_expressions")
            plt.yscale("log")
            plt.ylabel("Frequency")
            plt.title(f"{parameter} value of {key}")
            plt.show(block=False)
            plt.pause(0.1)
        plt.show()

    def z_score_normalize(self, col: str, new_path: str) -> None:
        '''
        Applies z-score normalization on each z coordinate, grouping each voxel by their z coordinate for the normalization.

        This is to prevent seperate slices on the z axis when performing k-means clustering
        '''
        df = pd.read_csv(self.file)
        cols = list(df.columns)
        for coord in HEADERS:
            cols.remove(coord)
        values = list(set(df[col].astype(float)))
        
        for value in values:
            df.loc[df["Z"] == value, cols] = zscore(df.loc[df["Z"] == value, cols], nan_policy="omit")
        df.to_csv(new_path, index=False)
        #df[parameter] = np.where

