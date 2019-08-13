#cython: language_level=3

import numpy as np
cimport numpy as np

cimport cython

DTYPE = np.uint8
ALPHALDTYPE = np.float64
ctypedef np.uint8_t DTYPE_t
ctypedef np.float64_t ALPHADTYPE_t

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cdef np.ndarray[ALPHADTYPE_t, ndim=3] add_to_frame(np.ndarray[DTYPE_t, ndim=3] background, np.ndarray[DTYPE_t, ndim=3] image, np.ndarray[ALPHADTYPE_t, ndim=2] alpha_l, int channel):

    cdef unsigned int rows = background.shape[0]
    cdef unsigned int cols = background.shape[1]
    cdef np.ndarray[ALPHADTYPE_t, ndim=3] out = np.zeros((rows, cols, channel))

    for color in range(0, channel):
        for col in range(0, cols):
            for row in range(0, rows):
                out[row, col, color] = image[row, col, color] + background[row, col, color] * alpha_l[row, col]

    return out

