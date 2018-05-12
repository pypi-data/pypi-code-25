"""
Definition of the base classes

- ProbabilityDistribution
- MultivariateProbabilityDistribution

"""
import numpy as np


class ProbabilityDistribution:
    def __init__(self, **kwargs):

        for key, item in kwargs.items():
            setattr(self, key, item)

        # logical for if the pdf behaves like a numpy
        # ufunc
        self._pdf_is_vec = False


    def pdf(self, x, **kwargs):
        try:
            return self._pdf(x, **kwargs)
        except:
            # ToDo - Catch that properly 
            raise NotImplementedError


class MultivariateProbabilityDistribution(ProbabilityDistribution):
    def __init__(self, dim=1, **kwargs):
        # dimension of the embedding space
        self.dim = dim
        self.is_vectorised = False

        super(MultivariateProbabilityDistribution, self).__init__(**kwargs)


    def pdf(self, x):
        return _handle_muldim_input(x, self._pdf, self.dim, self._pdf_is_vec)
            

    def logpdf(self, x):
        if hasattr(self, '_logpdf'):
            return _handle_muldim_input(x, self._logpdf, self.dim, self._pdf_is_vec)
        else:
            return np.log(self.pdf(x))


def _handle_muldim_input(x, func, dim, is_ufunc=False):

    if isinstance(x, np.ndarray):
        assert(x.shape[1] == dim)

        if is_ufunc:
            return func(x)

        else:
            return np.array([func(_x) for _x in x])
    
    elif isinstance(x, float):
        if dim == 1:
            return func(x)
        else:
            msg = "scalar input does not agree with dimension {}".format(dim)
            raise ValueError(msg)

    elif isinstance(x, list):
            # Rather than checking just try it and see if
            # if works
            #if len(x) != self.dim:
            #    raise ValueError
            #else:
            #    print("All good")        
            try:
                return func(x)
            except:
                raise ValueError
