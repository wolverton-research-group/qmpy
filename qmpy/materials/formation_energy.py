# qmpy/materials/formation_energy.py

from django.db import models
from django.db.models import Min
import json
import pprint
import logging

from qmpy.db.custom import DictField
import qmpy.materials.composition as Comp
import qmpy.analysis as vasp
import qmpy.materials.element as elt
from qmpy.data import *
from qmpy.utils import *

logger = logging.getLogger(__name__)

class ExptFormationEnergy(models.Model):
    """Experimentally measured formation energy.

    Any external formation energy should be entered as an ExptFormationEnergy
    object, rather than a FormationEnergy. If the external source is also
    computational, set the "dft" attribute to be True.

    Relationships:
        | :mod:`~qmpy.Composition` via composition
        | :mod:`~qmpy.Fit` via fit

    Attributes:
        | id: integer primary key.
        | delta_e: measured formation energy.
        | delta_g: measured free energy of formation.
        | dft: (bool) True if the formation energy is from a non-OQMD DFT
        |   calculation.
        | source: (str) Identifier for the source.

    """
    composition = models.ForeignKey('Composition', null=True, blank=True)
    delta_e = models.FloatField(null=True)
    delta_g = models.FloatField(null=True)
    source = models.CharField(max_length=127, blank=True, null=True)
    dft = models.BooleanField(default=False)

    class Meta:
        app_label = 'qmpy'
        db_table = 'expt_formation_energies'

    def __str__(self):
        return '%s : %s' % (self.composition, self.delta_e)

    @classmethod
    def read_file(cls, filename, dft=False):
        source = filename.split('.')[0]
        expts = []
        for line in open(filename, 'r'):
            comp, energy = line.strip().split()
            expt, new = ExptFormationEnergy.objects.get_or_create(delta_e=energy,
                    composition=Comp.Composition.get(comp),
                    source=source, 
                    dft=dft)
            if new:
                expt.save()
            expts.append(expt)
        return expts

class HubbardCorrection(models.Model):
    """
    Energy correction for DFT+U energies.

    Relationships:
        | :mod:`~qmpy.Fit` via fit
        | :mod:`~qmpy.Element` via element
        | :mod:`~qmpy.Hubbard` via hubbard

    Attributes:
        | id
        | value: Correction energy (eV/atom)

    """
    element = models.ForeignKey('Element')
    hubbard = models.ForeignKey('Hubbard')
    value = models.FloatField()
    fit = models.ForeignKey('Fit', blank=True, null=True,
                                   related_name='hubbard_correction_set')

    class Meta:
        app_label = 'qmpy'
        db_table = 'hubbard_corrections'

class ReferenceEnergy(models.Model):
    """
    Elemental reference energy for evaluating heats of formation.

    Relationships:
        | :mod:`~qmpy.Fit` via fit
        | :mod:`~qmpy.Element` via element

    Attributes:
        | id
        | value: Reference energy (eV/atom)


    """
    element = models.ForeignKey('Element')
    value = models.FloatField()
    fit = models.ForeignKey('Fit', blank=True, null=True,
                                   related_name='reference_energy_set')

    class Meta:
        app_label = 'qmpy'
        db_table = 'reference_energies'

class FormationEnergy(models.Model):
    """
    Base class for a formation energy.

    Relationships:
        | :mod:`~qmpy.Calculation` via calculation
        | :mod:`~qmpy.Composition` via composition
        | :mod:`~qmpy.Entry` via entry
        | :mod:`~qmpy.FormationEnergy` via equilibrium
        | :mod:`~qmpy.Fit` via fit

    Attributes:
        | id
        | delta_e: Formation energy (eV/atom)
        | description: A label of the source of the formation energy.
        | stability: Distance from the convex hull (eV/atom)

    """
    composition = models.ForeignKey('Composition', null=True, blank=True)
    entry = models.ForeignKey('Entry', null=True, blank=True)
    calculation = models.ForeignKey('Calculation', null=True, blank=True)
    description = models.CharField(max_length=20, null=True, blank=True)
    fit = models.ForeignKey('Fit', null=True)

    stability = models.FloatField(blank=True, null=True)
    delta_e = models.FloatField(null=True)

    equilibrium = models.ManyToManyField('self', blank=True, null=True)

    class Meta:
        app_label = 'qmpy'
        db_table = 'formation_energies'

    @classmethod
    def get(cls, calculation, fit='standard'):
        fit = Fit.get(fit)
        try:
            return FormationEnergy.objects.get(calculation=calculation, fit=fit)
        except FormationEnergy.DoesNotExist:
            return FormationEnergy(calculation=calculation, fit=fit)

    @staticmethod
    def search(bounds, fit='standard'):
        space = set()
        if isinstance(bounds, basestring):
            bounds = bounds.split('-')
        for b in bounds:
            bound = parse_comp(b)
            space |= set(bound.keys())
        in_elts = elt.Element.objects.filter(symbol__in=space)
        out_elts = elt.Element.objects.exclude(symbol__in=space)
        forms = FormationEnergy.objects.filter(fit=fit)
        forms = forms.exclude(composition__element_set__in=out_elts)
        forms = forms.filter(composition__element_set__in=in_elts)
        forms = forms.filter(composition__ntypes__lte=len(space))
        return forms.distinct()

    def __str__(self):
        return '%s : %s' % (self.composition, self.delta_e)

    def save(self, *args, **kwargs):
        self.composition = self.calculation.composition
        self.entry = self.calculation.entry
        super(FormationEnergy, self).save(*args, **kwargs)

Formation = FormationEnergy

class Fit(models.Model):
    """
    The core model for a reference energy fitting scheme. 
    
    The Fit model links to the experimental data (ExptFormationEnergy objects) 
    that informed the fit, as well as the DFT calculations (Calculation objects) 
    that were matched to each experimental formation energy. Once the fit is 
    completed, it also stores a list of chemical potentials both as a 
    relationship to ReferenceEnergy and HubbardCorrection objects. 
    These correction energies can also be accessed by dictionaries at 
    Fit.mus and Fit.hubbard_mus.

    Relationships:
        | :mod:`~qmpy.Calculation` via dft
        | :mod:`~qmpy.ExptFormationEnergy` via experiments
        | :mod:`~qmpy.FormationEnergy` via formationenergy_set
        | :mod:`~qmpy.HubbardCorrection` via hubbard_correction_set
        | :mod:`~qmpy.ReferenceEnergy` via reference_energy_set

    Attributes:
        | name: Name for the fitting
    
    Examples::

        >>> f = Fit.get('standard')
        >>> f.experiments.count()
        >>> f.dft.count()
        >>> f.mus
        >>> f.hubbard_mus

    """
    name = models.CharField(max_length=255, primary_key=True)
    elements = models.ManyToManyField('Element')
    experiments = models.ManyToManyField('ExptFormationEnergy') 
    dft = models.ManyToManyField('Calculation')

    class Meta:
        app_label = 'qmpy'
        db_table = 'fits'

    @classmethod
    def get(cls, name):
        try:
            return Fit.objects.get(name=name)
        except Fit.DoesNotExist:
            return Fit(name=name)

    @property
    def mus(self):
        mus = self.reference_energy_set.values_list('element_id', 'value')
        return dict(mus)

    @property
    def hubbard_mus(self):
        hm = self.hubbard_correction_set.all()
        return dict((h.hubbard.key, h.value) for h in hm)
