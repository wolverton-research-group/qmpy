# qmpy/analysis/vasp/phonons.py

import os
import six
import numbers
import numpy as np
from collections import defaultdict
from django.db import models

import phonopy.interface.vasp as phonopy_vasp
import phonopy.structure.cells as phonopy_cells

from qmpy import io
from qmpy.materials.entry import Entry
from qmpy.materials.structure import Structure
from qmpy.analysis.vasp.calculation import Calculation


class PhononCalculationError(Exception):
    """Base class to handle errors associated with phonon calculations."""


class PhononCalculation(models.Model):
    """Base class for managing/storing phonon calculations.

    Relationships:
        | :class:`qmpy.Composition` via composition
        | :class:`qmpy.Entry` via entry
        | :class:`qmpy.Structure` via input_structure. Completely relaxed
        |    primitive unit cell of the structure.
        | :class:`qmpy.Structure` via supercells/scs. Dictionary of
        |    supercells (of `input_structure`) with displaced atoms. Keys are
        |    of the form "sc_[n1]_[n2]" where n1 is the supercell index,
        |    and n2 is the magnitude of atomic displacement in 10^-2 Angstrom.
        | :class:`qmpy.Calculation` via supercell_calculations/sc_calcs.
        |    Dictionary of VASP calculations of the supercells.
        | :class:`qmpy.MetaData` via meta_data.

    Attributes:

    """
    composition = models.ForeignKey('Composition', null=True, blank=True)
    entry = models.ForeignKey('Entry', db_index=True, null=True, blank=True)
    input_structure = models.ForeignKey('Structure', db_index=True,
                                        null=True, blank=True)
    pristine_supercell = models.ForeignKey('Structure', null=True, blank=True)

    path = models.CharField(max_length=255, db_index=True, blank=True)

    @staticmethod
    def _get_default_supercell_matrix(prim_structure,
                                      simple_multiple=False,
                                      max_natoms=512):
        # if the 4x4x4 supercell has less than `max_natoms` atoms, use it
        smatrix = np.array([[4, 0, 0], [0, 4, 0], [0, 0, 4]])
        if np.linalg.det(smatrix)*prim_structure.natoms <= max_natoms:
            return smatrix
        # if `simple_multiple` is True, look only for NxNxN supercells
        if simple_multiple:
            while True:
                if abs(np.linalg.det(smatrix) - 1.) <= 1e-3:
                    break
                smatrix -= np.eye(3, dtype='int')
                if np.linalg.det(smatrix)*prim_structure.natoms <= max_natoms:
                    break
            return smatrix
        # if not, try finding the largest supercell with less than 512 atoms
        # of the form n1xn2xn3 (a more general supercell cannot be handled by
        # ShengBTE) that is closest to the simple-cubic shape by iteratively
        # decreasing the supercell size. (Larger non-cubic cells preferred over
        # smaller cubic ones. E.g., a 432-atom supercell with a 0.38
        # deviation from the cubic shape will be chosen over a 324-atom
        # supercell with 0.16 deviation from the cubic shape.)
        sc_shape = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        supercell_scores = defaultdict(dict)
        for n1 in range(4, 0, -1):
            for n2 in range(4, 0, -1):
                for n3 in range(4, 0, -1):
                    natoms = n1*n2*n3*prim_structure.natoms
                    if natoms > max_natoms:
                        continue
                    sc_key = 'x'.join(map(str, [n1, n2, n3]))
                    lat_vec = np.array([[n1, 0, 0],
                                        [0, n2, 0],
                                        [0, 0, n3]])*prim_structure.cell
                    sc_score = Structure.deviation_from_cell_shape(
                            lattice_vectors=lat_vec,
                            target_cell_shape=sc_shape
                    )
                    supercell_scores[natoms].update({sc_key: sc_score})
        if not supercell_scores:
            smatrix = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
            return smatrix
        best_natoms = sorted(supercell_scores.keys())[-1]
        n1n2n3, _ = sorted(supercell_scores[best_natoms].items(),
                           key=lambda x: x[1])[0]
        smatrix = map(int, n1n2n3.split('x'))*np.eye(3, dtype='int')
        return smatrix

    @classmethod
    def setup(cls,
              input_structure=None,
              path=None,
              entry=None,
              supercell_matrix=None,
              max_ifc_order=None,
              cluster_cutoffs=None,
              cs_solution_weights=None,
              holdout_fraction=None,
              n_supercells=None,
              atomic_displacements=None,
              ifc_conv_threshold=None,
              n_max_supercells=None,
              custom_dft_settings=None,
              verbosity=None,
              overwrite=True,
              from_scratch=False,
              **kwargs):
        """
        Method to create a new phonon calculation.

        Args:
            input_structure:
                :class:`qmpy.Structure` object with the initial (primitive)
                structure or String with the path to a POSCAR file with the
                initial primitive structure. The provided structure is assumed
                to be the ground state, i.e., it is not further relaxed using
                DFT in any manner.

            entry:
                :class:`qmpy.Entry` object with the OQMD entry corresponding
                to the structure if the entire OQMD framework is being used.

            path:
                String with the location where the calculations need to be run.

                If not specified (1 > 2 > 3 being the order of preference):
                1. If `input_structure` is a POSCAR file, the base directory
                with the POSCAR file is used.
                2. If `entry` is specified, defaults to a folder
                "[entry.path]/phonons".
                3. Current working directory.

            supercell_matrix:
                3x3 matrix of Integers with the transformation from the
                input primitive unit cell to the supercells to be used to
                calculate forces. E.g.: [[2, 2, 1], [2, 3, 4], [4, 3, 3]]

                Alternatively, if the input is 1x3 list of Integers,
                a diagonal matrix is assumed. E.g.:
                [3, 2, 2] -> [[3, 0, 0], [0, 2, 0], [0, 0, 2]]

                Alternatively, if the input is an Integer N, the transformation
                matrix is assumed to be N*I where I is the identity matrix.
                E.g.: 4 -> [[4, 0, 0], [0, 4, 0], [0, 0, 4]]

                If not specified, a default value of [4, 4, 4] is used. In
                case the latter supercell has more than 512 atoms,
                the largest [N1, N2, N3] supercell with <512 atoms is used.
                Cubic-like supercells are preferred in the latter step.

            max_ifc_order:
                Integer with the maximum order interatomic force constants (IFC)
                to be fit. Alternatively, String inputs "second", "third",
                "fourth" are recognized as valid inputs.

                If not specified, a default value of 2 (i.e., only second
                order IFCs are fit) is used.

            cluster_cutoffs:
                Dictionary with the cutoff radius for determining and including
                2-body, 3-body clusters. Keys are "2body" and "3body",
                and the corresponding values are Floats with the radii in nm.
                *NOTE*: the units are nm for by default, not Angstrom.

                If not specified, pair correlation distribution in the
                supercell specified by `input_structure` and `supercell_matrix`
                is used to determine cutoffs. For 2-body clusters,
                the default cutoff radius is the largest 2-body cluster. For
                3-body clusters, the default cutoff radius is half the size
                of the largest 2-body cluster.

            cs_solution_weights:
                List of Integers specifying the various \mu values to use in
                compressed sensing solution fit of IFCs:
                \phi_CS = arg min (|| \phi ||_1) +
                                  + \mu/2 (|| F - A \phi ||_2)^2
                The first term on the RHS of the above equation is the
                l1-norm term that drives solutions towards sparsity,
                while the second term is the l2-norm or the regular
                least-squares fitting. The parameter \mu adjusts the relative
                weights of the l1 and l2 terms. Higher values of \mu are
                prone to overfitting while small values of \mu result in very
                sparse underfitted IFCs.

                It is a good practice to test the fit with a range of \mu
                values, e.g.: [1, 20, 50, 100] and choose the best
                performing value.

                If not specified, [1, 10, 25, 50, 100, 250, 500, 1000] is
                used as default.

            holdout_fraction:
                Float with the fraction of the calculated interatomic forces
                held back while training, and used later for testing the
                accuracy of the fit.

                If not specified, a default value of 0.25 is used.

            n_supercells:
                Integer with the number of supercells to use to calculate
                interatomic force constants with VASP DFT calculations.

                If not specified, a default value of 2 is used.

            atomic_displacements:
                List of Integers with atomic displacements (in 10^-2 Angstrom)
                to use for each of the supercells specified in `n_supercells`.
                E.g., [1, 2, 3, 4] for `n_supercells` = 4 would use 0.01,
                0.02, 0.03, 0.04 Angstrom atomic diplacements in the first,
                second, third, and fourth supercell respectively.

                If the specified list has fewer elements than the number of
                supercells specified, displacements from the specified list
                are used in a round-robin fashion. E.g., if the number of
                supercells specified is 8, and list of displacements is [1,
                2, 3], then displacements used for each supercell is
                [1, 2, 3, 1, 2, 3, 1, 2]*10^-2 Angstrom, respectively.

                If not specified, a default value of [1, 2, 3, 4] is used.

            ifc_conv_threshold:
                Float with the threshold root-mean-square-error (RMSE) in
                the fitting of IFCs that is to be considered to be converged.
                No further supercells are calculated unless manually done so.

                If not specified, a default value of 0.05 is used.

            n_max_supercells:
                Integer with the maximum number of supercells to use for the
                calculation of interatomic forces. The iterative procedure of
                generating new supercells and calculating forces to add to
                the IFC-fitting-data is stopped when the maximum number of
                supercells specified is calculated or when the IFC have been
                fitted with sufficient accuracy (according to the specified
                `ifc_conv_threshold` parameter above), whichever happens
                earlier.

                If not specified, a default value of 10 is used.

            custom_dft_settings:
                Dictionary of VASP keywords and values to be used for the
                calculation of interatomic forces with DFT. These parameters
                are passed on to the :class:`qmpy.Calculation` object that is
                set up for each supercell.

                See the `setup()` function under :class:`qmpy.Calculation`,
                and its `settings` attribute.

                If not specified, defaults to the DFT settings specified in
                `qmpy.VASP_SETTINGS["sc_forces"]`.

            verbosity:
                Integer specifying the standard output verbosity.
                Values of <=0, 1, >=2 corresponding to low, moderate and high
                verbosity, respectively.

            overwrite:
                Boolean specifying if parameters of an existing
                :class:`qmpy.PhononCalculation`, if found, should be
                overwritten or not.

                **CAUTION**: Supercell folders and structures may be
                overwritten as well, if settings of the existing
                :class:`qmpy.PhononCalculation` object are incompatible with
                the input parameters.
                E.g., if the new supercell matrix specified ([4, 4, 4]) is
                different from that of the existing object ([3, 3, 3]), all
                supercells and consequently nearly all relevant files in the
                folder specified in `path` will be overwritten.

                If not specified, defaults to True.

            from_scratch:
                Boolean specifying if phonons for the input structure should
                be calculated from scratch.

                **CAUTION**: All existing supercell calculations and
                interatomic force constants fitting data in the folder
                specified by `path` *will* be deleted and cannot be recovered!

                If not specified, defaults to False.

            **kwargs:
                Miscellaneous keyword arguments

        Returns:
            `qmpy.PhononCalculation` object.

        """

        # Input crystal structure
        if isinstance(input_structure, six.string_types):
            if not os.path.isfile(input_structure):
                err_msg = 'Structure file {} not found'.format(input_structure)
                raise OSError(err_msg)
            struct_path = os.path.abspath(os.path.dirname(input_structure))
            input_structure = io.poscar.read(input_structure, **kwargs)

        # OQMD entry
        if entry is not None and not isinstance(entry, Entry):
            err_msg = '"entry" must be OQMD Entry object or None'
            raise PhononCalculationError(err_msg)

        # Path to the calculation folder
        if path is None:
            if entry is None:
                path = os.path.abspath(os.getcwd())
            elif entry.path is None:
                path = os.path.abspath(os.getcwd())
            else:
                path = os.path.join(os.path.abspath(entry.path), 'phonons')
        else:
            path = os.path.abspath(path)

        # Has the specified phonon calculation already been created?
        if PhononCalculation.objects.filter(path=path).exists():
            phonon_calc = PhononCalculation.objects.get(path=path)
        else:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            phonon_calc = PhononCalculation()
            phonon_calc.input_structure = input_structure
            phonon_calc.entry = entry
            phonon_calc.path = path
            phonon_calc.kwargs = kwargs

        # What is the primitive -> supercell transformation matrix?
        if supercell_matrix is None:
            phonon_calc.supercell_matrix = cls._get_supercell_matrix(
                    input_structure)
        if isinstance(supercell_matrix, numbers.Integral):
            np.eye(3, dtype='int')*int(supercell_matrix)










    def generate_pristine_supercell(self):
        phonopy_uc = phonopy_vasp.read_vasp()


    def generate_csld_ini(self):
        pass

    def generate_supercells_with_displacements(self):
        pass

    def add_supercells(self):
        pass

