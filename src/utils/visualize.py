import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections.abc import Callable
from src.constants import HEADERS
from scripts.script import read

class Visualize():
    '''
    The purpose of this class is to be used for visualizing data (bar plots, histograms, pie charts, etc. )
    
    '''
    def __init__(self, file: str = None, ignore: list[str] = None):
        self.file = file
        self.ignore = ignore

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
    
    def histogram(self, scale: str, x_name: str, y_name: str, title: str, bins: list[int] = None, e_bins: bool = False, right: bool = False) -> None:
        counts = self.bin_expression_values(bins, e_bins, right)
        print(counts)
        plt.bar(counts.index.astype(str), counts.values)
        plt.yscale(scale)
        plt.xlabel(x_name)
        plt.ylabel(y_name)
        plt.title(title)
        plt.show()

    def bin_expression_values(self, bins: list[int] = None, e_bins: bool = False, right: bool = False) -> pd.Series:
        """
        Bins expression values by custom bins or the following by default.

        bins[0] = (0, .001]
        bins[1] = (.001, .01]
        bins[2] = (.01, .1]
        bins[3] = (.1, 1]

        e_bins are for adding missing and invalid gene expression bins.

        returns the binned values
        """
        if bins == None:
            bins = [0.0, .001, .01, .1, 1]
        
        values = []

        df = pd.read_csv(self.file)

        df = df[df.columns.difference(self.ignore)]

        for _, row in df.iterrows():

            for cell in row:
                values.append(cell)

        split = {}

        if e_bins == True:
            values = pd.Series(values)

            zero_mask = values == 0
            zero_count = zero_mask.sum()
            split[zero_count] = "0"


            neg_mask = values == -1
            neg_count = neg_mask.sum() + df.isna().sum().sum()
            split[neg_count] = "-1"

            values = values[~neg_mask][~zero_mask]

        binned = pd.cut(values, bins=bins, right=right)

        counts = binned.value_counts(sort=False)
        for key, value in split.items():
            counts = pd.Series([key], index=[value])._append(counts)


        return counts

    def idk(self):

        # Load CSV
        df = read(self.file)

        structure_stats = df.groupby("Structure-ID").agg({
            "X": "mean",
            "Y": "mean",
            "voxRowNum": "count"
        }).reset_index()
        structure_stats.rename(columns={"voxRowNum": "voxel_count"}, inplace=True)

        cluster_stats = df.groupby("Cluster_13").agg({
            "X": "mean",
            "Y": "mean"
        }).reset_index()

        plt.figure(figsize=(8, 6))

        colors = plt.cm.tab20(np.linspace(0, 1, len(structure_stats)))

        for i, row in structure_stats.iterrows():
            plt.scatter(row["X"], row["Y"],
                        s=row["voxel_count"],  # scale size to voxel count
                        color=colors[i],
                        alpha=0.6,
                        label=f"Structure {int(row['Structure-ID'])}")

        plt.scatter(cluster_stats["X"], cluster_stats["Y"],
                    c="black", marker=".", s=100, label="Cluster Centers")

        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("Structure Centroids with Cluster Centers")
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)
        plt.tight_layout()
        plt.show()