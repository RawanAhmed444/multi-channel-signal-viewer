import csv
import numpy as np

def load_signal_from_file(filename):
    signal_data = []
    with open(filename, "r") as file:
        csvreader = csv.reader(file)
        header = next(csvreader)  # Skip the header row
        for row in csvreader:
            signal_data.append([row[0], row[1]])  # Extract only the first two columns
    return np.array(signal_data)


