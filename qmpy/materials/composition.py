# qmpy/materials/composition.py

from django.db import models
from django.db.models import F

from qmpy.materials.element import Element
from qmpy.data import elements
from qmpy.utils import *
import qmpy.analysis.thermodynamics as thermo

class Composition(models.Model):
    """
    Base class for a composition.

    Relationships:
        | :mod:`~qmpy.Calculation` via calculation_set
        | :mod:`~qmpy.Element` via element_set
        | :mod:`~qmpy.Entry` via entry_set
        | :mod:`~qmpy.ExptFormationEnergy` via exptformationenergy_set
        | :mod:`~qmpy.FormationEnergy` via formationenergy_set
        | :mod:`~qmpy.MetaData` via meta_data
        | :mod:`~qmpy.Structure` via structure_set
        | :mod:`~qmpy.Prototype` via prototype_set

    Attributes:
        | formula: Electronegativity sorted and normalized composition string.
        |   e.g. Fe2O3, LiFeO2
        | generic: Genericized composition string. e.g. A2B3, ABC2.
        | mass: Mass per atom in AMUs
        | meidema: Meidema model energy for the composition
        | ntypes: Number of elements. 

    """
    formula = models.CharField(primary_key=True, max_length=255)
    generic = models.CharField(max_length=255, blank=True, null=True)
    meta_data = models.ManyToManyField('MetaData')

    element_set = models.ManyToManyField('Element', null=True)
    ntypes = models.IntegerField(null=True)

    ### other stuff
    mass = models.FloatField(blank=True, null=True)

    ### thermodyanamic stuff
    meidema = models.FloatField(blank=True, null=True)
    structure = models.ForeignKey('Structure', blank=True,
            null=True,
            related_name='+')

    _unique = None
    _duplicates = None

    class Meta:
        app_label = 'qmpy'
        db_table = 'compositions'

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.compare(other)

    def compare(self, other, tol=1e-3):
        if self.space != other.space:
            return False
        for k in self.space:
            if abs(self.unit_comp[k] - other.unit_comp[k]) > tol:
                return False
        return True

    @classmethod
    def get(cls, composition):
        """
        Classmethod for getting Composition objects - if the Composition
        existsin the database, it is returned. If not, a new Composition is
        created.

        Examples::

            >>> Composition.get('Fe2O3')
            <Composition: Fe2O3>

        """
        if isinstance(composition, basestring):
            composition = parse_comp(composition)
        comp = reduce_comp(composition)
        f = ' '.join(['%s%g' % (k, comp[k]) for k in sorted(comp.keys())])
        comps = cls.objects.filter(formula=f)
        if comps.exists():
            return comps[0]
        else:
            comp = Composition(formula=f)
            comp.ntypes = len(comp.comp)
            comp.generic = format_generic_comp(comp.comp)
            comp.save()
            comp.element_set = comp.comp.keys()
            return comp

    @classmethod
    def get_list(cls, bounds, calculated=False, uncalculated=False):
        """
        Classmethod for finding all compositions within the space bounded by a
        sequence of compositions. 

        Examples::

            >>> from pprint import pprint
            >>> comps = Composition.get_list(['Fe','O'], calculated=True)
            >>> pprint(list(comps))
            [<Composition: Fe>,
             <Composition: FeO>,
             <Composition: FeO3>,
             <Composition: Fe2O3>,
             <Composition: Fe3O4>,
             <Composition: Fe4O5>,
             <Composition: O>]

        """
        space = set()
        if isinstance(bounds, basestring):
            bounds = bounds.split('-')
        if len(bounds) == 1:
            return [Composition.get(bounds[0])]
        for b in bounds:
            bound = parse_comp(b)
            space |= set(bound.keys())
        in_elts = Element.objects.filter(symbol__in=space)
        out_elts = Element.objects.exclude(symbol__in=space)
        comps = Composition.objects.filter(element_set__in=in_elts,
                ntypes__lte=len(space))
        comps = Composition.objects.exclude(element_set__in=out_elts)
        comps = comps.exclude(entry=None)
        if calculated:
            comps = comps.exclude(formationenergy=None)
        if uncalculated:
            comps = comps.filter(formationenergy=None)
        return comps.distinct()

    @property
    def entries(self):
        entries = self.entry_set.filter(id=F("duplicate_of__id"))
        if not entries.exists():
            return []
        return sorted(entries, key=lambda x:
                     100 if x.energy is None else x.energy )

    @property
    def ground_state(self):
        """Return the most stable entry at the composition."""
        e = self.entries
        if not e:
            return None
        return self.entries[0]

    _elements = None
    @property
    def elements(self):
        if self._elements is None:
            self._elements = list(self.element_set.all())
        return self._elements

    @elements.setter
    def elements(self, elements):
        self.element_set = elements
        self._elements = None

    @property
    def total_energy(self):
        calcs = self.calculation_set.filter(converged=True, 
                            label__in=['standard', 'static'])
        if not calcs.exists():
            return
        return min( c.energy_pa for c in calcs )


    @property
    def energy(self):
        calcs = self.calculation_set.filter(converged=True, 
                            label__in=['standard', 'static'])
        if not calcs.exists():
            return
        return min( c.formation_energy() for c in calcs )

    @property
    def delta_e(self):
        """Return the lowest formation energy."""
        formations = self.formationenergy_set.exclude(delta_e=None)
        formations = formations.filter(fit='standard')
        if not formations.exists():
            return
        return min(formations.values_list('delta_e', flat=True))

    @property
    def icsd_delta_e(self):
        """
        Return the lowest formation energy calculated from experimentally
        measured structures - i.e. excluding prototypes.
        """
        calcs = self.calculation_set.exclude(delta_e=None)
        calcs = calcs.filter(path__contains='icsd')
        if not calcs.exists():
            return
        return min(calcs.values_list('delta_e', flat=True))

    @property
    def ndistinct(self):
        """Return the number of distinct entries."""
        return len(self.entries)

    @property
    def comp(self):
        """Return an element:amount composition dictionary."""
        return parse_comp(self.formula)

    @property
    def unit_comp(self):
        """
        Return an element:amoutn composition dictionary normalized to a unit
        composition.
        """
        return unit_comp(self.comp)

    @property
    def name(self):
        return format_comp(reduce_comp(self.comp))

    @property
    def name_unreduced(self):
        return format_comp(self.comp)

    @property
    def latex(self):
        return format_latex(reduce_comp(self.comp))

    @property
    def html(self):
        return format_html(reduce_comp(self.comp))

    @property
    def space(self):
        """Return the set of element symbols"""
        return set(self.comp.keys())

    @property
    def experiment(self):
        """Return the lowest experimantally measured formation energy at the
        compositoin.
        """
        expts = self.exptformationenergy_set.filter(dft=False)
        if not expts.exists():
            return
        return min(expts.values_list('delta_e', flat=True))

    @property
    def relative_stability_plot(self):
        if not self.energy:
            return Renderer()
        ps = thermo.PhaseSpace(self.name)
        return ps.phase_diagram

    def get_mass(self):
        return sum([elements[k]['mass']*v for k, v in self.unit_comp.items() ])

    def get_similar(self):
        return Composition.objects.filter(generic=self.generic)

    def find_unique(self):
        unique = []
        #vih
        for e1 in self.entry_set.all():
            for i, e2 in enumerate(unique):
                if e1.structure == e2.structure:
                    ind = i
            else:
                unique.append(e1)
                continue

            exist = unique[ind]
            if e1.energy is None and e2.energy is None:
                e1.duplicate_of = exist.entry
            elif e2 is None:
                s1.entry.duplicate_of = exist.entry
            elif e1 is None:
                exist.entry.duplicate_of = s1.entry
                s1.entry.duplicate_of = None
                unique[ind] = s1
            elif e1 <= e2:
                s1.entry.duplicate_of = exist.entry
            else:
                exist.entry.duplicate_of = s1.entry
                s1.entry.duplicate_of = None
                unique[ind] = s1

        self.unique = dict([(s.entry, []) for s in unique ])
        for s in inputs:
            if not s.entry.duplicate_of is None:
                self.unique[s.entry.duplicate_of].append(s.entry)
