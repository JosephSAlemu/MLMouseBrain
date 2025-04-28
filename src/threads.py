from threading import Thread
from image import calculate_density
#from api import chunk
import pandas as pd


class Threads:
    def __init__(self, start, stop, file):
        self.start = start
        self.stop = stop
        self.file = file
        pass
            

    def retrieve_voxels(self) -> None:
        file = pd.read_csv(self.file)
        
        print(f"start: {self.start}")
        print(f"stop: {self.stop}")
        for index in range(self.start, self.stop+1):
            gene = file.iloc[index]["Gene"]
            print(f"index: {index} gene: {gene}")

            calculate_density(gene)
        
        

if __name__ == "__main__":
    file = rf"./Datasets/Outputs/P4_Section_Laptop8.csv"
    length = 259
    count = 0
    thread_count = 7
    thread_genes = length//thread_count
    
    thread_instances = []
    threads = []
    while count < length:
        #append threads in a list
        thread_instances.append(Threads(count, count+thread_genes-1, file))
        count+=thread_genes

    for instance in thread_instances:
        

        thread = Thread(target = instance.retrieve_voxels)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    