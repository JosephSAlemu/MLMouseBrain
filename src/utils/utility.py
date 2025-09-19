import os
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import modf
from sklearn.metrics import accuracy_score
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.model_selection import train_test_split
from collections.abc import Callable
from collections import Counter, defaultdict
from scipy.stats import zscore
from src.enums.inequality import Inequality
from src.enums.dimensions import Dimensions
from src.constants import HEADERS, HEADERS_V2, HEADERS_V4
from scripts.script import list_files_in_dir, read
from collections import defaultdict

class Utility():
    '''
    Class that holds functions that perform data filtering, feature reduction, plotting etc.
    '''
    def __init__(self, file: str = None):
        self.file = file
        pass
    
    def filter_genes(self, threshold: str | int | None, equality: Inequality, new_path: str) -> None:
        #df = read(self.file)
        match equality:
            case Inequality.LESS_THAN:
                df = read(self.file)
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
                df = read(self.file)
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
            df = read(self.file)
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
        
    def merge_csv_files(self, dir_path: str, file_name: str) -> None:
        '''
        Merges all csv files in a directory
        '''
        files = list_files_in_dir(dir_path)
        new_path = os.path.join(dir_path, file_name)
        headers = read(files[0]).columns

        with open(new_path, "w",) as new_file:
            writer = csv.writer(new_file)
            writer.writerow(headers)
            for file in files:
                df = read(file)
                for row in df.itertuples(index=False):
                    writer.writerow(row)
    
    def z_score_normalize(self, col: str, new_path: str, ignore: list[str]) -> None:
        '''
        Applies z-score normalization on each z coordinate, grouping each voxel by their z coordinate for the normalization.

        This is to prevent seperate slices on the z axis when performing k-means clustering
        '''
        
        df = read(self.file)
        df.replace(-1, np.nan, inplace=True)

        
        gene_cols = df.columns.difference(ignore)
        
        values = df[col].unique()
        for value in values:
            print(df.loc[df[col] == value, gene_cols])
            temp = df.loc[df[col] == value, gene_cols]
            df.loc[df[col] == value, gene_cols] = (temp - temp.mean())/temp.std()
            print(df.loc[df[col] == value, gene_cols])

        df.to_csv(new_path, index=False)

    def impute(self, method: str,  new_path: str) -> None:
        '''
        Applies SimpleImputer transform and 
        '''
        df = read(self.file)
        imp = SimpleImputer(missing_values=np.nan, strategy= method)
        new_df = pd.DataFrame(imp.fit_transform(df))
        new_df.columns = df.columns
        new_df.to_csv(new_path, index=False)

    def knn_impute(self, n: int, new_path: str, ignore: list[str]) -> None:
        df = read(self.file)
        gene_cols = df.columns.difference(ignore)
        print(df[gene_cols])
        imputer = KNNImputer(n_neighbors=n)
        df[gene_cols] = imputer.fit_transform(df[gene_cols])
        df.to_csv(new_path, index=False)
    
    def k_means_prep(self, new_path:str, ignore: list[str]) -> None:
        '''
        Prepares file for K-means clustering configurations set.
        '''
        df = read(self.file)
        gene_cols = df.columns.difference(ignore)
        cols = pd.Index(["X", "Y", "Z"]).append(gene_cols)
        df[cols].to_csv(new_path, index=False)

    def k_means_result(self, other_path:str, new_path: str, headers: list[str]) -> None:
        '''
        After performing K-means, concats the Structure information (ID, name, acronym) with the data

        Concats results from K-means clustering
        '''
        
        df = read(self.file)
        other_df = read(other_path)
        print(df[headers])
        print(other_df.iloc[:, 1:])
        merged_df = pd.concat([df[headers], other_df.iloc[:, 1:]], axis=1)
        merged_df.to_csv(new_path, index=False)

    def calculate_structure_centroids(self) -> dict[str, (int, int, int)]:
        '''
        Retrieves the centroid of each structure
        '''
        
        pass

    def get_common_voxels_and_genes(self, other_path: str, new_path_one: str, new_path_two: str, headers: list[str] = HEADERS) -> None:
        '''
        Finds the common voxel coordinates (X,Y,Z) and genes from both dataframes.
        
        Creates a new dataframe with the gene density 

        Must have X,Y,Z columns in both dataframes.
        '''
        df = read(self.file)
        other_df = read(other_path)
        if headers == HEADERS:
            df[headers] = df[headers].astype(float)
            other_df[headers] = other_df[headers].astype(float)

        # Reminder to self: _x is left and _y is right
        match = df.merge(other_df, how = 'inner', left_on=headers, right_on=headers)
        
        df_match = match[headers + [gene for gene in match.columns if "_x" in gene]]
        other_match = match[headers + [gene for gene in match.columns if "_y" in gene]]

        df_match = df_match.rename(columns=lambda col: col.rstrip("_x"))
        other_match = other_match.rename(columns=lambda col: col.rstrip("_y"))

        df_match.to_csv(new_path_one, index=False)
        other_match.to_csv(new_path_two, index=False)
    
    def distinct_structures(self, new_path: str) -> dict:
        '''
        Given a csv file that has a structure_name column, create a text file with the occurence of that structure

        Args:
            self.file = path of the csv file
            new_path = path of the text file for the results

        Returns:
            None
        '''
        df = read(self.file)

        structure_count = defaultdict(int)

        for row in df.itertuples():
            structure_count[row.structure_name] += 1
        
        with open(new_path, mode = "w") as file:
            for key, value in structure_count.items():
                file.write(f"{key} := {value}\n")

    def plot_cluster_structures(self) -> None:
        '''
        Given a csv file that that a cluster_id column and a structure id

        Args:
            self.file = path of the csv file

        Returns:
            None
        '''
        pass

    def bin_voxels(self, dir_path: str, file_path: str) -> None:
        '''
        Takes in a gene name as a string.

        Opens the file and retrieves the voxels.

        Bin all the voxels in all the files in the genes they belong to.

        Bins are a 9x9 grid based on the x and y value.

                           ___________
                n.0-n.33  |___|___|___|
      (X Coord) n.34-n.66 |___|___|___|
                n.67-n.99 |___|___|___|
                          n.0  n.34 n.67 
                           -    -    -
                          n.33 n.66 n.69
                            (Y Coord)

        ALSO binned on the rounded z coordinate binned
            
        '''
        new_path = os.path.join(dir_path, file_path)

        df = read(self.file)
        with open(new_path, "w") as new_file:
            writer = csv.writer(new_file)
            writer.writerow(df.columns)
            df.rename(columns={"Structure-ID": "structure"}, inplace=True)

            for row in df.itertuples():
                x = float(row.X)
                y = float(row.Y)
                z = float(row.Z)
                x_rem, x_num = modf(x)
                y_rem, y_num = modf(y)
                                    
                if x_rem >= .34 and x_rem < .67:
                    x_num = x_num+.34
                
                elif x_rem >= .67:
                    x_num = x_num+.67

                elif y_rem >= .34 and y_rem <.67:
                    y_num = y_num+.34
                                
                elif y_rem >= .67:
                    y_num = y_num + .67
                
                z_num = round(z)

                writer.writerow([row.structure, x_num, y_num, z_num])