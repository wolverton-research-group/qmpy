#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Interface to ASE Atoms, and Calculators.
"""
import logging

import qmpy
from qmpy.materials.structure import Structure
from qmpy.materials.atom import Atom

logger = logging.getLogger(__name__)

if qmpy.FOUND_ASE:
    import ase
    import ase.io

def structure_to_atoms(structure):
    """
    Convert a qmpy.Structure to an ase.Atoms

    Example::

        >>> import qmpy.io as io
        >>> structure = io.read('POSCAR')
        >>> atoms = io.ase_mapper.structure_to_atoms(structure)

    """
    if not qmpy.FOUND_ASE:
        print 'ASE must be installed to convert a Structure to an Atoms object'
        return
    atoms = ase.Atoms(
            structure.name,
            cell=structure.cell,
            scaled_positions=structure.coords, 
            magmoms=structure.magmoms)
    return atoms

def atoms_to_structure(atoms):
    """
    Convert a qmpy.Structure to an ase.Atoms

    Example::

        >>> import qmpy.io.ase_mapper
        >>> atoms = ase.io.read('POSCAR')
        >>> structure = qmpy.io.ase_mapper.atoms_to_structure(atoms)

    """
    if not qmpy.FOUND_ASE:
        print 'ASE must be installed to convert Atoms object to a Structure'
        return
    struct = Structure()
    struct.cell = atoms.get_cell()
    for a in atoms: 
        atom = Atom()
        atom.symbol = a.symbol
        atom.coord = a.position
        atom.magmom = a.magmom
        atom.direct = False
        struct.add_atom(atom)
    return struct

def read(filename, **kwargs):
    """
    Uses the ase.io.read method to read in a file, and convert it to a
    qmpy.Structure object. Passes any optional keyword arguments to the
    ase.io.read call.

    """
    if not qmpy.FOUND_ASE:
        print 'ASE must be installed to convert Atoms object to a Structure'
        return

    atoms = ase.io.read(filename, **kwargs)
    return atoms_to_structure(atoms)

def write(structure, **kwargs):
    atoms = structure_to_atoms(structure)
    return ase.io.write(atoms, **kwargs)
