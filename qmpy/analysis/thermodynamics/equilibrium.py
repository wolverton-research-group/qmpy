import numpy as np
import logging

import qmpy
import phase

logger = logging.getLogger(__name__)

class Equilibrium:
    def __init__(self, phases, **kwargs):
        self.phases = list(phases)

    def __getitem__(self, index):
        return self.phases[index]

    def __contains__(self, other):
        if isinstance(other, phase.Phase):
            return ( other in self.phases )
        if isinstance(other, list):
            return (set(other) <= set(self.phases))
        if isinstance(other, Equilibrium):
            return (other.phases <= self.phases)
        if isinstance(other, dict):
            return (set(other.keys()) <= set(self.phases))

    def __str__(self):
        return '-'.join([p.name for p in self.phases ])

    def __repr__(self):
        return '<Equilibrium: %s>' % self

    @property
    def elements(self):
        return sorted(set.union(*[p.space for p in self.phases]))

    @property
    def composition_matrix(self):
        mat = [ [ p.unit_comp.get(k,0) for k in self.elements ]
                                       for p in self.phases ]
        return np.array(mat)

    @property
    def energy_array(self):
        arr = [ p.energy for p in self.phases ]
        return np.array(arr)

    _chem_pots = None
    @property
    def chemical_potentials(self):
        if self._chem_pots:
            return self._chem_pots
        A = self.composition_matrix
        b = self.energy_array
        dmus = np.linalg.lstsq(A, b)
        self._chem_pots = dict(zip(self.elements, dmus[0]))
        return self._chem_pots

    @property
    def chem_pots(self):
        return self.chemical_potentials

    def adjacency(self, other):
        common = len(set(self.phases) & set(other.phases))
        return len(self.phases) - common

    @property
    def chem_pot_coord(self):
        return np.array([ self.chem_pots[k] for k in self.elements ])

    @property
    def label(self):
        return '-'.join([ p.name for p in self.phases ])
