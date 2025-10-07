import os
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from joblib import Parallel, delayed
from math import modf
from sklearn.metrics import accuracy_score
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.model_selection import train_test_split
from collections.abc import Callable
from collections import Counter, defaultdict
from scipy.stats import zscore
from src.enums.inequality import Inequality
from src.enums.dimensions import Dimensions
from src.constants import HEADERS, HEADERS_V2, HEADERS_V4, STRUCTURE_ID_ABBREVIATIONS
from scripts.script import list_files_in_dir, read, drop_columns
from collections import defaultdict


class Utility:
    '''
    Class that holds functions that perform data filtering, feature reduction, plotting etc.
    '''

    def __init__(self, file: str = None):
        self.file = file
        pass

    def filter_genes(
        self, 
        threshold: float,
        headers: list[str],
        new_path: str = None
    ) -> None:
        '''
        Default threshold is -1

        You can pass a threshold value
        '''
        df = read(self.file)
        temp = df.drop(columns = headers)
        columns = list(temp.columns)
        
        for col in temp.columns:
            print(temp[col])
            if (temp[col] == -1).all() or (temp[col] < threshold).all():
                columns.remove(col)
    
        print(df[headers+columns])

        if new_path:
            df[headers+columns].to_csv(new_path, index=False)

    def filter_voxels_and_genes(
        self,
        dimension: Dimensions,
        threshold: str | int | None,
        equality: Inequality,
        new_path: str,
    ) -> None:
        """
        filters all rows, columns, or both based on the threshold provided

        creates a new CSV file for the result
        """
        match equality:
            case Inequality.LESS_THAN:
                df = read(self.file)
                gene_cols = df.columns.difference(HEADERS)

                mask = (df[gene_cols] == 0) | (df[gene_cols] == -1)

                bad_ratio_row = mask.sum(axis=1) / len(gene_cols)

                bad_ratio_col = mask.sum(axis=0) / df.shape[0]

                clean_gene_cols = bad_ratio_col[
                    bad_ratio_col < threshold
                ].index.tolist()
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
        """
        retrieves the voxel coordinate and it's assigned gene expression

        Why? -> We want to see the distribution and mean of the gene expressions and then normalize them
        """
        values = None
        if coordinate == "X" or coordinate == "Y" or coordinate == "Z":
            df = read(self.file)
            values = list(set(df[coordinate].astype(float)))
            values.sort()
            my_dict = dict([(i, []) for i in values])
            print(my_dict)
            for _, row in df.iterrows():
                key = float(row[coordinate])
                if key in my_dict:
                    my_dict[key].extend(row[3:])

            return my_dict

        else:
            raise ValueError(f"invalid coordinate: {coordinate}")

    def merge_csv_files(self, dir_path: str, file_name: str) -> None:
        """
        Merges all csv files in a directory
        """
        files = list_files_in_dir(dir_path)
        new_path = os.path.join(dir_path, file_name)
        headers = read(files[0]).columns

        with open(
            new_path,
            "w",
        ) as new_file:
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

        Args:
            self.file: 
            col: the axis you want to z-score normalize on (ex: "Z")
            new_path: path of the new 
        '''

        df = read(self.file)
        df.replace(-1, np.nan, inplace=True)

        gene_cols = df.columns.difference(ignore)

        values = df[col].unique()
        for value in values:
            temp = df.loc[df[col] == value, gene_cols]
            df.loc[df[col] == value, gene_cols] = (temp - temp.mean()) / temp.std()

        df.to_csv(new_path, index=False)

    def impute(self, method: str, new_path: str) -> None:
        """
        Applies SimpleImputer transform and
        """
        df = read(self.file)
        imp = SimpleImputer(missing_values=np.nan, strategy=method)
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

    def k_means_prep(self, new_path: str, ignore: list[str]) -> None:
        """
        Prepares file for K-means clustering configurations set.
        """
        df = read(self.file)
        gene_cols = df.columns.difference(ignore)
        cols = pd.Index(["X", "Y", "Z"]).append(gene_cols)
        df[cols].to_csv(new_path, index=False)

    def k_means_result(
        self, other_path: str, new_path: str, headers: list[str]
    ) -> None:
        """
        After performing K-means, concats the Structure information (ID, name, acronym) with the data

        Concats results from K-means clustering
        """

        df = read(self.file)
        other_df = read(other_path)
        print(df[headers])
        print(other_df.iloc[:, 1:])
        merged_df = pd.concat([df[headers], other_df.iloc[:, 1:]], axis=1)
        merged_df.to_csv(new_path, index=False)

    def calculate_structure_centroids(self) -> dict[str, (int, int, int)]:
        """
        Retrieves the centroid of each structure
        """

        pass

    def get_common_voxels_and_genes(
        self,
        other_path: str,
        new_path: str = None,
        new_path_other: str = None,
        headers: list[str] = HEADERS,
        df_drop: list[str] = None,
        df_drop_other: list[str] = None,
        invert: bool = False,
        invert_other: bool = False,
    ) -> None:
        '''
        Finds the common voxel coordinates (X,Y,Z) and genes from both dataframes.

        Creates a new dataframe with the gene density

        Must have X,Y,Z columns in both dataframes.
        Args:
            self.file = path of the csv file
            other_path = path of the other csv file
            new_path = path for the new csv file
            new_path_other = path for second new csv file if needed

        Returns:
            None
        '''
        
        df = drop_columns(self.file, df_drop, invert)
        other_df = drop_columns(other_path, df_drop_other, invert_other)

        df[HEADERS] = df[HEADERS].astype(float)
        other_df[HEADERS] = other_df[HEADERS].astype(float)
        
        # Reminder to self: _x is left and _y is right
        match = df.merge(other_df, how="inner", left_on=headers, right_on=headers)

        
        if new_path and new_path_other:
            df_match = match[headers + [gene for gene in match.columns if "_x" in gene]]
            other_match = match[headers + [gene for gene in match.columns if "_y" in gene]]

            df_match = df_match.rename(columns=lambda col: col.rstrip("_x"))
            other_match = other_match.rename(columns=lambda col: col.rstrip("_y"))

            print(df_match)
            print(other_match)
            #df_match.to_csv(new_path, index=False)
            #other_match.to_csv(new_path_other, index=False)
        
        elif new_path:
            match.to_csv(new_path, index=False)
        
        else:
            print(match)
        
    def distinct_structures(self, new_path: str = None) -> None:
        '''
        Given a csv file that has a structure_name column, create a text file with the occurence of that structure

        Args:
            self.file: path of the csv file
            new_path = path of the text file for the results

        Returns:
            None
        '''
        df = read(self.file)


        #df.rename(columns={"Structure-ID": "structure"}, inplace=True)

        count = df["structure_names"].value_counts()

        if new_path:
            with open(new_path, "w") as newfile:
                newfile.write(count.to_string())
        else: 
            print(count)

    def plot_cluster_structures(self) -> None:
        """
        Given a csv file that that a cluster_id column and a structure id

        Args:
            self.file = path of the csv file

        Returns:
            None
        """
        pass

    def bin_voxels(self, dir_path: str, file_path: str) -> None:
        """
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

        """
        pass

    def round_voxels(self, dir_path: str, file_path: str) -> None:
        '''
        Rounds voxels.
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
                x_num = round(x)

                y_num = round(y)

                z_num = round(z)

                writer.writerow([row.structure, row.Section_Dataset , x_num, y_num, z_num])

    def separate_null_rows(self, new_path: str, other_new_path: str) -> None:
        '''
        This method takes in a dataframe\n
        and splits rows into two dataframes\n 
        by null and not null Structure-IDs

        Args:
            self.file: path to csv file
            new_path: path of the file with null rows
            other_new_path: path of the file with the non-null rows
        
        Returns:
            SideEffect: Creates two dataframe: one with no Structure-IDs and one with Structure-IDs
        '''

        df = read(self.file)


        df[df['Structure-ID'].isnull()].to_csv(new_path, index=False)
        df[df['Structure-ID'].notna()].to_csv(other_new_path, index=False)

    def check_conflicting_voxel_structures(self, new_path: str = None) -> dict[dict[int]]:
        '''
        Checks if a dataframe has the same voxel with different Structure-IDs associated with it.

        Args:
            self.file: path to csv file
            new_path: path of file to save results
        '''
        
        df = read(self.file)
        df.rename(columns={"Structure-ID": "structure"}, inplace=True)

        frequency = {}
        for row in df.itertuples():
            key = (row.X, row.Y, row.Z)
            id = row.structure
            if key not in frequency:
                frequency[key] = {}

            if id not in frequency[key]:
                frequency[key][id] = 0
            
            frequency[key][id] += 1

        if new_path:
            #with open(new_path, "w") as file:
            for key, value in frequency.items():
                #file.write(f"{key}:\n   {value}\n")
                if len(value) > 1:
                    print(f"{key}:\n   {value}\n")
        else:
            return frequency

    def create_unique_section_id_dataframe(self, dir_path) -> None:
        df = read(self.file)
        for section, sub_df in df.groupby("Section_Dataset"):
            filename = os.path.join(dir_path, f"{section}.csv")
            sub_df.to_csv(filename, index=False)
            print(f"Saved {filename}")

    def add_structures_name(self) -> None:
        df = read(self.file)
        df["structure_names"] = df["Structure-ID"].map(STRUCTURE_ID_ABBREVIATIONS)
        #print(df[["Structure-ID", "structure_names"]])
        df.to_csv(self.file, index=False)

    def pick_random_structure(self, new_path) -> None:

        frequency = self.check_conflicting_voxel_structures()
        df = read(self.file)

        with open(new_path, "w") as file:
            writer = csv.writer(file)
            writer.writerow(df)
            for key, value in frequency.items():
                print(f"{key}:\n   {value}\n")
                count = 0
                top = None
                temp = []
                for struct, val in value.items():
                    if val > count:
                        count = val
                        top = struct
                        temp.clear()
                        temp.append(top)
                    elif val == count:
                        temp.append(struct)
                        top = random.choice(temp)
                x,y,z = key
                writer.writerow([top, x, y, z])
    