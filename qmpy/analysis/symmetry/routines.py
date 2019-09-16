# wrappers for spglib functions | https://atztogo.github.io/spglib/
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

logger = logging.getLogger(__name__)


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

        `lattice` is a 3x3 array of float, `positions` is an Nx3 array of
        float, `atom_types` in an Nx1 list of integers, `magmoms` (if
        specified) is an Nx1 array of float, where N is the number of atoms
        in `structure. `atom_types` has numbers in place of element symbols
        (see :func:`qmpy.Structure.site_comp_indices`).

    Raises:
        :exc:`qmpy.StructureError` if `structure` is not a
        :class:`qmpy.Structure` object.

    """
    if not isinstance(structure, qmpy.Structure):
        raise qmpy.StructureError('Input is not of type `qmpy.Structure`')
    lattice = structure.cell.copy()
    positions = structure.site_coords.copy()
    numbers = structure.site_comp_indices.copy()
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
    structure.set_nsites_manager(cell[1])
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

