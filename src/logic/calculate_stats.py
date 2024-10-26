import numpy as np

def calculate_statistics(data):
    # Ensure that 'data' is a NumPy array
    if isinstance(data, list):
        data = np.array(data)

    return {
        'mean': np.mean(data),
        'std': np.std(data),
        'min': np.min(data),
        'max': np.max(data)
    }
