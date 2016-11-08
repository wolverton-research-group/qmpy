import numpy as np

import qmpy
from qmpy.utils import *
import symmetry.routines as routines

import logging

logger = logging.getLogger(__name__)

"""
Module to determine the necessary distortions for describing the full elastic
tensor for an arbitrary input Structure.

To do: need to convert the symmetry operations of a structure from the lattice
basis to cartesian.
"""

vectors = [[0.1, 0.0, 0.0],
           [0.0, 0.1, 0.0],
           [0.0, 0.0, 0.1],
           [0.1, 0.1, 0.0],
           [0.1, 0.0, 0.1],
           [0.0, 0.1, 0.1]]

def get_unique_transforms(structure):
    uniq_transforms = []

    structure.symmetrize()
    for mod in np.array(vectors):
        found = False
        mod = mod + 1
        cell = structure.cell * mod
        print 'right'
        print cell
        print 'tests:'
        for trans, cell2 in uniq_transforms:
            for rotation in structure.rotations:
                test = rotation.dot(cell2)
                if np.allclose(cell, test):
                    found = True
                    print test
                    print 'FOUND'
                    break
            if found:
                break

        if not found:
            uniq_transforms.append([mod, cell])

    return uniq_transforms
