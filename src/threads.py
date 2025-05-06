from threading import Thread
from image import (calculate_density, fill_negative_expressions)
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
        
        for index in range(self.start, self.stop+1):
            gene = file.iloc[index]["Gene"]
            calculate_density(gene)
    
    def retrieve_images(self) -> None:
        """
        find a way to thread the section images
        """
        fill_negative_expressions()


def use_threads(length: int, thread_count: int, file: str|None) -> None:
    '''
    Takes in the laptop number according to the lab and then retrieves all the genes for it using threading.
    '''
    file = rf"./Datasets/Outputs/P4_Section_Laptop{file_number}.csv"
    count = 0
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
  

if __name__ == "__main__":
    #file_numer = 8
    #use_threads(259, 7, f"./Datasets/Outputs/P4_Section_Laptop{file_number}.csv")
    use_threads()
    