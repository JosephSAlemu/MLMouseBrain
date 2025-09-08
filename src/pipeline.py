import os

from typing import Callable
from src.enums.actions import Action
from src.choice import print_constants, print_callable
from src.threads import use_threads
from src.api.newapi import Api
from src.image.newimage import Image
from src.constants import AVAILABLE_MICE
from src.utils.validation import is_valid
from src.utils.filter import retrieve_section_id_from_gene
from scripts.script import length, read

def exit_program() -> None:
    exit(0)

def multithread(csv_path: str) -> tuple | None:
    while True:
        print("--Do you want to multithread the call? (Y/N): ")
        answer = input().rstrip().upper()
        if answer == "Y":
            size = length(csv_path)
            while True:
                print(f"--How many threads do you want? (Must be a factor of {size}): ")
                threads = input().rstrip()
                if threads.isdigit():
                    threads = int(threads)
                    if size%threads == 0:
                        return (size, threads)
                        
                print("--Input a valid option\n")
            
        elif answer == "N":
            return None

def api() -> None:
    actions: [Callable] = {
        "Reference To Image": ref_to_image,
        "Image To Reference": image_to_ref
    }

    print_callable(
        "Here are your options.",
        actions,
        "Which API call would you like to do: "
    )

def ref_to_image() -> None:
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
    dir_path = input().rstrip()
    if is_valid(dir_path):
        os.mkdir(dir_path)
    
    response = multithread(csv_path)
    if response is not None:
        size, threads = response
        use_threads(size, threads, None, AllenApi.start_ref_to_img, [csv_path, txt_path, dir_path])
    else:
        AllenApi.start_ref_to_img(csv_path, txt_path, dir_path)
    
    
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
            AllenApi = Api()

            print("--Enter the directory path for downloading images ")
            dir_path = input().rstrip()
                
            if not is_valid(dir_path):
                response = multithread(csv_path)
                print("idk")

                if response is not None:
                    size, threads = response
                    use_threads(size, threads, None, AllenApi.start_download_binarized, [csv_path, dir_path])
                else:
                    df = read(csv_path)
                    for row in df.itertuples():
                        AllenApi.download_binarized_image(row.Section_Image, dir_path)
                
                break
        
        elif answer == "N":
            pass
    
    while True:
        print("\n--Do you want to retrieve gene_expression density for your csv file(s)? (Y/N): ")
        answer = input().rstrip().upper()

        if answer == "Y":
            print("--Enter the directory path for the new chunk files ")
            new_dir = input().rstrip()
                
            if not is_valid(dir_path):
                image = Image()
                image.create_file(csv_path, dir_path, new_dir, resolution=160)
        
        elif answer == "N":
            pass
        

def image_to_ref() -> None:
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