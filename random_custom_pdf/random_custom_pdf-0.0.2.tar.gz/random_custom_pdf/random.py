# -*- coding: utf-8 -*-
import numpy as np
from scipy.interpolate import interp1d
from scipy.integrate import trapz

def rand_custom(x: np.ndarray, y: np.ndarray, 
                shape: tuple=(1,), interp_type: str='linear') -> np.ndarray :
    """
      Generate random numbers with custom probability density function.
      To generate the sample, the truncation method is used.
      
      @x - x values vector.
      @y - y values vector.
      @shape - Output vector shape.
      @interp_type - Interpolation type. See scipy.interpolate.interp1d.
      @return - Random numbers with given shape.
      
    """
    
    assert (y >= 0).any(), "y shouldn't contain negative numbers"
    
    size = 1
    for n in shape:
        size *= n
    
    y_norm = y/y.max()
    func = interp1d(x, y_norm, kind=interp_type)
    integr_ratio = (x.max() - x.min())/trapz(y_norm, x)
    
    full = np.array([])
    
    while full.shape[0] < size:
        size_all = int(np.round(integr_ratio*(size - full.shape[0])))
        
        a = np.random.uniform(size=size_all)
        b = np.random.uniform(x.min(), x.max(), size=size_all)
    
        full = np.hstack([full, b[np.where(a < func(b))[0]]])
    
    return full[:size].reshape(shape).copy()
