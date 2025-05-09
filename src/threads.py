from threading import Thread
from image import (calculate_density_and_voxels, fill_negative_density)
#from api import chunk
import pandas as pd


class Threads:
    def __init__(self, start: int, stop: int, file: str|int|None):
        self.start = start
        self.stop = stop
        self.file = file
        pass
            

    def retrieve_voxels(self) -> None:
        file = pd.read_csv(self.file)
        
        for index in range(self.start, self.stop+1):
            gene = file.iloc[index]["Gene"]
            calculate_density_and_voxels(gene)
    
    def retrieve_images(self) -> None:
        """
        find a way to thread the section images
        """
        fill_negative_density(self.file, self.start, self.stop)
        


def use_threads(length: int, thread_count: int, file: str|int|None) -> None:
    '''
    Takes in the laptop number according to the lab and then retrieves all the genes for it using threading.
    '''
    count = 0
    thread_genes = length//thread_count
    
    thread_instances = []
    threads = []
    while count < length:
        #append threads in a list
        print(f"{count} - {count+thread_genes-1}")
        thread_instances.append(Threads(count, count+thread_genes-1, file))
        count+=thread_genes

    for instance in thread_instances:
        thread = Thread(target = instance.retrieve_images)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
  

if __name__ == "__main__":
    #file_number = 8
    #use_threads(259, 7, f"./Datasets/Outputs/P4_Section_Laptop{file_number}.csv")

    use_threads(7535, 11, 7)
    