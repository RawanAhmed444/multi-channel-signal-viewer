import numpy as np

def calculate_statistics(data):
    if data is None or len(data) == 0:
        return {'mean': 0, 'std': 0, 'min': 0, 'max': 0, 'duration': 0}
    stats = {
        'mean': np.mean(data),
        'std': np.std(data),
        'min': np.min(data),
        'max': np.max(data),
        'duration': len(data)
    }
    return stats
