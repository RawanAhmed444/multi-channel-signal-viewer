from logic.signal_processing import load_signal_from_file

# Example usage
filename = "src\data\signals\EEG_Normal.csv"
signal_data = load_signal_from_file(filename)
print(signal_data)

