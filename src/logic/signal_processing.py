import csv
import numpy as np
import pandas as pd

def load_signal_from_file(filename, col1, col2):
    """Loads data from a CSV file into a NumPy array.

    Args:
        filename: The name of the CSV file to load.

    Returns:
        A NumPy array containing the loaded data.
    """
    # Create an empty list to store the data
    signal_data = []  
    with open(filename, "r") as file: 
        csvreader = csv.reader(file)  
        for row in csvreader:  
            # Extract only the first two columns
            signal_data.append([row[col1], row[col2]])
    # Convert the data to a NumPy array
    return np.array(signal_data)  
    
def convert_signal_values_to_numeric(filename, col1, col2):
    """Converts the values in the loaded data to numeric format.

    Args:
        filename: The name of the CSV file containing the data.

    Returns:
        A tuple containing the x and y values as NumPy arrays.
    """

    signal_data = load_signal_from_file(filename, col1, col2)  
    # Create a pandas DataFrame from the data
    df = pd.DataFrame(signal_data)  
    
    # Convert the columns to numeric, handling potential errors
    df[0] = pd.to_numeric(df[0], errors='coerce')
    df[1] = pd.to_numeric(df[1], errors='coerce')

    # Extract the converted data as NumPy arrays
    x = df[0].values
    y = df[1].values

    return x, y

def cartesian_to_polar(filename, col1, col2):
    """Converts rectangular coordinates to polar coordinates.

    Args:
        filename: The name of the CSV file containing the data.

    Returns:
        A tuple containing the r-coordinate and θ-coordinate as NumPy arrays.
    """

    x, y = convert_signal_values_to_numeric(filename, col1, col2)  

    # Use NumPy's element-wise operations to calculate r and theta
    r = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y, x)

    return r, theta

