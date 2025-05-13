from threading import Thread
from image import (calculate_density_and_voxels, fill_negative_density, get_expressions)
from filter import (partition_section_images)
from constants import (RETRIEVE_VOXELS, RETRIEVE_IMAGES, CREATE_FILES, CREATE_DATAFRAME)
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
    
    def create_files(self) -> None:
        partition_section_images(self.start, self.stop)

    def create_dataframe(self) -> None:
        get_expressions(self.file, self.start, self.stop)
        

def use_threads(length: int, thread_count: int, file: str|int|None, func: int) -> None:
    '''
    Takes in the laptop number according to the lab and then retrieves all the genes for it using threading.
    '''
    thread_instances = []
    threads = []
    increment = length//thread_count

    if func == RETRIEVE_IMAGES:
        count = 0

        while count < length:
            #append threads in a list
            print(f"{count} - {count+increment-1}")
            thread_instances.append(Threads(count, count+increment-1, file))
            count+=increment

        for instance in thread_instances:
            thread = Thread(target = instance.retrieve_images)
            threads.append(thread)
            thread.start()
        
        
    elif func == CREATE_FILES:
        count = 1

        while count <= length:
            print(f"{count}-{count+increment}")
            thread_instances.append(Threads(count, count+increment, file))
            count+=increment

        for instance in thread_instances:
            thread = Thread(target = instance.create_dataframe)
            threads.append(thread)
            thread.start()

    elif func == CREATE_DATAFRAME:
        count = 0

        while count < length:
            #append threads in a list
            print(f"{count} - {count+increment-1}")
            thread_instances.append(Threads(count, count+increment-1, file))
            count+=increment

        for instance in thread_instances:
            thread = Thread(target = instance.create_dataframe)
            threads.append(thread)
            thread.start()
        
    for thread in threads:
            thread.join()

if __name__ == "__main__":
    #file_number = 8
    #use_threads(259, 7, f"./Datasets/Outputs/P4_Section_Laptop{file_number}.csv")

    #use_threads(7535, 11, 2, RETRIEVE_IMAGES)
    #use_threads(8, 8, None, CREATE_FILES)
    use_threads(7535, 11, 1, CREATE_DATAFRAME)




    