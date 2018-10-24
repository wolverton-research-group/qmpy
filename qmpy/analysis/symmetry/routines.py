import fractions as frac
import numpy as np
import logging

import qmpy
if not qmpy.FOUND_SPGLIB:
    logger.critical('Must install spglib to be able to do symmetry analysis')
import spglib

import qmpy.data as data
from qmpy.utils import *
from qmpy.materials.structure import Structure
from qmpy.materials.structure import StructureError

logger = logging.getLogger(__name__)


## wrappers for spglib functions | https://atztogo.github.io/spglib/


def __structure_to_cell(structure):
    """Convert `qmpy.Structure` objects to tuple of (lattice, positions, ...)
    required as input to all spglib functions.
    """
    if not isinstance(structure, Structure):
        raise StructureError('Input is not of type `qmpy.Structure`')
    lattice = structure.cell.copy()
    positions = structure.site_coords.copy()
    numbers = structure.species_id_types.copy()
    magmoms = structure.magmoms.copy()
    if not any(magmoms):
        return (lattice, positions, numbers)
    else:
        return (lattice, positions, numbers, magmoms)


def get_structure_symmetry(structure,
                           method='spglib',
                           symprec=1e-5,
                           angle_tolerance=-1.0):
    """
    Return the rotatiosn and translations which are possessed by the structure.

    Examples::

        >>> from qmpy.io import read
        >>> from qmpy.analysis.symmetry import get_structure_symmetry
        >>> structure = read('POSCAR')
        >>> get_structure_symmetry(structure)

    """
    if 'spglib' not in method.lower():
        raise NotImplementedError("Currently only supports analysis based on"
                                  " spglib routines")
    return spglib.get_symmetry(__structure_to_cell(structure),
                               symprec=symprec,
                               angle_tolerance=angle_tolerance)


def get_symmetry_dataset(structure,
                         symprec=1e-5,
                         angle_tolerance=-1.0):
    """
    Return a full set of symmetry information from a given input structure.

    Mapping values:
        number: International space group number
        international: International symbol
        hall: Hall symbol
        transformation_matrix:
          Transformation matrix from lattice of input cell to Bravais lattice
          L^bravais = L^original * Tmat
        origin shift: Origin shift in the setting of 'Bravais lattice'
        rotations, translations:
          Rotation matrices and translation vectors
          Space group operations are obtained by
            [(r,t) for r, t in zip(rotations, translations)]
        wyckoffs:
          Wyckoff letters

    Examples::

        >>> from qmpy.io import read
        >>> from qmpy.analysis.symmetry import get_symmetry_dataset
        >>> structure = read('POSCAR')
        >>> get_symmetry_dataset(structure)

    """
    keys = ('number',
            'hall_number',
            'international',
            'hall',
            'transformation_matrix',
            'origin_shift',
            'rotations',
            'translations',
            'wyckoffs',
            'equivalent_atoms',
            'std_lattice',
            'std_types',
            'std_positions',
            'pointgroup_number',
            'pointgroup')

    cell = structure.cell.T.copy()
    coords = np.array(structure.site_coords)
    comps = structure.site_compositions
    numbers = [ comps.index(c) for c in comps ]
    numbers = np.array(numbers, dtype='intc')

    dataset = {}
    for key, data in zip(keys, spg.dataset(cell,
                                           coords,
                                           numbers,
                                           symprec,
                                           angle_tolerance)):
        dataset[key] = data

    dataset['international'] = dataset['international'].strip()
    dataset['hall'] = dataset['hall'].strip()
    dataset['transformation_matrix'] = np.array(dataset['transformation_matrix'], dtype='double', order='C')
    dataset['origin_shift'] = np.array(dataset['origin_shift'], dtype='double')
    dataset['rotations'] = np.array(dataset['rotations'], dtype='intc', order='C')
    dataset['translations'] = np.array(dataset['translations'], dtype='double', order='C')
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    dataset['wyckoffs'] = [letters[x] for x in dataset['wyckoffs']]
    dataset['equivalent_atoms'] = np.array(dataset['equivalent_atoms'], dtype='intc')
    dataset['std_lattice'] = np.array(np.transpose(dataset['std_lattice']), dtype='double', order='C')
    dataset['std_types'] = np.array(dataset['std_types'], dtype='intc')
    dataset['std_positions'] = np.array(dataset['std_positions'], dtype='double', order='C')
    dataset['pointgroup'] = dataset['pointgroup'].strip()

    return dataset

def get_spacegroup(structure, symprec=1e-5, angle_tolerance=-1.0):
    """
    Return space group in international table symbol and number
    as a string.
    """
    cell = structure.cell.T.copy(),
    scaled = structure.site_coords.copy()
    comps = structure.site_compositions
    numbers = [ comps.index(c) for c in comps ]
    numbers = np.array(numbers, dtype='intc')
    # Atomic positions have to be specified by scaled positions for spglib.
    return int(spg.spacegroup(cell,
                          coords,
                          numbers,
                          symprec,
                          angle_tolerance).strip(' ()'))

def get_pointgroup(rotations):
    """
    Return point group in international table symbol and number.
    """

    # (symbol, pointgroup_number, transformation_matrix)
    return spg.pointgroup(rotations)

def refine_cell(structure, symprec=1e-5, angle_tolerance=-1.0):
    """
    Return refined cell
    """
    # Atomic positions have to be specified by scaled positions for spglib.
    num_atom = len(structure.sites)
    cell = structure.cell.T.copy()
    coords = np.zeros((num_atom * 4, 3), dtype='double')
    coords[:num_atom] = structure.site_coords.copy()
    comps = structure.site_compositions
    numbers = [ comps.index(c) for c in comps ]
    numbers = np.array(numbers*4, dtype='intc')

    num_atom_bravais = spg.refine_cell(cell,
                                       coords,
                                       numbers,
                                       num_atom,
                                       symprec,
                                       angle_tolerance)

    coords = wrap(coords)
    comps = [ comps[i] for i in numbers ]
    if num_atom_bravais > 0:
        structure.cell = cell.T
        structure.set_nsites(num_atom_bravais)
        structure.site_coords = coords[:num_atom_bravais]
        structure.site_compositions = comps[:num_atom_bravais]
        return structure
    else:
        return structure


def find_primitive(structure, symprec=1e-4, angle_tolerance=-1.0):
    """
    A primitive cell in the input cell is searched and returned
    as an object of Atoms class.
    If no primitive cell is found, (None, None, None) is returned.
    """
    cell = structure.cell.T.copy()
    coords = np.array(structure.site_coords.copy(), dtype='double')
    comps = structure.site_compositions
    numbers = [ comps.index(c) for c in comps ]
    numbers = np.array(numbers*4, dtype='intc')

    num_atom_prim = spg.primitive(cell,
                                  coords,
                                  numbers,
                                  symprec,
                                  angle_tolerance)

    coords = wrap(coords)
    comps = [ comps[i] for i in numbers ]
    if num_atom_prim > 0:
        structure.cell = cell.T
        structure.set_nsites(num_atom_prim)
        structure.site_coords = coords[:num_atom_prim]
        structure.site_compositions = comps[:num_atom_prim]
        return structure
    else:
        return structure

def parse_sitesym(sitesym, sep=','):
    rot = np.zeros((3, 3))
    trans = np.zeros(3)
    for i, s in enumerate (sitesym.split(sep)):
        s = s.lower().strip()
        while s:
            sign = 1
            if s[0] in '+-':
                if s[0] == '-':
                    sign = -1
                s = s[1:]
            if s[0] in 'xyz':
                j = ord(s[0]) - ord('x')
                rot[i, j] = sign
                s = s[1:]
            elif s[0].isdigit() or s[0] == '.':
                n = 0
                while n < len(s) and (s[n].isdigit() or s[n] in '/.'):
                    n += 1
                t = s[:n]
                s = s[n:]
                trans[i] = float(frac.Fraction(t))
            else:
                raise ValueError('Failed to parse symmetry of %s' % (sitesym))
    return rot, trans
