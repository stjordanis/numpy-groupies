import numpy as np

from .utils_numpy import minimum_dtype, minimum_dtype_scalar, check_boolean, get_func, aliasing
from .aggregate_numpy import aggregate as aggregate_np


def _anynan(group_idx, a, size, fill_value, dtype=None):
    return _any(group_idx, np.isnan(a), size, fill_value=fill_value, dtype=dtype)

def _allnan(group_idx, a, size, fill_value, dtype=None):
    return _all(group_idx, np.isnan(a), size, fill_value=fill_value, dtype=dtype)

def _any(group_idx, a, size, fill_value, dtype=None):
    check_boolean(fill_value)
    ret = np.full(size, fill_value, dtype=bool)
    if fill_value:
        ret[group_idx] = False  # any-test should start from False
    np.logical_or.at(ret, group_idx, a)
    return ret

def _all(group_idx, a, size, fill_value, dtype=None):
    check_boolean(fill_value)
    ret = np.full(size, fill_value, dtype=bool)
    if not fill_value:
        ret[group_idx] = True  # all-test should start from True
    np.logical_and.at(ret, group_idx, a)
    return ret

def _sum(group_idx, a, size, fill_value, dtype=None):
    dtype = minimum_dtype_scalar(fill_value, dtype, a)
    ret = np.full(size, fill_value, dtype=dtype)
    if fill_value != 0:
        ret[group_idx] = 0  # sums should start at 0
    np.add.at(ret, group_idx, a)
    return ret

def _prod(group_idx, a, size, fill_value, dtype=None):
    """Same as accumarray_numpy.py"""
    dtype = minimum_dtype_scalar(fill_value, dtype, a)
    ret = np.full(size, fill_value, dtype=dtype)
    if fill_value != 1:
        ret[group_idx] = 1  # product should start from 1
    np.multiply.at(ret, group_idx, a)
    return ret

def _min(group_idx, a, size, fill_value, dtype=None):
    """Same as accumarray_numpy.py"""
    dtype = minimum_dtype(fill_value, dtype or a.dtype)
    dmax = np.iinfo(a.dtype).max if issubclass(a.dtype.type, np.integer) else np.finfo(a.dtype).max
    ret = np.full(size, fill_value, dtype=dtype)
    if fill_value != dmax:
        ret[group_idx] = dmax  # min starts from maximum
    np.minimum.at(ret, group_idx, a)
    return ret

def _max(group_idx, a, size, fill_value, dtype=None):
    """Same as accumarray_numpy.py"""
    dtype = minimum_dtype(fill_value, dtype or a.dtype)
    dmin = np.iinfo(a.dtype).min if issubclass(a.dtype.type, np.integer) else np.finfo(a.dtype).min
    ret = np.full(size, fill_value, dtype=dtype)
    if fill_value != dmin:
        ret[group_idx] = dmin  # max starts from minimum
    np.maximum.at(ret, group_idx, a)
    return ret


_impl_dict = dict(min=_min, max=_max, sum=_sum, prod=_prod, all=_all, any=_any,
                  allnan=_allnan, anynan=_anynan)


def aggregate(group_idx, a, func='sum', **kwargs):
    """
    Aggregation similar to Matlab's `accumarray` function.
    
    See readme file at https://github.com/ml31415/accumarray for 
    full description.  Or see ``accumarray`` in ``accumarray_numpy.py``.

    Unlike the ``accumarray_numpy.py``, which in most cases does some custom 
    optimisations, this version simply uses ``numpy``'s ``ufunc.at``. 
    
    As of version 1.9 this gives fairly poor performance.

    Note that this implementation piggybacks on the main error checking and
    argument parsing etc. in ``accumarray_numpy.py``.
    """
    func = get_func(func, aliasing, _impl_dict)
    if not isinstance(func, basestring):
        raise NotImplementedError("No such ufunc available")
    return aggregate_np(group_idx, a, func=func, _impl_dict=_impl_dict, _nansqueeze=False, **kwargs)

