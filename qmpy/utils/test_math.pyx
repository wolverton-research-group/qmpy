
import numpy as np
cimport numpy as np
DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

cpdef get_distance(np.ndarray cell, np.ndarray coord1, np.ndarray coord2):
    cdef DTYPE_t xx = np.dot(cell[0], cell[0])
    cdef DTYPE_t yy = np.dot(cell[1], cell[1])
    cdef DTYPE_t zz = np.dot(cell[2], cell[2])
    cdef np.ndarray[DTYPE_t, ndim=1] x = cell[0]
    cdef np.ndarray[DTYPE_t, ndim=1] y = cell[1]
    cdef np.ndarray[DTYPE_t, ndim=1] z = cell[2]

    cdef np.ndarray vec = coord2 - coord1
    vec -= np.round(vec)
    
    cdef np.ndarray dist = np.dot(vec, cell)

    dist -= np.round(dist.dot(x)/xx)*x
    dist -= np.round(dist.dot(y)/yy)*y
    dist -= np.round(dist.dot(z)/zz)*z

    return (dist[0]**2 + dist[1]**2 + dist[2]**2)**0.5
