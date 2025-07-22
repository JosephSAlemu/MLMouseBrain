import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score
from sklearn.impute import KNNImputer
from sklearn.model_selection import train_test_split
from collections.abc import Callable
from collections import Counter, defaultdict
from scipy.stats import zscore
from src.enums.inequality import Inequality
from src.enums.dimensions import Dimensions
from src.constants import HEADERS, HEADERS_V2


class Utility():
    '''
    Class that holds functions that perform data filtering, feature reduction, plotting etc.
    '''
    def __init__(self, file: str = None):
        self.file = file
        pass
    
    def filter_genes(self, threshold: str | int | None, equality: Inequality, new_path: str) -> None:
        #df = pd.read_csv(self.file)
        match equality:
            case Inequality.LESS_THAN:
                df = pd.read_csv(self.file)
                gene_cols = df.columns.difference(HEADERS_V2)

                mask = (df[gene_cols] == 0) | (df[gene_cols] == -1)
                
                bad_ratio_col = mask.sum(axis=0) / df.shape[0]

                clean_gene_cols = bad_ratio_col[bad_ratio_col < threshold].index.tolist()
                final_cols = HEADERS_V2 + clean_gene_cols

                df_clean = df[final_cols].copy()

                # Final result
                df_clean.to_csv(new_path, index=False)

            case Inequality.GREATER_THAN:
                print(Inequality.GREATER_THAN)

            case Inequality.LESS_THAN_EQUAL:
                print(Inequality.LESS_THAN_EQUAL)

            case Inequality.GREATER_THAN_EQUAL:
                print(Inequality.GREATER_THAN_EQUAL)

            case Inequality.EQUAL_TO:
                print(Inequality.EQUAL_TO)
    
    def filter_voxels_and_genes(self, dimension: Dimensions, threshold: str | int | None, equality: Inequality, new_path: str) -> None:
        '''
        filters all rows, columns, or both based on the threshold provided

        creates a new CSV file for the result
        '''
        match equality:
            case Inequality.LESS_THAN:
                df = pd.read_csv(self.file)
                gene_cols = df.columns.difference(HEADERS)

                mask = (df[gene_cols] == 0) | (df[gene_cols] == -1)

                bad_ratio_row = mask.sum(axis=1) / len(gene_cols)
                
                bad_ratio_col = mask.sum(axis=0) / df.shape[0]

                clean_gene_cols = bad_ratio_col[bad_ratio_col < threshold].index.tolist()
                final_cols = HEADERS + clean_gene_cols

                df_clean = df.loc[bad_ratio_row < threshold, final_cols].copy()

                # Final result
                df_clean.to_csv(new_path, index=False)
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
            _, _ = plt.subplots()
            plt.hist(values, bins="auto")
            plt.xlabel(f"gene_expressions")
            plt.yscale("log")
            plt.ylabel("Frequency")
            plt.title(f"{parameter} value of {key}")
            plt.show(block=False)
            plt.pause(0.1)
        plt.show()

    def z_score_normalize(self, col: str, new_path: str, ignore: list[str]) -> None:
        '''
        Applies z-score normalization on each z coordinate, grouping each voxel by their z coordinate for the normalization.

        This is to prevent seperate slices on the z axis when performing k-means clustering
        '''
        

        df = pd.read_csv(self.file)
        df.replace(-1, np.nan, inplace=True)


        # Try imputing before z-score normalization.
        """imputer = SimpleImputer(missing_values= np.nan, strategy="mean")
        imputed = imputer.fit_transform(df)
        df = pd.DataFrame(imputed, columns=df.columns)"""
        
        
        gene_cols = df.columns.difference(ignore)
        
        values = df[col].unique()
        for value in values:
            print(df.loc[df[col] == value, gene_cols])
            temp = df.loc[df[col] == value, gene_cols]
            df.loc[df[col] == value, gene_cols] = (temp - temp.mean())/temp.std()
            print(df.loc[df[col] == value, gene_cols])

        df.to_csv(new_path, index=False)

    def knn_imputation(self, new_path: str, ignore: list[str]) -> None:
        '''
        Apply knn_imputation
        
        finds the best value of k for KNN imputation
        '''
        df = pd.read_csv(self.file)
        new_df = df.copy()
        gene_cols = new_df.columns.difference(ignore)
        print(new_df[gene_cols])
        imputer = KNNImputer(n_neighbors=2)
        new_df[gene_cols] = imputer.fit_transform(new_df[gene_cols])
        print(new_df.isna().sum().sum())

        new_df.to_csv(new_path, index=False)

    def k_means_prep(self, new_path:str, ignore: list[str]) -> None:
        '''
        Prepares file for K-means clustering configurations set.
        '''
        df = pd.read_csv(self.file)
        gene_cols = df.columns.difference(ignore)
        cols = pd.Index(["X", "Y", "Z"]).append(gene_cols)
        df[cols].to_csv(new_path, index=False)

    def k_means_result(self, cluster_path:str, new_path: str, headers: list[str]) -> None:
        '''
        Concats results from K-means clustering
        '''
        
        df = pd.read_csv(self.file)
        other_df = pd.read_csv(cluster_path)
        print(df[headers])
        print(other_df.iloc[:, 1:])
        merged_df = pd.concat([df[headers], other_df.iloc[:, 1:]], axis=1)
        merged_df.to_csv(new_path, index=False)

    def calculate_structure_centroids(self) -> dict[str, (int, int, int)]:
        '''
        Retrieves the centroid of each structure
        '''
        
        pass

    def count_missing_expressions(self, missing: str) -> None:
        '''
        Counts missing expressions
        '''
        df = pd.read_csv(self.file)
        print(df.drop(columns=HEADERS))

        match missing:
            case "na":
                print(df.isna().sum().sum())
            case "-1":
                pass
            case _:
                pass
    
        