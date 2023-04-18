
import numpy as np
from scipy.special import logsumexp

def init_particles(N=100, d=2, x_min=-1.0, x_max = 1.0, delta=1.0, method="uniform"):
    r"""Initialize particles
    
    Parameters
    ----------
    N : int, optional
        Number of particles. The default is 100.
    d : int, optional
        Dimension of the particles. The default is 2.
    x_min : float, optional
        Lower bound for the uniform distribution. The default is 0.0.
    x_max : float, optional
        Upper bound for the uniform distribution. The default is 1.0.
    delta : float, optional
        Standard deviation for the normal distribution. The default is 1.0.
    method : str, optional
        Method for initializing the particles. The default is "uniform".
        Possible values: "uniform", "normal"
    
    Returns
    -------
    x : numpy.ndarray
        Array of particles of shape (N, d)
    """

    if method == "uniform":
        x = np.random.uniform(x_min, x_max, (N, d))
    elif method == "normal":
        x = np.random.multivariate_normal(np.array([0,0]),delta*np.eye(d),(N,))
    else:
        raise Exception('Unknown method for init_particles specified!')
        
    return x
        

class config:
    r"""Configuration class
    """
    def __init__(self, **entries):
        self.__dict__.update(entries)
        

        