import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from src.constants import HEADERS

class KNN():
    def __init__(self):
        pass

    def elbow_plot(self, kmax: int) -> None:
        '''
        Apply knn_imputation
        
        finds the best value of k for KNN imputation

        1. Iterate over k
        2. Iterate over the dataframe and remove one gene n times, making a copy of each dataframe.
        3. Impute value n_neighbors = k on each n copies.
        4. Create a correlation matrix between imputed knn values and actual values.
        '''
        df = pd.read_csv("Datasets/Outputs/P4_50_RE_CLN_NewDenS.csv")
        df = df.drop(columns=HEADERS)
        print(df)
        sse = []
        for k in range(1, kmax+1):
            kmeans = KMeans(n_clusters=k).fit(df)
            sse.append(kmeans.inertia_)
            
        plt.plot(range(1, kmax+1), sse)
        plt.xticks(range(1, kmax+1))
        plt.xlabel("Number of Clusters")
        plt.ylabel("SSE")
        plt.show()