import pandas as pd
from collections.abc import Callable
from typing import Any
from threading import Thread
from src.image.image import (calculate_density_and_voxels, fill_negative_density, get_expressions, download_section_images)
from src.utils.filter import (partition_section_images)
from src.enums.actions import Action
from src.api.newapi import Api

class Threads:
    def __init__(self, start: int, stop: int, file: str|int = None):
        self.start = start
        self.stop = stop
        self.file = file
        pass
            
    def retrieve_voxels(self) -> None:
        file = pd.read_csv(self.file)
        
        for index in range(self.start, self.stop+1):
            gene = file.iloc[index]["Gene"]
            calculate_density_and_voxels(gene)
    
    def reanalysis(self) -> None:
        """
        threads reference-to-image
        """
        fill_negative_density(self.file, self.start, self.stop)
    
    def create_files(self) -> None:
        partition_section_images(self.start, self.stop)

    def create_dataframe(self) -> None:
        get_expressions(self.file, self.start, self.stop)

    def download_section_images(self) -> None:
        """
        threads downloading all binary section images
        """
        download_section_images(self.start, self.stop)

    def threaded_func(self, func: Callable, args: list[Any]) -> None:
        func(*args, thread_chunk_size = (self.start, self.stop))




def use_threads(length: int, thread_count: int, func: Action | None, caller: Callable, arguments: list[Any] | None, file: str|int = None) -> None:
    '''
    Takes in the laptop number according to the lab and then retrieves all the genes for it using threading.
    '''
    thread_instances = []
    threads = []
    increment = length//thread_count
    count = 0
    match func:
        case Action.REANALYSIS:
            while count < length:
                #append threads in a list
                print(f"{count} - {count+increment-1}")
                thread_instances.append(Threads(count, count+increment-1, file))
                count+=increment

            for instance in thread_instances:
                thread = Thread(target = instance.reanalysis)
                threads.append(thread)
                thread.start()

        case Action.CREATE_FILES:
            count = 1

            while count <= length:
                print(f"{count}-{count+increment}")
                thread_instances.append(Threads(count, count+increment, file))
                count+=increment

            for instance in thread_instances:
                thread = Thread(target = instance.create_files)
                threads.append(thread)
                thread.start()
        case Action.CREATE_DATAFRAME:
            while count < length:
                #append threads in a list
                print(f"{count} - {count+increment}")
                thread_instances.append(Threads(count, count+increment, file))
                count+=increment

            for instance in thread_instances:
                thread = Thread(target = instance.create_dataframe)
                threads.append(thread)
                thread.start()

        case Action.RETRIEVE_IMAGES:
            while count < length:
                print(f"{count}-{count+increment}")
                thread_instances.append(Threads(count, count+increment, file))
                count+=increment
            
            for instance in thread_instances:
                thread = Thread(target = instance.download_section_images)
                threads.append(thread)
                thread.start()

        case None:
            while count < length:
                #append threads in a list
                print(f"{count} - {count+increment}")
                thread_instances.append(Threads(count, count+increment))
                count+=increment
            
            for instance in thread_instances:
                thread = Thread(target = instance.threaded_func, args=(caller, arguments))
                threads.append(thread)
                thread.start()
        


    for thread in threads:
            thread.join()

def thread_threads(length: int, thread_count: int, func: int):
    """
    to thread threaded functions to be more efficient.
    """
    threads = []
    for file_no in range(FILE_START, FILE_END):
        thread = Thread(target = use_threads, args=(length, thread_count, file_no, func))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    #file_number = 8
    #use_threads(259, 7, f"./Datasets/Outputs/P4_Section_Laptop{file_number}.csv")

    #thread_threads(7535, 11, REANALYSIS)



    #use_threads(8, 8, None, CREATE_FILES)
    #use_threads(7535, 11, 2, CREATE_DATAFRAME)
    #use_threads(19608, 43, None, RETRIEVE_IMAGES)
    use_threads(1547475, 25, 1, CREATE_DATAFRAME)
    