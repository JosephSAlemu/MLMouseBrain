from collections.abc import Callable
import matplotlib.pyplot as plt
import pandas as pd

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
    
    def histogram(self, bins: list[int], scale: str, x_name: str, y_name: str, title: str) -> None:
        counts = self.bin_expression_values(bins)
        print(counts)
        plt.bar(counts.index.astype(str), counts.values)
        plt.yscale(scale)
        plt.xlabel(x_name)
        plt.ylabel(y_name)
        plt.title(title)
        plt.show()

    def bin_expression_values(self, bins: list[int] = None) -> pd.Series:
        """
        Bins expression values by custom bins or the following by default.

        bins[0] = [-1]
        bins[1] = [0]
        bins[2] = (0, .001]
        bins[3] = (.001, .01]
        bins[4] = (.01, .1]
        bins[4] = (.1, 1]

        returns the binned values
        """
        if bins == None:
            bins = [0, .001, .01, .1, 1]

        values = []
        df = pd.read_csv(self.file)
        df = df[df.columns.difference(HEADERS)]
        print(df)

        for _, row in df.iterrows():

            for cell in row:
                values.append(cell)

        binned = pd.cut(values, bins=bins, right=True)

        counts = binned.value_counts()

        return counts
