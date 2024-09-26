import time
from concurrent.futures import ThreadPoolExecutor
import sys
import os

import file_operations
import stl_operations

# Define the directory where all LDraw files are located
LDRAW_PATH = '../'
save_directory = './'
url_base = "https://library.ldraw.org/library/official/p/"
url_base_part = "https://library.ldraw.org/library/official/parts/"
parts_number = []
wrong_parts = []


def Input_lego_parts():
    global parts_number
    # Create a thread pool to process parts concurrently
    for i in range(len(parts_number)):
        if "pr" in parts_number[i]:
            parts_number[i] = parts_number[i].split("pr")[0]

    with ThreadPoolExecutor(max_workers=1) as executor:
        # Map each part number to the function that converts it to an STL
        executor.map(stl_operations.ldraw_to_stl, [part + '.dat' for part in parts_number], [part + '.stl' for part in parts_number])





def main():
    start_time = time.time()  # Startzeit messen

    global parts_number
    if len(sys.argv) != 3:
        print("Please provide the path to the csv file and the name of the set.")
        return

    if os.path.exists(sys.argv[1]) == False:
        print("The file does not exist.")
        return


    path = sys.argv[1]
    name = sys.argv[2]

    #Retrieve the parts number from the csv file
    parts_number = file_operations.read_input_files(path)

    #Setting up Environment for the project
    file_operations.setup_directories(name)

    #Check if all parts listed in the csv file exist
    check_if_parts_exist()

    if len(wrong_parts) != 0:
        print("Some parts are missing, STL file cannot be created.")
        print("Missing Subparts:")
        print(wrong_parts)
    else:

        print("Starting to get Parts")
        Input_lego_parts()
        time.sleep(3)

        for i in range(len(parts_number)):
            stl_operations.ldraw_to_stl(parts_number[i] + '.dat', parts_number[i] + '.stl')

        print("Scaling STL files to correct size: ")
        for i in range(len(parts_number)):
            stl_operations.scale_stl("./STL/" + parts_number[i] + '.stl', 0.395)

        end_time = time.time()  # Endzeit messen
        print(f"Program execution time: {end_time - start_time} seconds")  # Laufzeit ausgeben


def check_if_parts_exist():
    global parts_number
    for i in range(len(parts_number)):
        if "pr" in str(parts_number[i]):
            parts_number[i] = parts_number[i].split("pr")[0]
    with ThreadPoolExecutor(max_workers=16) as executor:
        executor.map(file_operations.get_dat_part, [part + '.dat' for part in parts_number])





if __name__ == "__main__":
    main()
