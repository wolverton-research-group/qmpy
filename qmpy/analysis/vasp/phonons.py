# qmpy/analysis/vasp/phonons.py

import os
from django.db import models

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

    def generate_pristine_supercell(self):
        pass

    def generate_csld_ini(self):
        pass

    def generate_supercells_with_displacements(self):
        pass

    def add_supercells(self):
        pass

