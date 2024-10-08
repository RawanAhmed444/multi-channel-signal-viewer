import numpy as np

def calculate_statistics(data):
    stats = {
        'mean': np.mean(data),
        'std': np.std(data),
        'min': np.min(data),
        'max': np.max(data),
        'duration': len(data)
    }
    return stats
