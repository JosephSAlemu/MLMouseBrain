import os

from typing import Callable
from src.enums.actions import Action
from src.choice import print_constants, print_callable
from src.threads import use_threads
from src.api.newapi import Api
from src.constants import AVAILABLE_MICE
from src.utils.validation import is_valid
from src.utils.filter import retrieve_section_id_from_gene
from scripts.script import length, read

def exit_program():
    exit(0)

def api() -> None:
    '''
    function to handle choices for the api class
    '''
    AllenApi = Api()
    csv_path = None
    txt_path = None
    print("\n--Ensure you have a CSV of voxels and a TXT file of section_data_set_ids--\n")

    while True:
        print("--Enter your CSV file path: ")
        csv_path = input().rstrip()
        
        if not is_valid(csv_path):
            break

    while True:
        print("\n--Do you have a TXT file of section_dataset_ids? (Y/N): ")
        answer = input().rstrip().upper()

        if answer == "Y":
            print("--Enter your TXT file: ")
            txt_path = input().rstrip()
                
            if not is_valid(txt_path):
                break
        
        elif answer == "N":
            print("--Enter a TXT file path for your section_dataset_ids: ")
            txt_path = input().rstrip()
            if is_valid(txt_path):
                # Implement
                pass

    AllenApi.mouse = print_constants(
        "Here are the available mice",
        AVAILABLE_MICE,
        "Which mouse do you want?"
    )
    
    print("--Enter the directory you want to save the files in: ")
    dir = input().rstrip()
    if is_valid(dir):
        os.mkdir(dir)
    

    print("--Do you want to multithread the call? (Y/N): ")
    answer = input().rstrip().upper()
    while True:
        if answer == "Y":
            size = length(csv_path)
            while True:
                print("--How many threads do you want?: ")
                threads = input().rstrip()
                if threads.isdigit():
                    threads = int(threads)
                    if size%threads == 0:
                        use_threads(size, threads, Action.REF_TO_IMG, AllenApi, [csv_path, txt_path, dir])
                        
                print("--Input a valid option\n")
            
        elif answer == "N":        
            AllenApi.start_ref_to_img(csv_path, txt_path, dir)
    
def image() -> None:
    '''
    function to hold choices for the image class
    '''
    print("\n--Ensure you have a directory of the seed pixels and section_images--\n")

    csv_path = None
    dir_path = None

    while True:
        print("\n--Do you want to retrieve all chunk or one chunks? (ALL/ONE): ")
        answer = input().rstrip().upper()
        if answer == "ALL":
            print("--Enter the directory path for the chunk files: ")
            csv_path = input().rstrip()
                
        elif answer == "ONE":
            print("--Enter the file path for the chunk: ")
            csv_path = input().rstrip()

                
        if not is_valid(csv_path):
            break
    
    
    while True:
        print("\n--Do you want to download the Binarized Images? (Y/N): ")
        answer = input().rstrip().upper()

        if answer == "Y":
            print("--Enter the directory path for downloading images ")
            dir_path = input().rstrip()
                
            if not is_valid(dir_path):
                api = Api()
                df = read(csv_path)
                for row in df.itertuples():
                    api.download_binarized_image(row.Section_Image, dir_path)
        
        elif answer == "N":
            pass

                
def main():
    print("Starting...\n")

    actions: [Callable] = {
        "Allen API": api,
        "Gene Expression Measurement": image,
        "Exit": exit_program
    }

    print_callable(
        "Here are your options.",
        actions,
        "What would you like to do with our program: "
    )