import os
import shutil
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor

wrong_parts = []
save_directory = './'
url_base = "https://library.ldraw.org/library/official/p/"
url_base_part = "https://library.ldraw.org/library/official/parts/"

def read_input_files(path):
    """
    Reads the input CSV file and extracts the parts numbers.
    """
    df = pd.read_csv(path)
    parts_number = df.iloc[:, 0].tolist()
    parts_number = [str(i) for i in parts_number]
    parts_number = list(dict.fromkeys(parts_number))  # Remove duplicates
    return parts_number

def setup_directories(name):
    """
    Sets up the working directories and copies base files.
    """
    print("Creating new directory")
    os.makedirs(name, exist_ok=True)

    print("Changing directory")
    os.chdir(name)
    src_folder = '../Base files'
    dest_folder = '.'
    for filename in os.listdir(src_folder):
        # Construct full file path
        src_file = os.path.join(src_folder, filename)
        dest_file = os.path.join(dest_folder, filename)

        # Copy only files (skip directories)
        if os.path.isfile(src_file):
            shutil.copy2(src_file, dest_file)
            print(f"Copied: {src_file} to {dest_file}")
    os.makedirs('STL', exist_ok=True)

def download_file(url, save_directory, file_name):
    """
    Downloads a file from the given URL if it doesn't already exist in the save directory.
    """
    global wrong_parts
    # Create the full file path
    file_path = os.path.join(save_directory, file_name)

    # Check if the file already exists
    if os.path.isfile(file_path):
        print(f"File '{file_name}' already exists. Skipping download.")
        return  # Exit the function early if the file exists

    # Send a GET request to the URL
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad responses

        # Open the file in binary write mode and write the content
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive new chunks
                    file.write(chunk)

        print(f"File '{file_name}' downloaded successfully.")

    except requests.exceptions.HTTPError as http_err:
        #print(f"HTTP error occurred: {http_err}")
        if "/p/" in url:
            url = url.replace("/p/", "/parts/")
        elif "/official/" in url:
            url = url.replace("/official/", "/unofficial/")
        else:
            wrong_parts.append(file_name)
            return -1
        download_file(url, save_directory, file_name)
    except Exception as err:
        #print(f"An error occurred: {err}")
        pass

def get_dat_files(name):
    """
    Downloads the .dat file for a given part name.
    """
    name_new = name.replace('()', '/')
    url = url_base + name_new

    # Ensure the save directory exists
    os.makedirs(save_directory, exist_ok=True)

    # Download the file
    download_file(url, save_directory, name)


def get_missing_parts(missing_parts):
    """
    Download missing parts from the list of missing parts.
    """
    print("Will download missing parts now.")
    # Use multithreading to download missing parts concurrently
    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(get_dat_files, missing_parts)

def get_dat_part(name):
    """
    Downloads the part file from the LDraw parts library.
    """
    url = url_base_part + name

    # Ensure the save directory exists
    os.makedirs(save_directory, exist_ok=True)

    # Download the file
    download_file(url, save_directory, name)