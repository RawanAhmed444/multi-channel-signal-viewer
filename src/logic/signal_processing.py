import csv
import numpy as np
import pandas as pd

def load_signal_from_file(filename):
    signal_data = []
    with open(filename, "r") as file:
        csvreader = csv.reader(file)
        header = next(csvreader)  # Skip the header row
        for row in csvreader:
            signal_data.append([row[0], row[1]])  # Extract only the first two columns
        return np.array(signal_data)

# def convert_signal_values_to_numeric(filename):
#     signal_data = load_signal_from_file(filename)
#     df = pd.DataFrame(signal_data)

#     # Convert the columns to numeric
#     df[0] = pd.to_numeric(df[0], errors='coerce')
#     df[1] = pd.to_numeric(df[1], errors='coerce')

#     # Extract the converted data
#     x = df[0].values
#     y = df[1].values
    
#     return x, y
    
