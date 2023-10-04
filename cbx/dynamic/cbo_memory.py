import numpy as np
from typing import Union
from scipy.special import logsumexp

from .cbo import CBO

#%% CBO_Memory
class CBOMemory(CBO):
    r"""Consensus-based optimization with memory effects (CBOMemory) class

    This class implements the CBO algorithm with memory effects as described in [1,2]_. The algorithm
    is a particle dynamic algorithm that is used to minimize the objective function :math:`f(x)`.

    Parameters
    ----------
    x : array_like, shape (J, d)
        The initial positions of the particles. For a system of :math:`J` particles, the i-th row of this array ``x[i,:]``
        represents the position :math:`x_i` of the i-th particle.
    y : array_like, shape (J, d)
        The initial positions of the particles. For a system of :math:`J` particles, the i-th row of this array ``y[i,:]``
        represents the or an approximation of the historical best position :math:`y_i` of the i-th particle.
    f : obejective
        The objective function :math:`f(x)` of the system.
    alpha : float, optional
        The heat parameter :math:`\alpha` of the system. The default is 1.0.
    noise : noise_model, optional
        The noise model that is used to compute the noise vector. The default is ``normal_noise(dt=0.1)``.
    dt : float, optional
        The parameter :math:`dt` of the noise model. The default is 0.1.
    sigma : float, optional
        The parameter :math:`\sigma` of the noise model. The default is 1.0.
    lamda : float, optional
        The decay parameter :math:`\lambda` of the noise model. The default is 1.0.
    sigma_memory : float, optional
        The parameter :math:`\sigma_{\text{memory}}` of the noise model. The default is 1.0.
    lamda_memory : float, optional
        The decay parameter :math:`\lambda_{\text{memory}}` of the noise model. The default is 1.0.
    
    References
    ----------
    .. [1] Grassi, S. & Pareschi, L. (2021). From particle swarm optimization to consensus based optimization: stochastic modeling and mean-field limit.
        Math. Models Methods Appl. Sci., 31(8):1625–1657.
    .. [2] Riedl, K. (2023). Leveraging memory effects and gradient information in consensus-based optimization: On global convergence in mean-field law.
        Eur. J. Appl. Math., XX (X), XX-XX.

    """

    def __init__(self,
                 f, 
                 #beta: float = float('inf'),
                 lamda_memory: float = 0.4,
                 sigma_memory: Union[float, None] = None,
                 **kwargs) -> None:
        
        super(CBOMemory, self).__init__(f, **kwargs)
        
        self.y = self.copy_particles(self.x)
        
        #self.beta = beta
        self.lamda_memory = lamda_memory
        
        if sigma_memory is None:
            self.sigma_memory = self.lamda_memory * self.sigma
        else:
            self.sigma_memory = self.sigma_memory
            
        self.energy = self.f(self.x)
        
    
    def step(self,) -> None:
        r"""Performs one step of the CBO algorithm.

        Parameters
        ----------
        None

        Returns
        -------
        None
        
        """
        self.set_batch_idx()
        self.x_old = self.copy_particles(self.x) # save old positions
        self.y_old = self.copy_particles(self.y) # save old positions
        #x_batch = self.x[self.M_idx, self.batch_idx, :] # get batch
        
        
        mind = self.get_mean_ind()
        ind = self.get_ind()#
        # first update
        self.m_alpha = self.compute_mean(self.y[mind], self.energy[mind])        
        self.m_diff = self.x[ind] - self.m_alpha
        self.memory_diff = self.x[ind] - self.y[ind]
        
        # inter step
        self.s = self.sigma * self.noise(self.m_diff)
        self.s_memory = self.sigma_memory * self.noise(self.memory_diff)

        self.x[ind] = (
            self.x[ind] -
            self.lamda * self.dt * self.m_diff * self.correction(self)[ind] -
            self.lamda_memory * self.dt * self.memory_diff +
            self.s + 
            self.s_memory)
        
        energy_new = self.f(self.x[ind])            
        self.y[ind] = self.y[ind] + ((self.energy>energy_new)[:, :, np.newaxis]) * (self.x[ind] - self.y[ind])
        self.energy = np.minimum(self.energy, energy_new)
        
        self.post_step()
        
    def compute_mean(self, x_batch, energy) -> None:
        r"""Updates the weighted mean of the particles.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        self.num_f_eval += np.ones(self.M) * self.batch_size # update number of function evaluations
        
        weights = - self.alpha * energy#[e_ind]
        coeffs = np.exp(weights - logsumexp(weights, axis=(-1,), keepdims=True))[...,None]
        return (x_batch * coeffs).sum(axis=-2, keepdims=True)
        