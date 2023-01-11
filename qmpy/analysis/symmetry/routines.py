# wrappers for some `spglib` functions  | https://atztogo.github.io/spglib/
# wrappers for some `phonopy` functions | http://atztogo.github.io/phonopy/

import fractions as frac
import numpy as np
import logging

import qmpy

import qmpy.data as data
from qmpy.utils import *

try:
    import spglib
    _FOUND_SPGLIB = True
except ImportError:
    _FOUND_SPGLIB = False

try:
    import phonopy
    _FOUND_PHONOPY = True
except ImportError:
    _FOUND_PHONOPY = False
else:
    import phonopy.interface.vasp as phpy_iv
    import phonopy.structure.cells as phpy_sc

logger = logging.getLogger(__name__)


# SPGLIB #

def _check_spglib_install():
    """Imports `spglib`, raises :exc:`ImportError` if unsuccessful."""
    if not _FOUND_SPGLIB:
        error_message = 'Could not import `spglib`. Is it installed?'
        raise ImportError(error_message)


def _check_spglib_success(cell,
                          func='standardize_cell',
                          verbosity=0):
    """
    Checks if `spglib` was successful, log error messages if not.

    Args:
        cell: Output from `spglib` functions. None or a tuple.
        func: String with the name of the parent `spglib` function
        verbosity: Integer with the level of standard output verbosity.

    Returns:
        True if `spglib` was successful, False if not.

    """
    if cell is None:
        err_msg = "`spglib.{}` failed".format(func)
        if verbosity > 0:
            print(err_msg)
        logging.debug(err_msg)
        return False
    else:
        return True


def _structure_to_cell(structure):
    """
    Converts :class:`qmpy.Structure` objects to tuple of (lattice, positions,
    atom_types, magmoms) for input to `spglib` functions.

    Args:
        structure: :class:`qmpy.Structure` object with the crystal structure.

    Returns:
        Tuple of (`lattice`, `positions`, `atom_types`) or (`lattice`,
        `positions`, `atom_types`, `magmoms`) depending on whether any
        `structure.magmoms` is nonzero.

        `lattice` is a 3x3 array of float.
        `positions` is an Nx3 array of float.
        `atom_types` in an Nx1 list of integers.
        `magmoms` (if specified) is an Nx1 array of float, where N is the
        number of atoms in `structure.

        `atom_types` has numbers in place of element symbols
        (see :func:`qmpy.Structure.species_id_types`).

    Raises:
        :exc:`qmpy.StructureError` if `structure` is not a
        :class:`qmpy.Structure` object.

    """
    if not isinstance(structure, qmpy.Structure):
        raise qmpy.StructureError('Input is not of type `qmpy.Structure`')
    lattice = structure.cell.copy()
    positions = structure.site_coords.copy()
    numbers = structure.species_id_types.copy()
    magmoms = structure.magmoms.copy()
    if not any(magmoms):
        return (lattice, positions, numbers)
    else:
        return (lattice, positions, numbers, magmoms)


def _cell_to_structure(cell, structure, rev_lookup):
    """
    Assign crystal structure info in `cell` onto `structure`.

    Args:
        cell: Tuple of (lattice, positions, atom_indices) output from `spglib`
            functions. See `_structure_to_cell()` for more details.
        structure: `qmpy.Structure` object with the crystal structure.
        rev_lookup: Dictionary mapping the atomic indices onto elements.

    Returns:
        None. (`structure` is modified in place.)

    """
    if not isinstance(structure, qmpy.Structure):
        raise qmpy.StructureError('Input is not of type `qmpy.Structure`')
    structure.cell = cell[0]
    nsites = len(cell[1])
    structure.set_nsites(nsites)
    structure.site_coords = cell[1]
    site_comps = [rev_lookup[k] for k in cell[2]]
    structure.site_compositions = site_comps


def get_structure_symmetry(structure,
                           symprec=1e-3):
    """
    Gets symmetry operations for `structure` using `spglib`.

    Args:
        structure: :class:`qmpy.Structure` object with the crystal structure.
        symprec: Float with the Cartesian distance tolerance.

    Returns:
        Dictionary of symmetry operations with keys "translations",
        "rotations", "equivalent_atoms" and values Nx(3x3) array of float,
        Nx3 array of integers, Nx3 array of integers, respectively.

        None if `spglib` is unable to determine symmetry.

    Raises:
        ImportError: If `spglib` cannot be imported.

    """
    _check_spglib_install()
    return spglib.get_symmetry(
        _structure_to_cell(structure),
        symprec=symprec
    )


def get_symmetry_dataset(structure,
                         symprec=1e-3):
    """
    Get complete symmetry information for `structure` using `spglib`.

    Args:
        structure: :class:`qmpy.Structure` object with the crystal structure.
        symprec: Float with the Cartesian distance tolerance.

    Returns:
        Dictionary of various symmetry related information:
        - `choice`: Choice of origin, basis vector centering
        - `equivalent_atoms`: Nx1 array of integers specifying which atoms are
              symmetrically equivalent
        - `hall`: String with the Hall symbol
        - `hall_number`: Long integer with the Hall number
        - `international`: String ITC space group short symbol
        - `mapping_to_primitive`: Nx1 array of integers with the atomic indices
              in the primitive unit cell
        - `number`: Long integer with the ITC space group number
        - `origin_shift`: 1x3 array of float with shift of origin
        - `pointgroup`: String with the point group symbol
        - `rotations`: Nx(3x3) array of float with rotation operations
        - `std_lattice`: 3x3 array of float with standardized lattice vectors
        - `std_positions`: Nx3 array of float with standardized atomic
              positions in fractional coordinates
        - `std_types`: Nx1 array of integers with atomic indices in the
              standardized unit cell
        - `std_mapping_to_primitive`: Nx1 array of integers with the atomic
              indices in the standardized primitive unit cell
        - `transformation_matrix`: 3x3 array of float with the transformation
              to standardized unit cell
        - `translations`: Nx3 array of float with translation operations
        - `wyckoffs`: Nx1 array of string with the Wyckoff symbol of each site

        The original reference for the dataset is at
        https://atztogo.github.io/spglib/python-spglib.html#get-symmetry-dataset
        and may change in future versions.

        None if `spglib` fails to determine symmetry.

    Raises:
        ImportError: If `spglib` cannot be imported.

    """
    _check_spglib_install()
    return spglib.get_symmetry_dataset(
        _structure_to_cell(structure),
        symprec=symprec
    )


def get_spacegroup(structure,
                   symprec=1e-3,
                   symbol_type=0):
    """
    Get the space group symbol and number of a crystal structure.

    Args:
        structure: :class:`qmpy.Structure` object with the crystal structure.
        symprec: Float with the Cartesian distance tolerance.
        symbol_type: Integer with the type: 0 - Schoenflies, 1 - ITC short

    Returns:
        String with the space group symbol and number. E.g. u"R-3m (166)"

        None if `spglib` fails to determine the space group.

    Raises:
        ImportError: If `spglib` cannot be imported.

    """
    _check_spglib_install()
    return spglib.get_spacegroup(
        _structure_to_cell(structure),
        symprec=symprec,
        symbol_type=symbol_type
    )


def get_spacegroup_type(hall_number):
    """
    Get space group information corresponding to the Hall number.

    Args:
        hall_number: Integer with the Hall number.

    Returns:
        Dictionary with the corresponding space group information. Keys:
        - `arithmetic_crystal_class_number`
        - `arithmetic_crystal_class_symbol`
        - `choice`
        - `hall_symbol`
        - 'international`
        - `international_full`
        - `international_short`
        - `number`
        - `pointgroup_international`
        - `pointgroup_schoenflies`
        - `schoenflies`

        None if `spglib` fails to determine space group type.

    Raises:
        ImportError: If `spglib` cannot be imported.

    """
    _check_spglib_install()
    return spglib.get_spacegroup_type(hall_number)


def get_pointgroup(structure):
    """
    Get the point group of the crystal structure.

    Args:
        structure: :class:`qmpy.Structure` object with the crystal structure.

    Returns:
        List of point group symbol, point group number, and the
        transformation matrix.

        None if `spglib` fails to determine symmetry.

    Raises:
        ImportError: If `spglib` cannot be imported.

    """
    _check_spglib_install()
    data = get_structure_symmetry(structure)
    if data is None:
        return None
    else:
        return spglib.get_pointgroup(data['rotations'])


def standardize_cell(structure,
                     to_primitive=True,
                     no_idealize=False,
                     symprec=1e-3,
                     verbosity=0):
    """
    Standardizes the input crystal structure using `spglib`.

    Args:
        structure: :class:`qmpy.Structure` object with a crystal structure.
        to_primitive: Boolean specifying whether to convert the input structure
            to a primitive unit cell.
        no_idealize: Boolean specifying whether to "idealize" lattice vectors,
            angles according to the ITC.
        symprec: Float with the Cartesian distance tolerance.
        verbosity: Integer with the level of standard output verbosity.

    Returns: :class:`qmpy.Structure` object with the standardized unit cell
        if successful, the input structure as is, otherwise.

    """
    _check_spglib_install()
    rev_lookup = dict(zip(structure.site_comp_indices,
                          structure.site_compositions))
    cell = spglib.standardize_cell(
        _structure_to_cell(structure),
        to_primitive=to_primitive,
        no_idealize=no_idealize,
        symprec=symprec
    )
    if not _check_spglib_success(cell,
                                 verbosity=verbosity):
        return structure
    _cell_to_structure(cell, structure, rev_lookup)
    return structure


def refine_cell(structure,
                symprec=1e-3,
                verbosity=0):
    """
    Refines the input crystal structure to within a tolerance using `spglib`.

    Args:
        structure: :class:`qmpy.Structure` object with a crystal structure.
        symprec: Float with the Cartesian distance tolerance.
        verbosity: Integer with the level of standard output verbosity.

    Returns: :class:`qmpy.Structure` object with the refined unit cell
        if successful, the input structure as is, otherwise.

    """
    _check_spglib_install()
    rev_lookup = dict(zip(structure.site_comp_indices,
                          structure.site_compositions))
    cell = spglib.refine_cell(
        _structure_to_cell(structure),
        symprec=symprec
    )
    if not _check_spglib_success(cell,
                                 func='refine_cell',
                                 verbosity=verbosity):
        return structure
    _cell_to_structure(cell, structure, rev_lookup)
    return structure


def find_primitive(structure,
                   symprec=1e-3,
                   verbosity=0):
    """
    Finds the primitive unit cell of the crystal structure.

    Args:
        structure: :class:`qmpy.Structure` object with a crystal structure.
        symprec: Float with the Cartesian distance tolerance.
        verbosity: Integer with the level of standard output verbosity.

    Returns: :class:`qmpy.Structure` object with the primitive unit cell
        if successful, the input structure as is, otherwise.

    """
    _check_spglib_install()
    rev_lookup = dict(zip(structure.site_comp_indices,
                          structure.site_compositions))
    cell = spglib.find_primitive(
        _structure_to_cell(structure),
        symprec=symprec
    )
    if not _check_spglib_success(cell,
                                 func='find_primitive',
                                 verbosity=verbosity):
        return structure
    _cell_to_structure(cell, structure, rev_lookup)
    return structure


def get_symmetry_from_database(hall_number):
    """
    Get symmetry operations corresponding to a Hall number.

    Args:
        hall_number: Integer with the Hall number.

    Returns:
        Dictionary of symmetry operations with keys "rotations", "translations"
        and values Nx(3x3) array of integers, Nx3 array of float, respectively.

        None if `spglib` is unable to determine symmetry.

    Raises:
        ImportError: If `spglib` cannot be imported.

    """
    _check_spglib_install()
    return spglib.get_symmetry_from_database(hall_number)


def niggli_reduce(structure,
                  symprec=1e-3):
    """
    TODO: Get the Niggli reduced cell of the input structure.
    """
    raise NotImplementedError


def delauney_reduce(structure,
                    symprec=1e-3):
    """
    TODO: Get the Delauney reduced cell of the input structure.
    """
    raise NotImplementedError


# PHONOPY #

def _check_phonopy_install():
    """Imports `phonopy`, raises :exc:`ImportError` if unsuccessful."""
    if not _FOUND_PHONOPY:
        error_message = 'Could not import `phonopy`. Is it installed?'
        raise ImportError(error_message)


def get_phonopy_style_supercell(structure,
                                supercell_matrix,
                                is_old_style=True,
                                symprec=1e-3,
                                in_place=False):
    """
    Wrapper function that generates a supercell of `structure` using `phonopy`.

    Args:
        structure:
            :class:`qmpy.Structure` object with the unit cell.

        supercell_matrix:
            A 3x3 array of Integers with the primitive -> supercell
            transformation matrix. Passed

        is_old_style:
            Phonopy-specific keyword. See notes under `get_supercell()`
            function in :mod:`phonopy.structure.cells`.

            Defaults to False.

        symprec:
            Float with the tolerance used to wrap atoms and eliminate
            overlapping atoms, if any, upon imposing periodic boundary
            conditions.

            Defaults to 1e-3.

            **NOTE**: The `phonopy` default is 1e-5, not 1e-3.

        in_place:
            Boolean specifying whether the unit cell in `structure` should be
            overwritten or not.

            Defaults to False.

    Returns:
        :class:`qmpy.Structure` object with the supercell.

    """
    _check_phonopy_install()

    if not in_place:
        structure_copy = structure.copy()
        return get_phonopy_style_supercell(
                structure_copy,
                supercell_matrix,
                is_old_style=is_old_style,
                symprec=symprec,
                in_place=True
        )

    phonopy_atoms = phpy_iv.read_vasp_from_strings(
            qmpy.io.poscar.write(structure))
    phonopy_sc = phpy_sc.get_supercell(
            unitcell=phonopy_atoms,
            supercell_matrix=supercell_matrix,
            is_old_style=is_old_style,
            symprec=symprec
    )
    num_atoms, symbols, positions, _ = phpy_iv.sort_positions_by_symbols(
            phonopy_sc.get_chemical_symbols(),
            phonopy_sc.get_scaled_positions()
    )

    structure.cell = phonopy_sc.get_cell()
    structure.set_nsites(sum(num_atoms))
    site_coords = [[float(c) for c in ac.strip().split()]
                   for ac in phpy_iv._get_scaled_positions_lines(positions)]
    structure.site_coords = site_coords
    site_comps = []
    for n, s in zip(num_atoms, symbols):
        site_comps.extend([s]*n)
    structure.site_compositions = site_comps

    return structure

