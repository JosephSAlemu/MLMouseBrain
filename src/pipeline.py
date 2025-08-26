import os

def pipleline() -> None:
    '''
    Starts the data pipeline
    '''
    print("Start data pipeline? (Y/N): ")
    while True:
        ans = input().rstrip().upper()
        if ans == "Y":
            api()
        elif ans == "N":
            break
        else:
            print("give a valid input")

def api() -> None:
    '''
    Gathering Section_Images for the API
    '''
    print("Ensure you have a CSV of voxels and a TXT file of section_data_set_ids")
    while True:
        paths = []

        print("Enter your CSV file path: ")
        path = input().rstrip()
        paths.append(path)
        while os.path.exists(path):
            print("Enter your TXT file: ")
            path = input().rstrip()
            paths.append(path)

            while os.path.exists(path):
                


        

pipleline()