import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from src.constants import HEADERS

class Kmeans():
    def __init__(self):
        pass

    def elbow_plot(self, kmax: int) -> None:
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