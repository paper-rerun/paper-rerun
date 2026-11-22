"""Restricted unpickler for the NANOGrav chain deposit.

The files are gzipped pickles from a download, so pickle.load is never used.
find_class allows only the three numpy names the opcode walk showed the files refer
to, and the array itself is rebuilt as a read-only view over the raw buffer so no
second multi-GB copy is made.
"""
import gzip, io, pickle
import numpy as np

ALLOWED = {
    ('numpy.core.multiarray', '_reconstruct'),
    ('numpy._core.multiarray', '_reconstruct'),
    ('numpy', 'ndarray'),
    ('numpy', 'dtype'),
}


class ArrayHolder(object):
    """Stand-in for numpy.ndarray during unpickling.

    numpy's pickle protocol calls _reconstruct(subtype, shape, b) and then
    __setstate__((version, shape, dtype, is_fortran, raw)). We keep the raw bytes and
    expose a zero-copy view, so peak memory is one copy of the data, not two.
    """

    def __init__(self):
        self.array = None
        self._raw = None

    def __setstate__(self, state):
        version, shape, dtype, is_fortran, raw = state
        if not isinstance(raw, (bytes, bytearray)):
            raise TypeError('unexpected array state payload: %r' % type(raw))
        self._raw = raw
        order = 'F' if is_fortran else 'C'
        self.array = np.frombuffer(raw, dtype=dtype).reshape(shape, order=order)


def _reconstruct(subtype, shape, b):
    if subtype is not ArrayHolder:
        raise pickle.UnpicklingError('unexpected ndarray subtype %r' % (subtype,))
    return ArrayHolder()


class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) not in ALLOWED:
            raise pickle.UnpicklingError('blocked global %s.%s' % (module, name))
        if name == '_reconstruct':
            return _reconstruct
        if name == 'ndarray':
            return ArrayHolder
        return np.dtype


def load_chain(path):
    """Return (param_dict, ndarray). The ndarray is a read-only view."""
    with gzip.open(path, 'rb') as f:
        obj = RestrictedUnpickler(f).load()
    # Most files hold a list [dict, array]; some hold a tuple instead.
    if not isinstance(obj, (list, tuple)):
        raise ValueError('top level is %r, expected list or tuple' % type(obj))
    params = None
    holder = None
    for item in obj:
        if isinstance(item, dict):
            params = item
        elif isinstance(item, ArrayHolder):
            holder = item
        elif isinstance(item, (tuple, list)):
            for sub in item:
                if isinstance(sub, dict):
                    params = sub
                elif isinstance(sub, ArrayHolder):
                    holder = sub
    if params is None or holder is None:
        raise ValueError('could not find both the param dict and the array; top level '
                         'held %r' % [type(i) for i in obj])
    return params, holder.array
