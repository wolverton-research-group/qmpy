import numpy as np
import numpy.linalg as linalg
import itertools
from collections import defaultdict
import logging

import qmpy
from qmpy.utils import *

logger = logging.getLogger(__name__)

class PDF(object):
    """
    Container class for a Pair-distribution function.

    Attributes:
        structure: :mod:`~qmpy.Structure`
        pairs: dict of (atom1, atom2):[distances]
        limit: maximum distance
    """

    def __init__(self, structure, limit=10):
        elements = structure.comp.keys()
        pairs = itertools.combinations_with_replacement(elements, r=2)
        self.pairs = [ self.get_pair(pair) for pair in pairs ]
        self.distances = dict((p, []) for p in self.pairs)
        self.weights = dict((p, []) for p in self.pairs)

        structure = structure.copy()
        structure.reduce()
        structure.symmetrize()
        self.structure = structure
        self.cell = self.structure.cell
        self.uniq = self.structure.uniq_sites
        self.sites = self.structure.sites
        self.limit = limit
        self.limit2 = limit**2
        lp = structure.find_lattice_points_within_distance(limit)
        self.lattice_points = np.array([ np.dot(p, self.cell) for p in lp ])

    def get_pair(self, pair):
        return tuple(sorted(pair))

    def get_pair_distances(self):
        """
        Loops over pairs of atoms that are within radius max_dist of one another.
        Returns a dict of (atom1, atom2):[list of distances].

        """
        for s1 in self.uniq:
            for s2 in self.sites:
                _dist = s1.cart_coord - s2.cart_coord
                for lp in self.lattice_points:
                    dist = _dist + lp
                    if any([ abs(p) > self.limit for p in dist ]):
                        continue
                    dist2 = np.dot(dist, dist)
                    if dist2 < 1e-6:
                        continue
                    if dist2 > self.limit2:
                        continue
                    distance = dist2**0.5

                    for a1, a2 in itertools.product(s1, s2):
                        pair = self.get_pair([a1.element_id, a2.element_id])
                        w = s1.multiplicity*a1.occupancy*a2.occupancy
                        self.distances[pair].append(float(distance))
                        self.weights[pair].append(float(w))

    def plot(self, smearing=0.1):
        renderer = Renderer()
        N = len(self.structure)
        V = self.structure.get_volume()
        xs = np.mgrid[0.5:self.limit:1000j]
        dr = xs[1] - xs[0]
        norms = [ ( (x+dr/2)**3 - (x-dr/2)**3) for x in xs ]
        for pair in self.pairs:
            e1, e2 = pair
            vals = np.zeros(xs.shape)
            nanb = self.structure.comp[e1]*self.structure.comp[e2]
            prefactor = 1.0/(smearing*np.sqrt(2*np.pi))
            #prefactor = V**2 * (N-1)/N
            for w, d in zip(self.weights[pair], self.distances[pair]):
                if not d:
                    continue
                vals += np.exp(-(d-xs)**2/(2*smearing**2))*w
            vals = prefactor*vals/norms
            vals = [ v if v > 1e-4 else 0.0 for v in vals ]
            line = Line(zip(xs, vals), label='%s-%s' % (e1, e2))
            renderer.add(line)

        renderer.xaxis.label = 'interatomic distance [&#8491;]'
        return renderer
