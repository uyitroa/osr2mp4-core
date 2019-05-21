from numpy import ctypeslib
import numpy
from multiprocessing import sharedctypes


def to_rawarray(array):
	tmp_array = numpy.copy(array)
	size = tmp_array.size
	shape = tmp_array.shape
	tmp_array.shape = size
	raw = sharedctypes.RawArray('d', tmp_array)
	return raw


def to_array(raw, shape):
	S = ctypeslib.as_array(raw)
	S.shape = shape
