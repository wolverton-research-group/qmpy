# qmpy/analysis/interface_finder.py

import numpy as np
import numpy.linalg as la
import itertools

__all__ = ['InterfaceFinder']

class InterfaceFinder(object):
    """
    Tool for finding interfaces between two arbitrary crystal structures.

    Takes no consideration of the contained atoms or translations ON the
    surface -- only looks at the lattice and identifies low-strain planes.

    Arguments:
        A and B are Structures

    Keyword Arguments:
        max_dist:
            The longest allowed lattice vector in the plane of the interface.

        max_strain:
            Strain is calculated from the e_xx, e_yy and y_xy components of
            strain, and if the _total_ strain is less than "max_strain", an
            interface is considered acceptable.

    Examples::

        >>> s1 = io.read(INSTALL_PATH+'/io/files/POSCAR_FCC')
        >>> s2 = io.read(INSTALL_PATH+'/io/files/POSCAR_BCC')
        >>> finder = InterfaceFinder(s1, s2)
        >>> finder.interfaces[0]

    """
    def __init__(self, A, B, 
            max_dist=10, max_strain=0.1, **kwargs):
        assert isinstance(A, Structure)
        assert isinstance(B, Structure)
        self._A = A.make_primitive(in_place=False)
        self._B = B.make_primitive(in_place=False)
        self.tol = max_strain_energy

        self._lp_A = self._A.find_lattice_points_within_distance(max_dist)
        self._lp_B = self._B.find_lattice_points_within_distance(max_dist)
        self.find_interfaces()

    @property
    def surf_B(self):
        saved = []
        for element in itertools.combinations(self._lp_B, r=2):
            if all([ e == 0 for e in element[0]]):
                continue
            if all([ e == 0 for e in element[1]]):
                continue
            v1 = np.dot(self._B.cell, element[0])
            v2 = np.dot(self._B.cell, element[1])
            element = Surface(v1, v2)
            yield element
            saved.append(element)
        #while saved:
        #    for element in saved:
        #        yield element

    @property
    def surf_A(self):
        saved = []
        for element in itertools.combinations(self._lp_A, r=2):
            if all([ e == 0 for e in element[0]]):
                continue
            if all([ e == 0 for e in element[1]]):
                continue
            v1 = np.dot(self._A.cell, element[0])
            v2 = np.dot(self._A.cell, element[1])
            element = Surface(v1, v2)
            yield element
            saved.append(element)
        #while saved:
        #    for element in saved:
        #        yield element

    def find_interfaces(self):
        acceptable = []
        for sa, sb in itertools.product(self.surf_A, self.surf_B):
            e = sa*sb
            if e < self.tol:
                acceptable.append((sa, sb, e))
        self.interfaces = sorted(acceptable, key=lambda x: x[2])

class Surface:
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2
        self.a = la.norm(v1)
        self.b = la.norm(v2)
        self.alpha = np.arcsin(np.dot(v1,v2)/(self.a*self.b))
        self.area = self.v1.dot(self.v2)

    def __mul__(self, other):
        e1 = 2*(self.a - other.a)/(self.a + other.a)
        e2 = 2*(self.b - other.b)/(self.b + other.b)
        g = (self.b - other.b)/(self.b + other.b) 
        return abs(e1) + abs(e2) + abs(g)

