import matplotlib.pyplot as plt
import pandas as pd
from collections.abc import Callable
from src.constants import HEADERS

class Visualize():
    '''
    The purpose of this class is to be used for visualizing data (bar plots, histograms, pie charts, etc. )
    
    '''
    def __init__(self, file: str = None):
        self.file = file

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

        df = df[df.columns.difference(HEADERS)]
        print(df)

        for _, row in df.iterrows():

            for cell in row:
                values.append(cell)

        split = {}

        if e_bins == True:
            values = pd.Series(values)

            zero_mask = values == 0
            zero_count = zero_mask.sum()
            split[zero_count] = "0"

            print(zero_count)

            neg_mask = values == -1
            neg_count = neg_mask.sum()
            split[neg_count] = "-1"

            values = values[~neg_mask][~zero_mask]
            print("working")

        binned = pd.cut(values, bins=bins, right=right)

        counts = binned.value_counts(sort=False)
        for key, value in split.items():
            counts = pd.Series([key], index=[value])._append(counts)


        return counts
