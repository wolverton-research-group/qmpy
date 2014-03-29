from django.db import models
import yaml
import os.path
import logging

import numpy as np

import qmpy
import qmpy.db.custom as custom
from qmpy.utils import *

logger = logging.getLogger(__name__)

#class Orbital(models.Model):
#    name = models.CharField(max_length=10)

#class EnergyLevel(models.Model):
#    dos = models.ForeignKey('DOS', related_name='energy_levels')
#    energy = models.FloatField(blank=True, null=True)
#    occupation = models.FloatField(blank=True, null=True)
#    orbital = models.ForiegnKey(Orbital)
#
#    class Meta:
#        db_table = 'states'
#        app_label = 'qmpy'
#        order_by = 'energy'

class DOS(models.Model):
    """
    Electronic density of states..

    Relationships:
        | :mod:`~qmpy.Entry` via entry
        | :mod:`~qmpy.MetaData` via meta_data
        | :mod:`~qmpy.Calculation` via calculation

    Attributes:
        | id
        | data: Numpy array of DOS occupations.
        | file: Source file.
        | gap: Band gap in eV.

    """

    meta_data = models.ManyToManyField('MetaData')
    entry = models.ForeignKey('Entry', null=True)
    efermi = models.FloatField(default=0.0)
    gap = models.FloatField(blank=True, null=True)
    data = custom.NumpyArrayField(blank=True, null=True)
    file = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'dos'
        app_label = 'qmpy'

    @classmethod
    def read(cls, doscar='DOSCAR', efermi=0.0):
        try:
            dos = DOS(file=os.path.abspath(doscar))
            dos._efermi = 0.0
            dos.read_doscar(dos.file)
            dos.efermi = efermi
        except ValueError:
            raise VaspError('Could not parse DOSCAR')
        return dos

    @property
    def efermi(self):
        return self._efermi

    @efermi.setter
    def efermi(self, efermi):
        """Set the Fermi level."""
        ef = efermi - self._efermi
        self._efermi = efermi
        try:
            self.data[0, :] = self.data[0, :] + ef
            self._site_dos[:, 0, :] = self._site_dos[:, 0, :] + ef
        except IndexError:
            pass

    @property
    def energy(self):
        """Return the array with the energies."""
        return self.data[0, :]

    def find_vbm(self, tol=1e-3):
        i = (np.abs(self.energy)).argmin()
        if self.energy[i] > 0:
            i -= 1
        edos = self.total_dos
        while edos[i] < tol:
            i -= 1
        else:
            self.vbm = self.energy[i]
        return self.vbm

    def find_cbm(self, tol=1e-3):
        i = (np.abs(self.energy)).argmin()
        if self.energy[i] < 0:
            i += 1
        edos = self.total_dos
        while edos[i] < tol:
            i += 1
        else:
            self.cbm = self.energy[i]
        return self.cbm

    def find_gap(self, tol=1e-3):
        i0 = (np.abs(self.energy)).argmin()
        i1 = ( i0-1 if self.energy[i0] > 0 else i0+1 )
        edos = self.total_dos
        if edos[i0] > tol and edos[i1] > tol:
            self.gap = 0
        else:
            self.gap = self.find_cbm(tol) - self.find_vbm(tol)
        return self.gap

    _plot = None
    @property
    def plot(self):
        if self._plot is None:
            line1 = Line(zip(self.energy, self.total_dos))
            line1.options['lines'] = {'fill': True}
            line2 = Line([[0,0], [0, max(self.total_dos)*1.1]])
            canvas = Renderer(lines=[line1, line2])
            canvas.yaxis.max = max(self.total_dos)*1.1
            canvas.yaxis.min = 0
            self._plot = canvas
        return self._plot

    def site_dos(self, atom, orbital):
        """Return an NDOSx1 array with dos for the chosen atom and orbital.

        atom: int
            Atom index
        orbital: int or str
            Which orbital to plot

        If the orbital is given as an integer:
        If spin-unpolarized calculation, no phase factors:
        s = 0, p = 1, d = 2
        Spin-polarized, no phase factors:
        s-up = 0, s-down = 1, p-up = 2, p-down = 3, d-up = 4, d-down = 5
        If phase factors have been calculated, orbitals are
        s, py, pz, px, dxy, dyz, dz2, dxz, dx2
        double in the above fashion if spin polarized.

        """
        # Integer indexing for orbitals starts from 1 in the _site_dos array
        # since the 0th column contains the energies
        if isinstance(orbital, int):
            return self._site_dos[atom, orbital + 1, :]
        n = self._site_dos.shape[1]
        if n == 4:
            norb = {'s':1, 'p':2, 'd':3}
        elif n == 7:
            norb = {'s+':1, 's-up':1, 's-':2, 's-down':2,
                    'p+':3, 'p-up':3, 'p-':4, 'p-down':4,
                    'd+':5, 'd-up':5, 'd-':6, 'd-down':6}
        elif n == 10:
            norb = {'s':1, 'py':2, 'pz':3, 'px':4,
                    'dxy':5, 'dyz':6, 'dz2':7, 'dxz':8,
                    'dx2':9}
        elif n == 19:
            norb = {'s+':1, 's-up':1, 's-':2, 's-down':2,
                    'py+':3, 'py-up':3, 'py-':4, 'py-down':4,
                    'pz+':5, 'pz-up':5, 'pz-':6, 'pz-down':6,
                    'px+':7, 'px-up':7, 'px-':8, 'px-down':8,
                    'dxy+':9, 'dxy-up':9, 'dxy-':10, 'dxy-down':10,
                    'dyz+':11, 'dyz-up':11, 'dyz-':12, 'dyz-down':12,
                    'dz2+':13, 'dz2-up':13, 'dz2-':14, 'dz2-down':14,
                    'dxz+':15, 'dxz-up':15, 'dxz-':16, 'dxz-down':16,
                    'dx2+':17, 'dx2-up':17, 'dx2-':18, 'dx2-down':18}
        return self._site_dos[atom, norb[orbital.lower()], :]

    @property
    def dos(self):
        if self.data.shape[0] == 3:
            return self.data[1, :]
        elif self.data.shape[0] == 5:
            return self.data[1:3, :]

    @property
    def total_dos(self):
        if self.data.shape[0] == 3:
            return self.data[1, :]
        elif self.data.shape[0] == 5:
            return np.sum(self.data[1:3, :], 0)

    @property
    def integrated_dos(self):
        if self.data.shape[0] == 3:
            return self.data[2, :]
        elif self.data.shape[0] == 5:
            return self.data[3:5, :]

    def read_doscar(self, fname="DOSCAR"):
        """Read a VASP DOSCAR file"""
        if os.path.getsize(fname) < 300:
            return
        f = open(fname)
        natoms = int(f.readline().split()[0])
        [f.readline() for nn in range(4)]  # Skip next 4 lines.
        # First we have a block with total and total integrated DOS
        ndos, efermi = f.readline().split()[2:4]
        self._efermi = float(efermi)
        ndos = int(ndos)
        dos = []
        for nd in xrange(ndos):
            dos.append(np.array([float(x) for x in f.readline().split()]))
        self.data = np.array(dos).T
        # Next we have one block per atom, if INCAR contains the stuff
        # necessary for generating site-projected DOS
        dos = []
        for na in xrange(natoms):
            line = f.readline()
            if line == '':
                # No site-projected DOS
                break
            ndos = int(line.split()[2])
            line = f.readline().split()
            cdos = np.empty((ndos, len(line)))
            cdos[0] = np.array(line)
            for nd in xrange(1, ndos):
                line = f.readline().split()
                cdos[nd] = np.array([float(x) for x in line])
            dos.append(cdos.T)
        self._site_dos = np.array(dos)
