# qmpy/materials/atom.py

"""
The Atom and Site models represent a single atom or an atomic site,
repsectively. 

"""

from numpy.linalg import solve, norm
import time
import copy
from collections import defaultdict
import logging

from django.db import models
from django.db import transaction

import qmpy
from qmpy.utils import *
from qmpy.analysis.symmetry import WyckoffSite

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AtomError(qmpy.qmpyBaseError):
    pass

class SiteError(qmpy.qmpyBaseError):
    pass

class Atom(models.Model):
    """
    Model for an Atom.

    Relationships:
        | :mod:`~qmpy.Structure` via structure
        | :mod:`~qmpy.Element` via element
        | :mod:`~qmpy.Site` via site 
        | :mod:`~qmpy.WyckoffSite` via wyckoff

    Attributes:
        | id
        | x, y, z: Coordinate of the atom
        | fx, fy, fz: Forces on the atom
        | magmom: Magnetic moment on the atom (in &Mu;<sub>b</sub>)
        | occupancy: Occupation fraction (0-1).
        | ox: Oxidation state of the atom (can be different from charge)
        | charge: Charge on the atom
        | volume: Volume occupied by the atom

    """
    structure = models.ForeignKey('Structure', related_name='atom_set',
                                               null=True)
    site = models.ForeignKey('Site', related_name='atom_set', null=True)

    # species
    element = models.ForeignKey('Element', blank=True, null=True)
    ox = models.IntegerField(default=None, blank=True, null=True)

    # position
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()

    # forces
    fx = models.FloatField(blank=True, null=True)
    fy = models.FloatField(blank=True, null=True)
    fz = models.FloatField(blank=True, null=True)

    # properties
    magmom = models.FloatField(blank=True, null=True)
    charge = models.FloatField(blank=True, null=True)
    volume = models.FloatField(blank=True, null=True)

    # symmetry
    occupancy = models.FloatField(default=1)
    wyckoff = models.ForeignKey(WyckoffSite, blank=True, null=True)

    dist = None
    copy_of = None
    class Meta:
        app_label = 'qmpy'
        db_table = 'atoms'

    def __str__(self):
        return '%s @ %0.3g %0.3g %0.3g' % (self.element_id, 
                self.x, self.y, self.z)

    def __eq__(self, other):
        if self.element_id != other.element_id:
            return False
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)

    def __cmp__(self, other):
        comp_arr = [[ self.x, other.x ],
                    [ self.y, other.y ],
                    [ self.z, other.z ],
                    [ self.ox, other.ox ],
                    [ qmpy.elements[self.element_id]['z'], 
                      qmpy.elements[other.element_id]['z'] ]]
        comp_arr = np.array([ row for row in comp_arr if 
                                  all( not x is None for x in row ) ])
        comp_arr = np.array([ row for row in comp_arr if 
                                  not abs(row[0] - row[1]) < 1e-10 ]).T

        if len(comp_arr) == 0:
            raise AtomError

        if all(abs(comp_arr[0] - comp_arr[1]) < 1e-3):
            return 0
        ind = np.lexsort(comp_arr.T)
        return 2*ind[0] - 1

    @property
    def forces(self):
        """Forces on the Atom in [x, y, z] directions."""
        return np.array([self.fx , self.fy, self.fz])

    @forces.setter
    def forces(self, values):
        self.fx, self.fy, self.fz = values

    _coord = None
    @property
    def coord(self):
        """[x,y,z] coordinates."""
        if self._coord is None:
            self._coord = np.array([self.x, self.y, self.z], dtype='float64')
        return self._coord

    @coord.setter
    def coord(self, values):
        self.x, self.y, self.z = wrap(values)
        self._cart = None
        self._coord = None

    _cart = None
    @property
    def cart_coord(self):
        """Cartesian coordinates of the Atom."""
        if self._cart is None:
            if self.structure is None:
                raise AtomError("Cannot determine cartesian coordinate")
            self._cart = np.dot(self.coord, self.structure.cell)
        return self._cart

    @cart_coord.setter
    def cart_coord(self, value):
        if not self.structure is None:
            coords = self.structure.inv.T.dot(value)
            self.coord = wrap(coords)
        self._cart = value

    @property
    def species(self):
        """Formatted Species string. e.g. Fe3+, O2-"""
        return format_species(self.element_id, self.ox)

    @property
    def index(self):
        """
        None if not in a :mod:`~qmpy.Structure`, otherwise the index of the atom 
        in the structure.
        """
        if not self.structure: 
            return None
        return self.structure.atoms.index(self)

    @classmethod
    def create(cls, element, coord, **kwargs):
        """
        Creates a new Atom object. 

        Arguments:
            element (str or Element): Specifies the element of the Atom.
            coord (iterable of floats): Specifies the coordinate of the Atom.

        Keyword Arguments:
            forces: 
                Specifies the forces on the atom.
            magmom: 
                The magnitude of the magnetic moment on the atom.
            charge: 
                The charge on the Atom.
            volume: 
                The atomic volume of the atom (Angstroms^3).

        Examples::

            >>> Atom.create('Fe', [0,0,0])
            >>> Atom.create('Ni', [0.5, 0.5, 0.5], ox=2, magmom=5, 
            >>>                                 forces=[0.2, 0.2, 0.2],
            >>>                                 volume=101, charge=1.8,
            >>>                                 occupancy=1)

        """
        atom = Atom()
        atom.element_id = element
        atom.coord = coord
        valid_keys = ['ox', 'occupancy', 'wyckoff', 'charge', 
                'magmom', 'volume', 'forces']
        for key in valid_keys:
            if key in kwargs:
                setattr(atom, key, kwargs[key])
        return atom

    def copy(self):
        """
        Creates an exact copy of the atom, only without the matching primary
        key.

        Examples::

            >>> a = Atom.get('Fe', [0,0,0])
            >>> a.save()
            >>> a.id
            1
            >>> a.copy()
            >>> a
            <Atom: Fe - 0.000, 0.000, 0.000>
            >>> a.id
            None
        
        """
        atom = Atom()
        keys = ['ox', 'occupancy', 'charge', 
                'magmom', 'volume', 'forces',
                'coord', 'element_id']
        for key in keys:
            setattr(atom, key, getattr(self, key))
        atom.base_atom = self
        return atom

    def get_site(self, tol=1e-1):
        if not self.site is None:
            return self.site

        if not self.structure is None:
            for site in self.structure.sites:
                if self.is_on(site):
                    site.add_atom(self, tol=tol)
                    return site

        s = Site()
        s.structure = self.structure
        s.coord = self.coord
        s.atoms = [self]
        self.site = s
        return s

    _dist = None
    @property
    def dist(self):
        if self._dist is None:
            vec = np.dot(wrap(self.coord), self.structure.cell)
            self._dist = norm(vec)
        return self._dist

    def is_on(self, site, tol=1e-3):
        """
        Tests whether or not the ``Atom`` is on the specified ``Site``.

        Examples::

            >>> a = Atom.create('Fe', [0,0,0])
            >>> s = a.get_site()
            >>> a2 = Atom.create('Ni', [0,0,0])
            >>> a2.is_on(s)
            True

        """
        if self.dist - site.dist < tol:
            dist = self.structure.get_distance(self.coord, site.coord, 
                    limit=tol, wrap_self=True)
            if dist is None:
                return False
        else:
            return False
        return dist < tol

class Site(models.Model):
    """
    A lattice site. 

    A site can be occupied by one Atom, many Atoms or no Atoms. 

    Relationships:
        | :mod:`~qmpy.Structure` via structure
        | :mod:`~qmpy.Atom` via atom_set
        | :mod:`~qmpy.WyckoffSite` via wyckoff

    Attributes:
        | id
        | x, y, z: Coordinate of the Site

    """
    structure = models.ForeignKey('Structure', blank=True, null=True)
    wyckoff = models.ForeignKey(WyckoffSite, blank=True, null=True)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()

    class Meta:
        app_label = 'qmpy'
        db_table = 'sites'

    def __eq__(self, other):
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)

    def __str__(self):
        coord_str = ''
        comp_str = ''
        if not self.coord is None:
            coord_str = '%0.3g %0.3g %0.3g' % tuple(self.coord)

        if len(self.atoms) == 1:
            comp_str = self.atoms[0].element_id
        elif len(self.atoms) > 1:
            elts = [ str(a.element) for a in self.atoms ]
            specs = [ str(a.species) for a in self.atoms ]
            if ( len(set(elts)) == len(set(specs)) and 
                    len(set([ a.ox for a in self.atoms ])) == 1):
                comp_str = '('+','.join(elts)+')'
            else:
                comp_str = '('+','.join(specs)+')'

        if coord_str and comp_str:
            return "%s @ %s" % (comp_str, coord_str)
        elif coord_str:
            return 'Vac @ %s' % (coord_str)
        elif comp_str:
            return comp_str

    def __getitem__(self, i):
        return self.atoms[i]

    def __len__(self):
        return len(self.atoms)

    _dist = None
    @property
    def dist(self):
        if self._dist is None:
            vec = np.dot(wrap(self.coord), self.structure.cell)
            self._dist = norm(vec)
        return self._dist

    @transaction.atomic
    def save(self,*args, **kwargs):
        super(Site, self).save(*args, **kwargs)
        if not self._atoms is None:
            self.atom_set = self.atoms

    _atoms = None
    @property
    def atoms(self):
        """List of Atoms on the Site."""
        if self._atoms is None:
            if self.id is None:
                self._atoms = []
            else:
                self._atoms = list(self.atom_set.all())
        return self._atoms

    @atoms.setter
    def atoms(self, atoms):
        if isinstance(atoms, Atom):
            self._atoms = [atoms]
        elif all([ isinstance(a, Atom) for a in atoms ]):
            self._atoms = atoms
        else:
            raise TypeError('atoms must be a sequence of Atoms')

    @property
    def coord(self):
        """[Site.x, Site.y, Site.z]"""
        if any([ self.x is None, self.y is None, self.z is None]):
            return None
        return np.array([self.x, self.y, self.z], dtype='float64')

    @coord.setter
    def coord(self, coord):
        coord = wrap(coord)
        self.x, self.y, self.z = coord
        for a in self.atoms:
            a.coord = coord
        self._cart = None

    _cart = None
    @property
    def cart_coord(self):
        """Cartesian coordinates of the Atom."""
        if self.structure is None:
            raise AtomError("Cannot determine cartesian coordinate")
        if self._cart is None:
            self._cart =  np.dot(self.coord, self.structure.cell)
        return self._cart

    @cart_coord.setter
    def cart_coord(self, value):
        self._cart = value
        if self.structure:
            coord = self.structure.inv.T.dot(value)
            self.coord = wrap(coords)

    @property
    def label(self):
        """
        Assigns a human friendly label for the Site, based on its atomic
        composition. If singly occupied, returns the symbol of the atom on the
        site. If multiply occupied, returns a comma seperated string

        Examples::

            >>> a1 = Atom.create('Fe', [0,0,0], occupancy=0.2)
            >>> a2 = Atom.create('Ni', [0,0,0], occupancy=0.8)
            >>> s = Site.from_atoms([a1,a2])

        """
        if len(self.atoms) == 1:
            return self.atoms[0].element_id
        else:
            return format_comp(self.comp)

    @classmethod
    def from_atoms(cls, atoms, tol=1e-4):
        """
        Constructs a Site from an iterable of Atoms.

        Notes:
          Site.coord is set as the average coord of all assigned Atoms.

          Checks that the Atoms are close together. If the Atoms are further
          apart than `tol`, raises a SiteError

        Arguments:
          atoms (iterable of `Atom`): List of Atoms to occupy the Site.

        Keyword Arguments:
          tol (float): Atoms must be within `tol` of each other to be assigned 
          to the same Site. Defaults to 1e-4.

        Examples::

            >>> a1 = Atom.create('Fe', [0,0,0])
            >>> a2 = Atom.create('Ni', [1e-5, -1e-5, 0])
            >>> s = Site.from_atoms([a1,a1])

        """
        site = cls()
        if isinstance(atoms, Atom):
            site.coord = atoms.coord
            site.atoms = [atoms]
            return site

        site.coord = atoms[0].coord
        for a in atoms:
            site.add_atom(a, tol=tol)
        return site

    @staticmethod
    def create(coord, comp=None):
        """
        Constructs a Site from a coordinate.

        Note:
          The Site is created without any Atoms occupying it.

        Arguments:
          coord (length 3 iterable): Assigns the x, y, and z coordinates of 
            the Site.

        Keyword Arguments:
          comp (dict, string, or qmpy.Element): Composition dictionary.
           Flexible about input forms. Options include: <Element: Fe>, 'Fe',
           {"Fe":0.5, "Co":0.5}, and {<Element: Ni>:0.5, <Element: Co>:0.5}.

        Raises:
            TypeError: if `comp` isn't a string, ``Atom``, ``Element``.

        Examples::

            >>> s = Site.create([0.5,0.5,0.5])

        """
        site = Site()
        site.coord = coord
        if comp:
            if isinstance(comp, qmpy.Element):
                a = Atom.create(comp.symbol, coord)
                site.add_atom(a)
            elif isinstance(comp, str):
                a = Atom.create(comp, coord)
                site.add_atom(a)
            elif isinstance(comp, Atom):
                site.add_atom(comp)
            elif isinstance(comp, dict):
                for k,v in comp.items():
                    a = Atom.create(k, coord, occupancy=v)
            else:
                raise TypeError("Unknown datatype")
        return site

    def copy(self):
        new = Site()
        new.coord = self.coord
        new.atoms = [ atom.copy() for atom in self.atoms ]
        new.base_site = self
        return new

    @property
    def comp(self):
        """
        Composition dictionary of the Site.

        Returns:
          dict: of (element, occupancy) pairs. 
        
        Examples::

            >>> a1 = Atom('Fe', [0,0,0], occupancy=0.2)
            >>> a2 = Atom('Ni', [0,0,0], occupancy=0.8)
            >>> s = Site.from_atoms([a1,a2])
            >>> s.comp
            {'Fe':0.2, 'Ni':0.8}

        """
        comp = defaultdict(float)
        for a in self.atoms:
            comp[a.element_id] += a.occupancy
        return dict(comp)

    @comp.setter
    def comp(self, comp):
        atoms = []
        for k,v in comp.items():
            a = Atom.create(k, self.coord, occupancy=v)
            atoms.append(a)
        self.atoms = atoms

    @property
    def spec_comp(self):
        """
        Composition dictionary of the Site.

        Returns:
          dict: of (species, occupancy) pairs. 
        
        Examples::

            >>> a1 = Atom('Fe', [0,0,0], occupancy=0.2)
            >>> a2 = Atom('Ni', [0,0,0], occupancy=0.8)
            >>> s = Site.from_atoms([a1,a2])
            >>> s.comp
            {'Fe':0.2, 'Ni':0.8}

        """
        comp = defaultdict(float)
        for a in self.atoms:
            comp[a.species] += a.occupancy
        return dict(comp)

    def add_atom(self, atom, tol=None):
        """
        Adds Atom to `Site.atoms`. 

        Notes:
          If the Site being assigned to doens't have a coordinate, it is assigned
          the coordinate of `atom`.

        Arguments:
          atom (Atom): Atom to add to the structure.

        Keyword Arguments:
          tol (float): Distance between `atom` and the Site for the Atom to be 
            assigned to the Site. Raises a SiteError if the distance is 
            greater than `tol`. 

        Raises:
          SiteError: If `atom` is more than `tol` from the Site. 

        Examples::

            >>> s = Site.create([0,0,0])
            >>> a = Atom.create('Fe', [0,0,0])
            >>> s.add_atom(a)
            >>> s2 = Site()
            >>> s2.add_atom(a)

        """
        if not self.coord is None:
            if not tol is None:
                if self.structure.get_distance(self, atom, limit=2*tol) > tol:
                    raise SiteError("%s is too far from %s to add" % (atom, self))
                else:
                    if not atom in self.atoms:
                        self.atoms.append(atom)
        else:
            self.coord = atom.coord
            self.atoms = [atom]

    @property
    def magmom(self):
        """
        Calculates the composition weighted average magnetic moment of the atoms 
        on the Site.

        Returns:
          float or None
        """
        if self.atoms:
            mag = sum([ a.magmom*a.occupancy for a in self.atoms ])
            return mag/self.occupancy()

    @property
    def ox(self):
        """
        Calculates the composition weighted average oxidation state of the atoms 
        on the Site.

        Returns:
          float or None

        """
        if self.atoms:
            ox = sum([ a.ox*a.occupancy for a in self.atoms ])
            return ox/self.occupancy()

    @property
    def occupancy(self):
        """
        Calculates the total occupancy of the site.

        Returns:
          float or None
        """
        if self.atoms:
            return sum([ a.occupancy for a in self.atoms ])

    @property
    def partial(self):
        return any([ a.occupancy != 1.0 for a in self ])
