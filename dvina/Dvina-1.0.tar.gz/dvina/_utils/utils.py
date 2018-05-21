import numpy as np
import scipy as sci
from collections import defaultdict


def get_fields_as_arrays(examples, fields):
    """
    Gets examples from the set as a numpy matrix. Also gets indices of the examples in the overall set
    Parameters
    ----------
    examples
        list of examples, where every example is a dictionary or an Example which should contain provided fields
    fields
        list of field names to extract
    Returns
    -------
        dictionary of field_name->numpy/scipy array of the field values
    """

    def has_field(example, field_name):
        if isinstance(example, dict):
            return field_name in example
        else:
            return hasattr(example, field_name)

    def get_field(example, field_name):
        if isinstance(example, dict):
            return example[field_name]
        else:
            return getattr(example, field_name)

    ret = defaultdict(list)

    for example in examples:
        for field_name in fields:
            if has_field(example, field_name):
                ret[field_name].append(get_field(example, field_name))
            else:
                raise KeyError("Attribute '{0}' is not in example {1}".format(field_name, example))

    for field_name in fields:
        if len(ret[field_name]) > 0:
            for x in ret[field_name]:
                if not isinstance(x, type(ret[field_name][0])):
                    raise TypeError("Inconsistent type for field '{0}': expected {1} received {2}".
                                    format(field_name, type(ret[field_name][0]), type(x)))
            if np.isscalar(ret[field_name][0]):
                ret[field_name] = np.array(ret[field_name])
            elif isinstance(ret[field_name][0], np.ndarray):
                ret[field_name] = np.vstack(ret[field_name])
            elif isinstance(ret[field_name][0], sci.sparse.csr_matrix):
                ret[field_name] = sci.sparse.vstack(ret[field_name])
            else:
                raise TypeError("Type '{0}' isn't supported".format(type(ret[field_name][0])))
        else:
            ret[field_name] = np.array([])
    return ret


def smooth_probabilities(prob, eps):
    """
    Smooth probabilities to make sure they are not exactly 1 or 0
    Parameters
    ----------
    prob
        array or matrix of probabilities
    eps
        smoothing factor
    Returns
    -------
        Array or matrix of smoothed probabilities
    """
    if len(prob.shape) == 1:
        n = prob.size
    else:
        n = prob.shape[1]
    prob = prob * (1.0 - eps / n) + eps / (2 * n)
    return prob


def normalize_scores(scores, norm='linf'):
    """
    Normalizes scores to be positive and have unit norm
    Parameters
    ----------
    norm
    scores: array or matrix of scores
    Returns
    -------
        array of normalized scores
    """
    is_matrix = True
    if scores.ndim == 1:
        scores = scores[np.newaxis, :]
        is_matrix = False
    scores -= np.min(scores, axis=1, keepdims=True)
    if norm == 'linf':
        # if the scores are all the same, get one to be different
        scores[np.max(scores, axis=1) == 0, 0] = 1
        scores /= np.max(scores, axis=1, keepdims=True)
    elif norm == 'l1':
        # if the scores are all the same, get one to be different
        scores[np.sum(scores, axis=1) == 0, 0] = 1
        scores /= np.sum(scores, axis=1, keepdims=True)
    else:
        raise ValueError("Can't handle norm {0}".format(norm))
    if not is_matrix:
        scores = scores[0]

    return scores


def clean_multilabels(labels):
    """
    Cleans labels such that only classes which have examples in them, and not in them, are being used. 
    This is useful for multilabel datasets
    Parameters
    ----------
    labels : numpy.ndarray
        array of labels, number of classes on horizontal axis and number of examples on the vertical on
    Returns
    -------
    labels: labels array, without the columns which do not have any examples
    is_good: binary array, indicating for every column if there are examples from that class and not from that class
    """
    is_good = ~((np.sum(labels, axis=0) == 0) | (np.sum(labels, axis=0) == labels.shape[0]))
    is_good = np.ndarray.flatten(np.array(is_good))
    return labels[:, is_good], is_good
