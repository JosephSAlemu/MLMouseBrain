from threading import Thread
#from api import chunk
import pandas as pd


#Literally trash this. Race conditions may ruin the entire thing.
class Threads:
    def __init__(self, threads):
        self.threads = threads
        self.range = None
        self.file = None
        self.counter = 0
        pass
    
    def threaded_chunks_function(self, thread_id) -> None:
        if self.file == None:
            file = pd.read_csv(r'./Datasets/Outputs/NewDenC_Microns.csv')
            self.file = file
            self.range = int(len(file['X'])//5)
        start = thread_id * self.range
        end = start + self.range - 1
        while start <= end:
            #chunk(self.file['X'][start], self.file['Y'][start], self.file['Z'][start])
            start+=1
        print("\n")
        
        

if __name__ == "__main__":
    instance = Threads(5)
    threads = []
    for j in range(instance.threads):

        thread = Thread(target = instance.threaded_chunks_function, args = [j] )
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    print(instance.counter)