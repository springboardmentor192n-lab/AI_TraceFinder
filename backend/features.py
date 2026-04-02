import numpy as np

def extract(residual):

    mean = np.mean(residual)
    std = np.std(residual)

    return [mean,std]