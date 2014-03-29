# qmpy/materials/element

"""
Django models representing elements and species.
"""

from django.db import models

from qmpy.db.custom import DictField
from qmpy.utils import *

class Element(models.Model):
    """
    Core model for an element.

    Relationships:
      | :mod:`~qmpy.Atom` via atom_set
      | :mod:`~qmpy.Species` via species_set
      | :mod:`~qmpy.Structure` via structure_set
      | :mod:`~qmpy.Entry` via entry_set
      | :mod:`~qmpy.Composition` via composition_set
      | :mod:`~qmpy.Calculation` via calculation_set
      | :mod:`~qmpy.Potential` via potential_set
      | :mod:`~qmpy.Hubbard` via hubbards
      | :mod:`~qmpy.HubbardCorrection` via hubbardcorrection_set
      | :mod:`~qmpy.ReferenceEnergy` via referenceenergy_set

    Attributes:
      | **Identification**
      | z: atomic number
      | name: full atomic name
      | symbol: atomic symbol
      | group: group in the periodic table
      | period: period in the periodic table
      | 
      | **Physical properties**
      | mass: Atomic mass, in AMU (float)
      | density: Density at STP, in g/cm^3 (float)
      | volume: Atomic volume at STP, in A^3/atom (float)
      | atomic_radii: in A (float)
      | van_der_waals radii: in A (float)
      | covalent_radii: in A (float)
      | scattering_factors: A dictionary of scattering factor coeffs.
      | 
      | **Thermodynamic properties**
      | melt: melting point in K
      | boil: boiling point in K
      | specific_heat: C_p in J/K
      | 
      | **Electronic properties**
      | electronegativity: Pauling electronegativity
      | ion_energy: First ionization energy. (eV)
      | s_elec: # of s electrons
      | p_elec: # of p electrons
      | d_elec: # of d electrons
      | f_elec: # of f electrons
      |
      | **Additional information**
      | production: Annual tons of element produced.
      | abundance: Amount in earths crust (ppm)
      | radioactive: Are all isotopes unstable?
      | HHI_P: Herfindahl-Hirschman Index for production.
      | HHI_R: Herfindahl-Hirschman Index for reserve

    Note:
      HHI values from Gaultois, M. et al. Chem. Mater. 25, 2911-2920 (2013).

    """
    ### Identification
    z = models.IntegerField()
    name = models.CharField(max_length=20)
    symbol = models.CharField(max_length=9, primary_key=True)

    ### Periodic table
    group = models.IntegerField()
    period = models.IntegerField()

    ### Phyical characteristics
    mass = models.FloatField()
    density = models.FloatField()
    volume = models.FloatField()
    atomic_radii = models.IntegerField()
    van_der_waals_radii = models.IntegerField()
    covalent_radii = models.IntegerField()
    scattering_factors = DictField()

    ### Thermodynamics
    melt = models.FloatField()
    boil = models.FloatField()
    specific_heat = models.FloatField()

    ### Electonic structure
    electronegativity = models.FloatField()
    first_ionization_energy = models.FloatField()
    s_elec = models.IntegerField()
    p_elec = models.IntegerField()
    d_elec = models.IntegerField()
    f_elec = models.IntegerField()

    ### misc
    HHI_P = models.FloatField(default=0)
    HHI_R = models.FloatField(default=0)
    production = models.FloatField(default=0)
    radioactive = models.BooleanField(default=False)

    class Meta:
        app_label = 'qmpy'
        db_table = 'elements'

    # builtins
    def __str__(self):
        return self.symbol

    # accessor
    @classmethod
    def get(cls, value):
        """
        Return an element object. Accepts symbols and atomic numbers, or a list
        of symbols/atomic numbers.
        
        Examples::

            >>> Element.get('Fe')
            >>> Element.get(26)
            >>> Element.get(['Fe', 'O'])

        """
        if isinstance(value, cls):
            return value
        elif isinstance(value, list):
            return [ cls.get(v) for v in value ]
        elif isinstance(value, int):
            return cls.objects.get(z=value)
        elif isinstance(value, basestring):
            return cls.objects.get(symbol=value)

    # methods
    def species_distribution(self):
        counts = {}
        for s in self.species_set.all():
            counts[s.ox] = s.structure_set.count()
        return counts

class Species(models.Model):
    """
    Base model for an atomic species. (Element + charge state).

    Relationships:
      | :mod:`~qmpy.Element` via element
      | :mod:`~qmpy.Entry` via entry_set
      | :mod:`~qmpy.Structure` via structure_set

    Attributes:
      | name: Species name. e.g. Fe3+, O2-
      | ox: Oxidation state (float)

    """
    name = models.CharField(max_length=8, primary_key=True)
    element = models.ForeignKey(Element, blank=True, null=True)
    ox = models.FloatField(blank=True, null=True)

    class Meta:
        app_label = 'qmpy'
        db_table = 'species'

    # builtins
    def __str__(self):
        return str(self.name)

    # accessor
    @classmethod
    def get(cls, value):
        """
        Gets or creates the specified species.

        Arguments:
            value: 
                Accepts multiple input types. Can be a string, e.g. Fe3+
                or a tuple of (symbol, oxidation state) pairs, e.g. (Fe, 3).

        Return:
            A :mod:`~qmpy.Species` or list of :mod:`~qmpy.Species`.

        Examples::

            >>> Species.get('Fe3+')
            >>> Species.get('Fe3')
            >>> Species.get(('Fe', 3))
            >>> Species.get([ 'Fe3+', 'O2-', 'Li1+'])

        """
        if isinstance(value, cls):
            return value
        elif isinstance(value, basestring):
            spec, new = cls.objects.get_or_create(name=value)
            if new:
                elt, ox = parse_species(value)
                spec.element_id = elt
                spec.ox = ox
                spec.save()
            return spec
        elif isinstance(value, list):
            return [ cls.get(value) for value in list ]

    @property
    def ox_format(self):
        if self.ox is None:
            return 0
        elif is_integer(self.ox):
            return int(self.ox)
        else:
            return float(round(self.ox, 3))
        
