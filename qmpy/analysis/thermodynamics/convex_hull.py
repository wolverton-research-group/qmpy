# qmpy/analysis/thermodynamics/convex_hull.pyx

import numpy as np
#cimport numpy as np
#DTYPE = np.float64
#ctypedef np.float64_t DTYPE_t

import numpy.linalg as la
import itertools
import random
import logging

logger = logging.getLogger(__name__)

class Simplex(object):
    """
    A Simplex is a geometric object with N vertices in N dimensions.
    """

    def __init__(self, phases):
        space = set.union(*[p.space for p in phases ])
        cc = [ [p.unit_comp[e] for e in self.space ] for p in phases ]

        self.space = space
        self.comps = np.array(cc)
        self.energies = np.array([ p.energy for p in phases ])

        self.bounds = np.array(range(len(space)))
        self.ref_energies = np.array([ self.energies[i] for i in self.bounds ])
        self.ref_comps = np.array([ self.comps[i] for i in self.bounds ])

        self.find_bounds()

    def contains(self, comp):
        """
        Put the point in barycentric coordinates and check that it is in the
        simplex.
        """
        coord = self.bcc(comp)
        return (all([ a >= 0 for a in coord ]) and sum(coord) <= 1)

    def bcc(self, point):
        r = point - self.comps[self.bounds[0]]
        return np.dot(self.inv, r)

    def get_relative_energy(self, ind):
        return self.energies[ind] - self.comps[ind].dot(
                                           self.ref_energies[ind])
