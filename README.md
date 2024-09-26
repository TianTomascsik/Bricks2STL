# Bricks2STL - Bricks to STL

## Purpose

You can use this tool to convert a interlocking Bricks into 3D printable STL file.

## Run

Dependencies:

first install the following dependencies:

```bash
pip install numpy numpy-stl requests pandas
```
This programm is designed to parse a whole set of interlocking bricks and convert them into a 3D printable STL file.
The input file should be a CSV file. The CSV file can be found for example on the website: https://rebrickable.com/sets/. 
When you found a set you like klick on "Inventory" and then "Export parts" download the Rebrickable CSV file and use it as input file.

Example: 
```bash
python ./src/Bricks2STL.py input_file_path name_of_output_directory
```

Hint: The programm is designed to use 8 threads. If you want to use less threads you can change the number of threads in the programm.
The CSV file is also not allways perfect. Sometimes the CSV file contains wrong information. In this case you have to correct the CSV file manually.
The generated STL file sometimes contains errors. You can use the programm "MeshLab" or your slicer to fix the errors.
