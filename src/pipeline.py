import os

from typing import Callable
from src.choice import print_constants, print_callable
from src.api.newapi import Api
from scripts.script import file_to_list
from src.constants import AVAILABLE_MICE, P56_MOUSE_REFERENCE_ID, P4_MOUSE_REFERENCE_ID
from src.utils.validation import is_valid


def exit_program():
    exit(0)

def api() -> None:
    '''
    Gathering Section_Images for the API
    '''
    AllenApi = Api()
    print("\nEnsure you have a CSV of voxels and a TXT file of section_data_set_ids")
    while True:
        paths = []

        print("Enter your CSV file path: ")
        csv_path = input().rstrip()
        
        while os.path.exists(csv_path):
            AllenApi.file = csv_path

            print("Enter your TXT file: ")
            txt_path = input().rstrip()
            paths.append(txt_path)
            
            while os.path.exists(txt_path):
                dataset_ids = file_to_list(txt_path)

                AllenApi.mouse = print_constants(
                    "Here are the available mice",
                    AVAILABLE_MICE,
                    "Which mouse do you want?"
                )
                print("Enter the directory you want to save the files in: ")
                dir = input().rstrip()
                if is_valid(dir):
                    os.mkdir(dir)
                
                AllenApi.reference_to_image()
                print(AllenApi.mouse)
                
def main():
    print("Starting...\n")

    while True:
        actions: [Callable] = {
            "Allen API": api,
            "Exit": exit_program
        }
        print_callable(
            "Here are your options.",
            actions,
            "What would you like to do with our program: "
        )
        
            

        