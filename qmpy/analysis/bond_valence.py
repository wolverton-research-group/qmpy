#!/usr/bin/env python
"""
Implementation of the Bond-Valence Sum method.

Data sourced from: 
    http://www.iucr.org/resources/data/datasets/bond-valence-parameters
"""

import numpy as np
import logging

import qmpy

logger = logging.getLogger(__name__)

def get_params(elt1, elt2):
    raise NotImplementedError

def v_ij(atom1, atom2, params=None):
    if params is None:
        params = get_params(atom1.element_id, atom2.element_id)
    if params is None:
        return None
    R = atom1.structure.get_distance(atom1, atom2)
    R0 = params['param_r0']
    B = params['param_B']
    return np.exp( (R0 - R)/B )

def valence_sum(atom):
    valence = 0
    structure = atom.structure
    for atomp in atom.neighbors:
        v = v_ij(atom, atomp)
        if v is None:
            continue
        valence += v
    return valence

def total_valence_sum(structure):
    structure.find_nearest_neighbors()
    for atom in structure.atoms:
        atom.charge = valence_sum(atom)
