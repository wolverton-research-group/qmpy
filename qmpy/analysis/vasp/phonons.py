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
from qmpy.materials.structure import StructureError
from qmpy.analysis.symmetry.routines import get_phonopy_style_supercell
from qmpy.analysis.vasp.calculation import Calculation


def _parsing_err_msg(argument, user_input=None):
    return ('Failed to parse input'
            ' `{}` = {}').format(argument, user_input)


def _parse_supercell_matrix(supercell_matrix):
        if isinstance(supercell_matrix, numbers.Integral):
            _smatrix = np.eye(3, dtype=int)*int(supercell_matrix)
        elif np.shape(supercell_matrix) == (3, ):
            _smatrix = map(int, supercell_matrix)*np.eye(3, dtype=int)
        elif np.shape(supercell_matrix) == (9, ):
            _smatrix = np.array(supercell_matrix).reshape(3, 3)
        elif np.shape(supercell_matrix) == (3, 3):
            _smatrix = np.array(supercell_matrix)
        else:
            raise PhononCalculationError(_parsing_err_msg(
                    'supercell_matrix', supercell_matrix
            ))


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
                                      max_natoms=200):
        # if the 4x4x4 supercell has less than `max_natoms` atoms, use it
        smatrix = np.array([[4, 0, 0], [0, 4, 0], [0, 0, 4]])
        if np.linalg.det(smatrix)*prim_structure.natoms <= max_natoms:
            return smatrix
        # if `simple_multiple` is True, look only for NxNxN supercells
        if simple_multiple:
            while True:
                if abs(np.linalg.det(smatrix) - 1.) <= 1e-3:
                    break
                smatrix -= np.eye(3, dtype=int)
                if np.linalg.det(smatrix)*prim_structure.natoms <= max_natoms:
                    break
            return smatrix
        # if not, try finding the largest supercell with less than 200 atoms
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
                                        [0, 0, n3]]).dot(prim_structure.cell)
                    sc_score = Structure.get_deviation_from_cell_shape(
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
        smatrix = map(int, n1n2n3.split('x'))*np.eye(3, dtype=int)
        return smatrix

    @staticmethod
    def get_cluster_cutoff_radius(structure=None, cluster_type=2):
        """
        Calculates the default cutoff radii for including and performing
        symmetry analysis of 2-body and 3-body clusters in `structure`.

        For including clusters in the sensing matrix, if user input is not
        specified, this method can be used to get some sensible defaults.
        Note that the input structure to this method should be a supercell
        with or without atomic displacements that you (plan to) use to
        calculate interatomic forces, and **NOT** the primitive cell. No
        periodic images are created to "expand" the input structure in any way.
        Currently, by default, the radial distribution of an atom chosen at
        random from `structure` is calculated, and the maximum pair distance
        is chosen as the cutoff for 2-body clusters, and 40% of the maximum
        as the cutoff for 3-body clusters.

        TODO: A statistical way to determine 3-body cutoff radius.

        Args:
            structure:
                :class:`qmpy.Structure` object with the crystal structure.

            cluster_type:
                Integer specifying the kind of cluster (2-body, 3-body, etc.)

        Returns:
            Float with the cluster cutoff radius in Angstrom.

        """
        if structure is None:
            return None
        elif isinstance(structure, six.string_types):
            if not os.path.isfile(structure):
                raise OSError('Structure file "{}" not found'.format(structure))
            structure = io.poscar.read(structure)
        elif isinstance(structure, Structure):
            pass
        else:
            err_msg = '`structure` must be POSCAR or `qmpy.Structure` object'
            raise StructureError(err_msg)
        scale = {2: 1.0, 3: 0.4}.get(cluster_type, 1.)
        rd = structure.get_radial_distances()
        return max(rd['distances'].values())*scale

    @classmethod
    def setup(cls,
              input_structure=None,
              path=None,
              entry=None,
              max_ifc_order=None,
              ifc2_from_phonopy=None,
              csld_ini_file=None,
              supercell_matrix=None,
              atomic_displacements=None,
              cluster_cutoffs=None,
              fitting_weghts=None,
              holdout_fraction=None,
              n_supercells=None,
              ifc_conv_threshold=None,
              n_max_supercells=None,
              custom_dft_settings=None,
              overwrite=True,
              from_scratch=False,
              verbosity=None,
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

            path:
                String with the location where the calculations need to be run.

                If not specified (1 > 2 > 3 being the order of preference):
                1. If `input_structure` is a POSCAR file, the base directory
                with the POSCAR file is used.
                2. If `entry` is specified, defaults to a folder
                "[entry.path]/phonons".
                3. Current working directory.

            entry:
                :class:`qmpy.Entry` object with the OQMD entry corresponding
                to the structure if the entire OQMD framework is being used.

            max_ifc_order:
                Integer with the maximum order interatomic force constants (IFC)
                to be fit. Alternatively, String inputs "second" and "third"
                are recognized as valid inputs.

                **NOTE**: Currently only up to third-order implemented.

                Defaults to a value of 2 (i.e., only second order IFCs are
                fit) is used.

            ifc2_from_phonopy:
                Boolean specifying whether second order force constants
                should be calculated using the method of finite-displacements
                using the `phonopy` package.

                (The higher order force constants, if requested, will still be
                calculated using CSLD. For complex crystals, especially those
                with > 20 atoms/unit cell and reasonably high symmetry,
                (a) calculating 2nd order IFCs with CSLD can be almost as
                expensive or more than traditional finite-displacements method
                (b) separately fitting 2-order IFCs using traditional
                finite-displacements, and then using CSLD only for
                higher-order IFCs is cheaper *and* more accurate.)

                Defaults to False if the number of atoms/primitive cell <= 20,
                True otherwise.

            csld_ini_file:
                String specifying the location of the .ini file with settings
                related to CSLD. See documentation for the
                `self.write_csld_ini()` function for details.

                If specified, the settings read from the INI file
                *WILL BE OVERWRITEN!* by any overlapping settings passed as
                arguments later (e.g., `supercell_matrix`, `cluster_cutoffs`,
                `fitting_weights`, `holdout_fraction`, `atomic_displacements`).

                Defaults to None.

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
                case the latter supercell has more than 200 atoms,
                the largest [N1, N2, N3] supercell with <200 atoms is used.
                Cubic-like supercells are preferred in the latter step.

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

            cluster_cutoffs:
                Dictionary with the cutoff radius for determining and including
                2-body, 3-body clusters. Keys are Integers, 2 and 3, and the
                corresponding values are Floats with the radii in Angstrom.

                If not specified, pair correlation distribution in the
                supercell specified by `input_structure` and `supercell_matrix`
                is used to determine cutoffs. For 2-body clusters,
                the default cutoff radius is the largest 2-body cluster. For
                3-body clusters, the default cutoff radius is 40% the size
                of the largest 2-body cluster.

            fitting_weghts:
                List of Integers or Float specifying the various \mu values to
                use in compressed sensing solution fit of IFCs:
                \phi_CS = arg min (|| \phi ||_1) +
                                  + \mu/2 (|| F - A \phi ||_2)^2
                The first term on the RHS of the above equation is the
                L1-norm term that drives solutions towards sparsity,
                while the second term is the L2-norm or the regular
                least-squares fitting. The parameter \mu adjusts the relative
                weights of the L1- and L2- terms. Higher values of \mu are
                prone to overfitting while small values of \mu result in very
                sparse underfitted IFCs.

                It is a good practice to test the fit with a range of \mu
                values, e.g.: [1, 20, 50, 100] and choose the best
                performing value.

                Defaults to [1, 25, 100, 400, 1000].

            holdout_fraction:
                Float with the fraction of the calculated interatomic forces
                held back while training, and used later for testing the
                accuracy of the fit.

                Defaults to 0.25.

            n_supercells:
                Integer with the number of supercells to use to calculate
                interatomic force constants with VASP DFT calculations.

                Defaults to 2.

            ifc_conv_threshold:
                Float with the threshold root-mean-square-error (RMSE) in
                the fitting of IFCs that is to be considered to be converged.
                No further supercells are calculated unless manually done so.

                Defaults to 0.05.

            n_max_supercells:
                Integer with the maximum number of supercells to use for the
                calculation of interatomic forces. The iterative procedure of
                generating new supercells and calculating forces to add to
                the IFC-fitting-data is stopped when the maximum number of
                supercells specified is calculated or when the IFC have been
                fitted with sufficient accuracy (according to the specified
                `ifc_conv_threshold` parameter above), whichever happens
                earlier.

                Defaults to 10.

            custom_dft_settings:
                Dictionary of VASP keywords and values to be used for the
                calculation of interatomic forces with DFT. These parameters
                are passed on to the :class:`qmpy.Calculation` object that is
                set up for each supercell.

                See the `setup()` function under :class:`qmpy.Calculation`,
                and its `settings` attribute.

                Defaults to the DFT settings specified in
                `qmpy.VASP_SETTINGS["sc_forces"]`.

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

                Defaults to True.

            from_scratch:
                Boolean specifying if phonons for the input structure should
                be calculated from scratch.

                **CAUTION**: All existing supercell calculations and
                interatomic force constants fitting data in the folder
                specified by `path` *will* be deleted and cannot be recovered!

                Defaults to False.

            verbosity:
                Integer specifying the standard output verbosity.
                Values of <=0, 1, >=2 corresponding to low, moderate and high
                verbosity, respectively.

                Defaults to 1.

            **kwargs:
                Miscellaneous keyword arguments

        Returns:
            `qmpy.PhononCalculation` object.

        """

        # Input crystal structure
        input_structure_folder = None
        if isinstance(input_structure, six.string_types):
            if not os.path.isfile(input_structure):
                err_msg = 'Structure file {} not found'.format(input_structure)
                raise OSError(err_msg)
            input_structure_folder = os.path.abspath(os.path.dirname(
                    input_structure))
            input_structure = io.poscar.read(input_structure, **kwargs)

        # OQMD entry
        if entry is not None and not isinstance(entry, Entry):
            err_msg = '"entry" must be OQMD Entry object or None'
            raise PhononCalculationError(err_msg)

        # Path to the calculation folder
        if path is None:
            if input_structure_folder is not None:
                path = input_structure_folder
            elif entry is None:
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

        # Up to what order IFCs should be fit?
        nie_err_msg = 'Only up to 3rd order implemented so far'
        if isinstance(max_ifc_order, six.string_types):
            if max_ifc_order.lower() == 'second':
                _mio = 2
            elif max_ifc_order.lower() == 'third':
                _mio = 3
            elif max_ifc_order.lower() == 'fourth':
                raise NotImplementedError(nie_err_msg)
            else:
                raise PhononCalculationError(_parsing_err_msg(
                        'max_ifc_order', max_ifc_order
                ))
        elif isinstance(max_ifc_order, numbers.Integral):
            if max_ifc_order > 3:
                raise NotImplementedError(nie_err_msg)
            _mio = max_ifc_order if max_ifc_order >= 2 else 2
        elif max_ifc_order is None:
            _mio = 2
        else:
            raise PhononCalculationError(_parsing_err_msg(
                    'max_ifc_order', max_ifc_order
            ))
        phonon_calc.max_ifc_order = _mio

        # Should I calculate 2-order IFCs via traditional enumerative
        # finite-diplacements approach (using `phonopy`)?
        _ifc2_fd = False
        if _ifc2_fd is not None:
            _ifc2_fd = ifc2_from_phonopy
            if isinstance(ifc2_from_phonopy, six.string_types):
                _ifc2_fd = ifc2_from_phonopy.lower()[0] == 't'
        phonon_calc.ifc2_from_phonopy = _ifc2_fd

        # Location of the INI file with related settings
        phonon_calc.csld_ini_file = None
        if csld_ini_file is not None:
            if not os.path.isfile(csld_ini_file):
                err_msg = 'CSLD INI file "{}" not found'.format(csld_ini_file)
                raise OSError(err_msg)
            phonon_calc.csld_ini_file = csld_ini_file

        # Read settings from the CSLD INI file, if specified
        # For now the settings read are: primitive -> supercell
        # transformation matrix, magnitude of atomic displacements, cluster
        # cutoff radii, CS fitting weights, holdout-fraction of IFC data
        _smatrix = None
        _ad = [1, 2, 3, 4]
        _ccs = {2: None, 3: None}
        _fw = [1, 25, 100, 400, 1000]
        _hf = 0.25
        csld_ini_dict = io.ini.read(phonon_calc.csld_ini_file)
        for section, options in csld_ini_dict.items():
            for option, value in options.items():
                if section.lower() == 'supercell':
                    if value.lower() == 'tmatrix':
                        csld_smatrix = map(int, value.strip().split())
                        _smatrix = _parse_supercell_matrix(csld_smatrix)
                    elif value.lower() == 'disp':
                        _ad = map(int, value.strip().split())
                elif section.lower() == 'cluster':
                    if value.lower() == '2body':
                        _ccs[2] = float(value.strip())
                    elif value.lower() == '3body':
                        _ccs[3] = float(value.strip())
                elif section.lower() == 'csfit':
                    if value.lower() == 'mu':
                        _fw = map(int, value.strip().split())
                    elif value.lower() == 'holdout':
                        _hf = float(value.strip())

        # *OVERWRITE* values read from the CSLD INI file with input function
        # arguments, if any overlapping ones are provided.

        # The primitive unit cell -> supercell transformation matrix
        if supercell_matrix is not None:
            _smatrix = _parse_supercell_matrix(supercell_matrix)
        # If CSLD INI and `supercell_matrix` are not input, use sensible
        # default values
        if _smatrix is None:
            _smatrix = PhononCalculation._get_default_supercell_matrix(
                input_structure)
        phonon_calc.supercell_matrix = _smatrix

        # What magnitude of atomic displacement to use for each supercell?
        if atomic_displacements is not None:
            _ad = map(int, atomic_displacements)
        phonon_calc.atomic_displacements = _ad

        # What radii cutoffs should be used for identifying symmetrically
        # unique (and then including for sensing) 2-body and 3-body clusters?
        if cluster_cutoffs is not None:
            _ccs.update({
                2: cluster_cutoffs.get(2, None),
                3: cluster_cutoffs.get(3, None)
            })
        for k in _ccs:
            if _ccs[k] is None:
                _ccs[k] = PhononCalculation.get_cluster_cutoff_radius(
                        structure=phonon_calc.pristine_supercell,
                        cluster_type=k
                )
        phonon_calc.cluster_cutoffs = _ccs

        # What values of \mu (weight of L2-norm, the least-squares residual,
        # vs the L1-norm, the sparsity of the solution) to use in the
        # compressed sensing fitting?
        if fitting_weghts is not None:
            if isinstance(fitting_weghts, numbers.Number):
                _fw = [fitting_weghts]
            elif isinstance(fitting_weghts, list):
                _fw = fitting_weghts
            else:
                raise PhononCalculationError(_parsing_err_msg(
                        'fitting_weights', fitting_weghts
                ))
        phonon_calc.fitting_weights = _fw

        # What fraction of the forces must be held back for testing the fit?
        if holdout_fraction is not None:
            _hf = float(holdout_fraction)
        phonon_calc.holdout_fraction = _hf

        # How many supercells with displacements must be calculated initially?
        _ns = 2
        if n_supercells is not None:
            _ns = int(n_supercells)
        phonon_calc.n_supercells = _ns

        # What is the convergence threshold for the fitted IFCs?
        _ict = 0.05
        if ifc_conv_threshold is not None:
            _ict = float(ifc_conv_threshold)
        phonon_calc.ifc_conv_threshold = _ict

        # What is the maximum number of supercells that must be used to
        # calculate/fit the IFCs?
        _nms = 10
        if n_max_supercells is not None:
            _nms = int(n_max_supercells)
        phonon_calc.n_max_supercells = _nms

        # Any custom DFT settings to use for calculating forces
        phonon_calc.custom_dft_calculations = custom_dft_settings

        # Should I overwrite any currently existing calculations?
        _overwrite = True
        if overwrite is not None:
            _overwrite = overwrite
            if isinstance(overwrite, six.string_types):
                _overwrite = overwrite.lower()[0] == 't'

        # Should I calculate phonons for this structure from scratch?
        _from_scratch = False
        if from_scratch is not None:
            _from_scratch = from_scratch
            if isinstance(from_scratch, six.string_types):
                _from_scratch = from_scratch.lower()[0] == 't'

        # Standard output verbosity
        _v = 1
        if verbosity is not None:
            _v = int(verbosity)
            if _v <= 0:
                _v = 0
            elif _v >= 2:
                _v = 2
        _verbosity = _v

        # Clear any previous variables if `from_scratch`
        if _from_scratch:
            phonon_calc.pristine_supercell = None
            phonon_calc.perturbed_supercells = {}
            phonon_calc.supercell_calculations = {}

        # Get the pristine supercell structure using Phonopy
        # Phonopy is used here to maintain consistency with the rest of the
        # CSLD machinery (TODO: verify that Phonopy is required here)
        if not phonon_calc.pristine_supercell:
            phonon_calc.pristine_supercell = get_phonopy_style_supercell(
                    structure=input_structure,
                    supercell_matrix=_smatrix
            )
            phonon_calc.pristine_supercell.set_label('pristine_supercell')

        # Generate supercells with all atoms randomly perturbed
        if not phonon_calc.perturbed_supercells:
            _nad = len(phonon_calc.atomic_diplacements)
            for i in range(phonon_calc.n_supercells):
                atom_disp = phonon_calc.atomic_displacements[i % _nad]
                sc_label = 'cs_sc-{:04d}-{:02d}'.format(i, atom_disp)
                sc = phonon_calc.pristine_supercell.perturb_all_atoms(
                    in_place=False,
                    displacement=atom_disp*0.01
                )
                sc.set_label(sc_label)
                phonon_calc.perturbed_supercells[sc_label] = sc


        """TODO:
        1. Generate csld.ini; read from csld.ini
        2. Generate rattled supercells
        3. Generate paraphernalia: CONTROL, sc.txt, info, lat.in
        """


    def generate_csld_ini(self):
        pass

    def generate_perturbed_supercells(self):
        pass

    def add_supercells(self):
        pass

