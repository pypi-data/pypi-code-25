#!/usr/bin/env python

# libraries
import warnings
import numpy as np
import six
from sklearn.decomposition import PCA, FastICA, IncrementalPCA, KernelPCA, FactorAnalysis, TruncatedSVD, SparsePCA, MiniBatchSparsePCA, DictionaryLearning, MiniBatchDictionaryLearning
from sklearn.manifold import TSNE, MDS, SpectralEmbedding, LocallyLinearEmbedding, Isomap
from umap import UMAP
from ..tools.df2mat import df2mat
from .._shared.helpers import *
from .normalize import normalize as normalizer
from .align import align as aligner
from .format_data import format_data as formatter

# dictionary of models
models = {
    'PCA' : PCA,
    'IncrementalPCA' : IncrementalPCA,
    'SparsePCA' : SparsePCA,
    'MiniBatchSparsePCA' : MiniBatchSparsePCA,
    'KernelPCA' : KernelPCA,
    'FastICA' : FastICA,
    'FactorAnalysis' : FactorAnalysis,
    'TruncatedSVD' : TruncatedSVD,
    'DictionaryLearning' : DictionaryLearning,
    'MiniBatchDictionaryLearning' : MiniBatchDictionaryLearning,
    'TSNE' : TSNE,
    'Isomap' : Isomap,
    'SpectralEmbedding' : SpectralEmbedding,
    'LocallyLinearEmbedding' : LocallyLinearEmbedding,
    'MDS' : MDS,
    'UMAP' : UMAP
}

# main function
@memoize
def reduce(x, reduce='IncrementalPCA', ndims=None, normalize=None, align=None,
           model=None, model_params=None, internal=False, format_data=True):
    """
    Reduces dimensionality of an array, or list of arrays

    Parameters
    ----------
    x : Numpy array or list of arrays
        Dimensionality reduction using PCA is performed on this array.

    reduce : str or dict
        Decomposition/manifold learning model to use.  Models supported: PCA,
        IncrementalPCA, SparsePCA, MiniBatchSparsePCA, KernelPCA, FastICA,
        FactorAnalysis, TruncatedSVD, DictionaryLearning, MiniBatchDictionaryLearning,
        TSNE, Isomap, SpectralEmbedding, LocallyLinearEmbedding, MDS and UMAP.
        Can be passed as a string, but for finer control of the model
        parameters, pass as a dictionary, e.g. reduce={'model' : 'PCA',
        'params' : {'whiten' : True}}. See scikit-learn specific model docs
        for details on parameters supported for each model.

    ndims : int
        Number of dimensions to reduce

    format_data : bool
        Whether or not to first call the format_data function (default: True).

    model : None
        Deprecated argument.  Please use reduce.

    model_params : None
        Deprecated argument.  Please use reduce.

    align : None
        Deprecated argument.  Please use new analyze function to perform
        combinations of transformations

    normalize : None
        Deprecated argument.  Please use new analyze function to perform
        combinations of transformations

    Returns
    ----------
    x_reduced : Numpy array or list of arrays
        The reduced data with ndims dimensionality is returned.  If the input
        is a list, a list is returned.

    """

    # deprecated warning
    if (model is not None) or (model_params is not None):
        warnings.warn('Model and model params will be deprecated.  Please use the \
                      reduce keyword.  See API docs for more info: http://hypertools.readthedocs.io/en/latest/hypertools.tools.reduce.html#hypertools.tools.reduce')
        reduce = {}
        reduce['model'] = model
        reduce['params'] = model_params

    # if model is None, just return data
    if reduce is None:
        return x
    else:

        # common format
        if format_data:
            x = formatter(x, ppca=True)

        if np.vstack([i for i in x]).shape[0]==1:
            warnings.warn('Cannot reduce the dimensionality of a single row of'
                          ' data. Return zeros length of ndims')
            return [np.zeros((1, ndims))]
        if ndims:
            if np.vstack([i for i in x]).shape[0]<ndims:
                warnings.warn('The number of rows in your data is less than ndims.'
                              ' The data will be reduced to the number of rows.')

        # deprecation warnings
        if normalize is not None:
            warnings.warn('The normalize argument will be deprecated for this function.  Please use the \
                          analyze function to perform combinations of these transformations.  See API docs for more info: http://hypertools.readthedocs.io/en/latest/hypertools.analyze.html#hypertools.analyze')
            x = normalizer(x, normalize=normalize)

        if align is not None:
            warnings.warn('The align argument will be deprecated for this function.  Please use the \
                          analyze function to perform combinations of these transformations.  See API docs for more info: http://hypertools.readthedocs.io/en/latest/hypertools.analyze.html#hypertools.analyze')
            x = aligner(x, align=align)

        # if the shape of the data is already less than ndims, just return it
        if ndims is None:
            return x
        elif all([i.shape[1]<=ndims for i in x]):
            return x

        # if reduce is a string, find the corresponding model
        if type(reduce) in [str, np.string_]:
            model = models[reduce]
            model_params = {
                'n_components' : ndims
            }
        # if its a dict, use custom params
        elif type(reduce) is dict:
            if isinstance((reduce['model']), six.string_types):
                model = models[reduce['model']]
                if reduce['params'] is None:
                    model_params = {
                        'n_components' : ndims
                    }
                else:
                    model_params = reduce['params']
        if ndims:
            model_params = {
                'n_components' : ndims
            }

        # initialize model
        model = model(**model_params)

        # reduce data
        x_reduced = reduce_list(x, model)

        # return data
        if internal or len(x_reduced)>1:
            return x_reduced
        else:
            return x_reduced[0]

# sub functions
def reduce_list(x, model):
    split = np.cumsum([len(xi) for xi in x])[:-1]
    x_r = np.vsplit(model.fit_transform(np.vstack(x)), split)
    if len(x)>1:
        return [xi for xi in x_r]
    else:
        return [x_r[0]]
