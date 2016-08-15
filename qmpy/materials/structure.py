# qmpy/materials/structure.py

"""
The Structure class is used to represent a crystal structure.

"""

import numpy as np
import numpy.linalg as la
import time
import copy
import pprint
import random
from collections import defaultdict
import logging

from django.db import models
from django.db import transaction

import qmpy
from qmpy.utils import *
from element import Element, Species
from atom import Atom, Site
from composition import Composition
from qmpy.utils import *
from qmpy.data.meta_data import *
from qmpy.analysis.symmetry import *
from qmpy.analysis import *

logger = logging.getLogger(__name__)

#logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)

class StructureError(Exception):
    """Structure related problem"""

@add_meta_data('comment')
@add_meta_data('keyword')
class Structure(models.Model, object):
    """
    Structure model. Principal attributes are a lattice and basis set.

    Relationships:
        | :mod:`~qmpy.Entry` via entry
        | :mod:`~qmpy.Atom` via atom_set: Atoms in the structure. More commonly
        |   handled by the managed attributed `atoms`.
        | :mod:`~qmpy.Calculation` via calculated. Calculation objects
        |   that the structure is an *output* from.
        | :mod:`~qmpy.Calculation` via calculation_set. Returns calculation
        |   objects that the structure is an *input* to.
        | :mod:`~qmpy.Composition` via composition.
        | :mod:`~qmpy.Element` via element_set
        | :mod:`~qmpy.Spacegroup` via spacegroup
        | :mod:`~qmpy.Species` via species_set
        | :mod:`~qmpy.Prototype` via prototype. If the structure belongs to a
        |   prototypical structure, it is referred to here.
        | :mod:`~qmpy.Reference` Original literature reference.
        | :mod:`~qmpy.MetaData` via meta_data

    Attributes:
        | **Identification**
        | id
        | label: key in the Entry.structures dictionary.
        | natoms: Number of atoms.
        | nsites: Number of sites.
        | ntypes: Number of elements.
        | measured: Experimentally measured structure?
        | source: Name for source.
        | 
        | **Lattice**
        | x1, x2, x3
        | y1, y2, y3
        | z1, z2, z3: Lattice vectors of the cell. Accessed via `cell`.
        | volume
        | volume_pa
        |
        | **Calculated properties**
        | delta_e: Formation energy (eV/atom)
        | meta_stability: Distance from the convex hull (eV/atom)
        | energy: Total DFT energy (eV/FU)
        | energy_pa: Total DFT energy (eV/atom)
        | magmom: Total magnetic moment (&Mu;<sub>b</sub>)
        | magmom_pa: Magnetic moment per atom.
        | sxx, sxy, syy
        | syx, szx, szz: Stresses on the cell. Accessed via `stresses`.

    Examples::
        
        >>> s = io.read(INSTALL_PATH+'/io/files/POSCAR_FCC')
        >>> s.atoms
        >>> s.cell
        >>> s.magmoms
        >>> s.forces
        >>> s.stresses

    """
    entry = models.ForeignKey('Entry', null=True)
    element_set = models.ManyToManyField('Element')
    species_set = models.ManyToManyField('Species')
    meta_data = models.ManyToManyField('MetaData')
    reference = models.ForeignKey('Reference', null=True)
    label = models.CharField(blank=True, max_length=63)
    prototype = models.ForeignKey('Prototype', null=True, blank=True,
                                               related_name='+')
    measured = models.BooleanField(default=False)

    composition = models.ForeignKey('Composition', null=True, 
                                    related_name='structure_set')
    natoms = models.IntegerField(null=True, blank=True)
    nsites = models.IntegerField(null=True, blank=True)
    ntypes = models.IntegerField(null=True, blank=True)

    x1 = models.FloatField()
    x2 = models.FloatField()
    x3 = models.FloatField()
    y1 = models.FloatField()
    y2 = models.FloatField()
    y3 = models.FloatField()
    z1 = models.FloatField()
    z2 = models.FloatField()
    z3 = models.FloatField()

    volume = models.FloatField(blank=True, null=True)
    volume_pa = models.FloatField(blank=True, null=True)

    sxx = models.FloatField(default=0)
    syy = models.FloatField(default=0)
    szz = models.FloatField(default=0)
    sxy = models.FloatField(default=0)
    syz = models.FloatField(default=0)
    szx = models.FloatField(default=0)

    spacegroup = models.ForeignKey('Spacegroup', blank=True,
            null=True)

    energy = models.FloatField(blank=True, null=True)
    energy_pa = models.FloatField(blank=True, null=True)
    magmom = models.FloatField(blank=True, null=True)
    magmom_pa = models.FloatField(blank=True, null=True)
    delta_e = models.FloatField(blank=True, null=True)
    meta_stability = models.FloatField(blank=True, null=True)

    _reciprocal_lattice = None
    _distinct_atoms = []
    _magmoms = []

    class Meta:
        app_label = 'qmpy'
        db_table = 'structures'
        unique_together = ('entry', 'label')

    def __eq__(self, other):
        return self.compare(other)

    def __str__(self):
        return format_comp(reduce_comp(self.comp))

    def printf(self):
        res = format_comp(reduce_comp(self.comp)) + '\n'
        res += self.lat_param_string()
        for i, s in enumerate(self.sites):
            res += '\n - %s' % s
            if i == 6:
                res += '\n ... \n %d more atoms.' % (len(self)-6)
                break
        return res

    def __getitem__(self, i):
        return self.atoms[i]

    def __len__(self):
        return len(self.atoms)

    @staticmethod
    def create(cell, atoms=[], **kwargs):
        """
        Creates a new Structure.

        Arguments:
            cell: 3x3 lattice vector array

        Keyword Arguments:
            atoms: List of ``Atom`` creation arguments. Can be a list of 
            [element, coord], or a list of [element, coord, kwargs].

        Examples::

            >>> a = 3.54
            >>> cell = [[a,0,0],[0,a,0],[0,0,a]]
            >>> atoms = [('Cu', [0,0,0]),
                         ('Cu', [0.5, 0.5, 0.5])]
            >>> s = Structure.create(cell, atoms)
            >>> atoms = [('Cu', [0,0,0], {'magmom':3}),
                    ('Cu', [0.5, 0.5, 0.5], {'magmom':-3})]
            >>> s2 = Structure.create(cell, atoms)

        """
        s = Structure(**kwargs)
        if np.shape(cell) == (6,):
            s.lat_params = cell
        elif np.shape(cell) == (3,3):
            s.cell = cell
        elif np.shape(cell) == (3,):
            s.cell = np.eye(3)*cell

        for atom in atoms:
            if len(atom) == 2:
                atom = Atom.create(*atom)
            elif len(atom) == 3:
                atom = Atom.create(atom[0], atom[1], **atom[2])
            s.add_atom(atom)

        if s.comp:
            s.composition = Composition.get(s.comp)

        return s

    @transaction.atomic
    def save(self,*args, **kwargs):
        if not self.composition:
            self.composition = Composition.get(self.comp)

        if not self.spacegroup:
            self.symmetrize()

        self.natoms = len(self.atoms)
        self.nsites = len(self.sites)
        self.ntypes = len(self.comp.keys())
        self.get_volume()
        super(Structure, self).save(*args, **kwargs)
        if not self._atoms is None:
            self.atom_set = self.atoms
        if not self._sites is None:
            self.site_set = self.sites
        self.element_set = self.elements
        self.species_set = self.species
        self.meta_data = self.comment_objects + self.keyword_objects

    _atoms = None
    @property
    def atoms(self):
        """
        List of ``Atoms`` in the structure. 
        """
        if self._atoms is None:
            if not self.id:
                self._atoms = []
            else:
                self._atoms = list(self.atom_set.all())
                self._sites = list(self.site_set.all())
        return self._atoms

    @atoms.setter
    def atoms(self, atoms):
        self._atoms =  []# list(atoms)
        self._sites = []
        for a in atoms:
            self.add_atom(a)
        self.natoms = len(self._atoms)
        self.ntypes = len(self.comp)

    _abc = None
    @property
    def atoms_by_coord(self):
        if self._abc is None:
            _abc = {}
            for a in self.atoms:
                _abc[tuple(a.cart_coord.tolist())] = a
            self._abc = _abc
        return self._abc

    _sbc = None
    @property
    def sites_by_coord(self):
        if self._sbc is None:
            _sbc = {}
            for s in self.sites:
                _sbc[tuple(s.cart_coord.tolist())] = s
            self._sbc = _sbc
        return self._sbc

    _sites = None
    @property
    def sites(self):
        """
        List of ``Sites`` in the structure.
        """
        if self._sites is None:
            self.atoms
            self.get_sites()
            self.nsites = len(self.sites)
        return self._sites

    @sites.setter
    def sites(self, sites):
        self._atoms = []
        for s in sites:
            self.add_site(s)
        self._sites = sites
        self.natoms = len(self.atoms)
        self.ntypes = len(self.comp)

    @property
    def site_compositions(self):
        return [ format_comp(s.comp) for s in self.sites ]

    @site_compositions.setter
    def site_compositions(self, values):
        atoms = []
        for s, v in zip(self.sites, values):
            s.comp = parse_comp(v)
            atoms += s.atoms
        self._atoms = atoms
        self.natoms = len(atoms)

    @property
    def elements(self):
        """List of Elements"""
        return [ Element.get(e) for e in self.comp.keys() ]

    @property
    def species(self):
        """List of species"""
        return [ Species.get(s) for s in self.spec_comp.keys() ]

    @property
    def stresses(self):
        """Calculated stresses, a numpy.ndarray of shape (6,)"""
        return np.array([self.sxx, self.syy, self.szz,
            self.sxy, self.syz, self.szx ])
        
    @stresses.setter
    def stresses(self, vector):
        self.sxx, self.syy, self.szz = vector[0:3]
        self.sxy, self.syz, self.szx = vector[3:6]

    def get_volume(self):
        """Calculates the volume from the triple product of self.cell"""
        b1, b2, b3 = self.cell
        self.volume = abs(np.dot(np.cross(b1, b2), b3))
        self.volume_pa = self.volume/len(self)
        return self.volume

    def set_label(self, label):
        self.label = label
        if not self.entry is None:
            self.entry.structures[label] = self
        #if self.id:
        #    Structure.objects.filter(id=self.id).update(label=label)

    def set_volume(self, value):
        """
        Rescales the unit cell to the specified volume, keeping the direction
        and relative magnitudes of all lattice vectors the same.
        """
        self.get_volume()
        scale = value/self.volume
        self.cell = self.cell * (scale**(1/3.))
        self.volume_pa = value/self.natoms
        self.volume = value

    def set_volume_to_sum_of_elements(self):
        volume = 0
        for atom in self:
            volume += atom.element.volume*atom.occupancy
        self.set_volume(volume)

    @property
    def lat_param_dict(self):
        """Dictionary of lattice parameters."""
        return dict(zip( ['a', 'b', 'c', 'alpha', 'beta', 'gamma'], 
                         self.lat_params))

    _lat_params = None
    @property
    def lat_params(self):
        """Tuple of lattice parameters (a, b, c, alpha, beta, gamma)."""
        if self._lat_params is None:
            self._lat_params = basis_to_latparams(self.cell)
        return self._lat_params

    @lat_params.setter
    def lat_params(self, lat_params):
        self.cell = latparams_to_basis(lat_params)
        self._lat_params = lat_params

    def lat_param_string(self, format='screen'):
        """
        Generates a human friendly representation of the lattice parameters of
        a structure.

        Keyword Arguments:
            format: ('screen'|'html'|'mathtype')

        """
        formats = {
                'html':{
                    'keys':['&alpha;', '&beta;', '&gamma'],
                    'newline':'<br>'},
                'mathtype':{
                    'keys':[r'\alpha', r'\beta', r'\gamma'],
                    'newline':'\n'},
                'screen':{
                    'keys':[r'alpha', r'beta', r'gamma'],
                    'newline':'\n'}
                }

        f = formats[format]

        lp = self.lat_param_dict
        if abs(lp['a'] - lp['b']) < 1e-4:
            if abs(lp['a'] - lp['c']) < 1e-4:
                lpstr = 'a = b = c = %0.3g' % lp['a']
            else:
                lpstr = 'a = b = %0.3g, c = %0.3g' % ( lp['a'], lp['c'])
        else:
            lpstr = 'a = %0.3g, b = %0.3g, c = %0.3g' % (lp['a'], lp['b'], lp['c'])

        lpstr += f['newline']

        if abs(lp['alpha'] - lp['beta']) < 1e-2:
            if abs(lp['alpha'] - lp['gamma']) < 1e-2:
                lpstr += '%s = %s = %s = %0.3g' % (
                    f['keys'][0], f['keys'][1], f['keys'][2], lp['alpha'])
            else:
                lpstr += '%s = %s = %0.3g, %s = %0.3g' % (
                    f['keys'][0], f['keys'][1], lp['alpha'], 
                    f['keys'][2], lp['gamma'])
        else:
            lpstr += '&alpha; = %0.3g, &beta; = %0.3g, &gamma; = %0.3g' % (
                f['keys'][0], lp['alpha'],  
                f['keys'][1], lp['beta'],
                f['keys'][2], lp['gamma'])
        return lpstr

    lp = lat_params
    _cell = None
    @property
    def cell(self):
        """Lattice vectors, 3x3 numpy.ndarray."""
        if self._cell is None:
            self._cell = np.array([
                            [self.x1, self.x2, self.x3],
                            [self.y1, self.y2, self.y3],
                            [self.z1, self.z2, self.z3]])
        return self._cell

    @cell.setter
    def cell(self, cell):
        self.x1, self.x2, self.x3 = cell[0]
        self.y1, self.y2, self.y3 = cell[1]
        self.z1, self.z2, self.z3 = cell[2]
        self._lat_params = None
        self._inv = None
        self._metrical_matrix = None
        for a in self.atoms:
            a._cart = None
        for s in self.sites:
            s._cart = None
        self._cell = None

    _metrical_matrix = None
    @property
    def metrical_matrix(self):
        """np.dot(self.cell.T, self.cell)"""
        if self._metrical_matrix is None:
            self._metrical_matrix = self.cell.dot(self.cell.T)
        return self._metrical_matrix

    @metrical_matrix.setter
    def metrical_matrix(self, G):
        a = np.sqrt(abs(G[0,0]))
        b = np.sqrt(abs(G[1,1]))
        c = np.sqrt(abs(G[2,2]))
        al = np.arccos(G[1,2]/abs(b*c))*180/np.pi
        be = np.arccos(G[0,2]/abs(a*c))*180/np.pi
        ga = np.arccos(G[0,1]/abs(a*b))*180/np.pi
        self.cell = latparams_to_basis([a, b, c, al, be, ga])

    @property
    def atomic_numbers(self):
        """List of atomic numbers, length equal to number of atoms."""
        return np.array([ atom.element.z for atom in self.atoms ])

    @property
    def atom_types(self):
        """List of atomic symbols, length equal to number of atoms."""
        return np.array([ atom.element_id for atom in self.atoms ])

    @atom_types.setter
    def atom_types(self, elements):
        if isinstance(elements, list):
            for a, e in zip(self.atoms, elements):
                a.element_id = e
        elif isinstance(elements, basestring):
            for a in self.atoms:
                a.element_id = elements
        elif isinstance(elements, qmpy.Element):
            for a in self.atoms:
                a.element = elements
        else:
            raise ValueError('Unrecognized type for atom type assignment')

    @property
    def species_types(self):
        """List of species, length equal to number of atoms."""
        return np.array([ atom.species_id for atom in self.atoms ])

    def symmetrize(self, tol=1e-3, angle_tol=-1):
        """
        Analyze the symmetry of the structure. Uses spglib to find the
        symmetry. 

        symmetrize sets:
         * spacegroup -> Spacegroup
         * uniq_sites -> list of unique Sites
         * orbits -> lists of equivalent Atoms
         * rotations -> List of rotation operations
         * translations -> List of translation operations
         * operatiosn -> List of (rotation,translation) pairs
         * for each atom: atom.wyckoff -> WyckoffSite
         * for each site: site.multiplicity -> int

        """
        self.get_sites()
        dataset = get_symmetry_dataset(self, symprec=tol)
        self.spacegroup = Spacegroup.objects.get(pk=dataset['number'])
        for i, site in enumerate(self.sites):    
            site.wyckoff = self.spacegroup.get_site(dataset['wyckoffs'][i])
            site.structure = self
        counts = defaultdict(int)
        orbits = defaultdict(list)
        origins = {}
        for i, e in enumerate(dataset['equivalent_atoms']):
            counts[e] += 1
            origins[self.sites[i]] = self.sites[e]
            orbits[e].append(self.sites[i])
        self.origins = origins
        self.operations = zip(dataset['rotations'], dataset['translations'])
        rots = []
        for r in dataset['rotations']:
            if not any([ np.allclose(r, x) for x in rots ]):
                rots.append(r)
        self.rotations = rots
        trans = []
        for t in dataset['translations']:
            if not any([ np.allclose(t, x) for x in trans ]):
                trans.append(t)
        self.translations = trans
        self.orbits = orbits.values()
        self.duplicates = dict((self.sites[e], v) for e, v in orbits.items())
        self._uniq_sites = []
        self._uniq_atoms = []
        for ind, mult in counts.items():
            site = self.sites[ind]
            for site2 in self.duplicates[site]:
                site2.multiplicity = mult
            site.index = ind
            site.multiplicity = mult
            self._uniq_sites.append(site)
            for a in site:
                self._uniq_atoms.append(a)

    _uniq_atoms = None
    @property
    def uniq_atoms(self):
        if self._uniq_atoms is None:
            self.symmetrize()
        return self._uniq_atoms

    _uniq_sites = None
    @property
    def uniq_sites(self):
        if self._uniq_sites is None:
            self.symmetrize()
        return self._uniq_sites

    def pdf_compare(self, other, tol=1e-2):
        """
        Compute the PDF for each structure and evaluate the overlap integral
        for all pairs of species.
        """

        elts = list(set([a.element_id for a in self ])) 
        dists = get_pair_distances(self)
        odists = get_pair_distances(other)
        for e1, e2 in itertools.combinations(elts,2):
            d1 = dists[frozenset([e1,e2])]
            d2 = odists[frozenset([e1,e2])]
            for x, y in zip(d1, d2):
                if abs(x-y) > tol:
                    return False
        return True

    def compare(self, other, tol=0.01,
                             atom_tol=10,
                             volume=False, 
                             allow_distortions=False, 
                             check_spacegroup=False,
                             wildcard=None):
        """
        Credit to K. Michel for the algorithm.

        1. Check that elements are the same in both structures

        2. Convert both structures to primitive form

        3. Check that the total number of atoms in primitive cells are the same

        4. Check that the number of atoms of each element are the same in
        primitive cells

        4b. Check that the spacegroup is the same.

        5. If needed check that the primitive cell volumes are the same

        6. Convert both primitive cells to reduced form There is one issue here - 
        the reduce cell could be type I (all angles acute) or type II (all angles 
        obtuse) and a slight difference in the initial cells could cause two 
        structures to reduce to different types. So at this step, if the angles 
        are not correct, the second cell is transformed as 
        [[-1, 0, 0], [0, -1, 0], [0, 0, 1]].

        7. Check that the cell internal angles are the same in both reduced
        cells. 

        8. Check that the ratios of reduced cell basis lengths are the same. ie
        a1/b1 = a2/b2, a1/c1 = a2/c2, and b1/c1 = b2/c2 where a1, b1, c1, are
        the lengths of basis vectors in cell 1 and a2, b2, c2 are the lengths
        of cell 2.

        9. Get the lattice symmetry of the reduced cell 2 (this is a list of
        all rotations that leave the lattice itself unchanged). In turn, apply
        all rotations to reduced cell 2 and for each search for a vector that
        overlaps rotated cell positions with positions in reduced cell 1. If a
        rotation + translation overlaps reduced cells, then they are the same.

        MODIFICATIONS:
        Only need one "base" atom from the first structure
        Get the distance from the origin for every atom first

        Arguments:
            other: Another ``Structure``.

        Keyword Arguments:
            tol: Percent deviation in lattice parameters and angles.

            Not Implemented Yet:
            wildcard: Elements of the specified type can match with any atom.

        """

        # 1
        #if len(self) > 80 or len(other) > 80:
        #    return False
        me = self.copy()
        you = other.copy()

        if not set(me.elements) == set(you.elements):
            logger.debug("Structure comparison: element mismatch")
            return False

        # 2
        me.make_primitive()
        you.make_primitive()

        # 3
        if not me.natoms == you.natoms:
            logger.debug("Structure comparison: natom mismatch")
            return False

        # 4
        if not Composition.get(me.comp) == Composition.get(you.comp):
            logger.debug("Structure comparison: composition mismatch")
            return False

        # 5 (optional)
        if volume:
            v1, v2 = me.get_volume(), you.get_volume()
            if abs(v1 - v2)/min(v1, v2) > tol:
                logger.debug("Structure comparison: volume mismatch")
                return False

        # 6
        me.reduce()
        you.reduce()

        #6b
        if check_spacegroup:
            me.symmetrize()
            you.symmetrize()
            if me.spacegroup != you.spacegroup:
                return False

        # 7
        try_again = False
        for a, b in zip(me.lat_params[3:], you.lat_params[3:]):
            if abs((a-b)/min(a,b)) > tol:
                you.transform([1,-1,-1])
                logger.debug('Tranforming other from type II to type I.')
                try_again = True

        if try_again:
            try_again = False
            for a, b in zip(me.lat_params[3:], you.lat_params[3:]):
                if abs((a-b)/min(a,b)) > tol:
                    you.transform([-1,-1,1])
                    logger.debug('Tranforming other from type II to type I.')
                    try_again = True

        if try_again:
            try_again = False
            for a, b in zip(me.lat_params[3:], you.lat_params[3:]):
                if abs((a-b)/min(a,b)) > tol:
                    logger.debug("Structure comparison: lat param mismatch")
                    return False

        # 8
        if not allow_distortions:
            ratios = [ x/y for x,y in zip(me.lp[:3], you.lp[:3])]
            for a,b in itertools.combinations(ratios, r=2):
                if abs(a-b)/min(a,b) > tol:
                    logger.debug("Structure comparison: lattice vector ratio mismatch")
                    return False

        # 9
        min_elt = sorted(me.comp, key=lambda x: me.comp[x])[0]
        test_atom = [ a for a in me.atoms if a.element_id == min_elt ][0]
        me.coords -= test_atom.coord
        
        # get all rotational symmetries of the lattice
        test_struct = Structure()
        test_struct.cell = me.cell
        test_struct.atoms = [Atom.create('Fe', [0,0,0])]
        test_struct.symmetrize()
        rotations = test_struct.rotations

        test_struct = you.copy()

        eps = 2*tol*atom_tol#*me.volume**(1./3)
        eps2 = eps**2

        for rot in rotations:
            # loop over all possible re-orientations of the cell
            inv = la.inv(rot)
            test_struct.cell = rot.dot(you.cell)
            test_struct.coords = np.array([ inv.dot(c) for c in you.coords ])
            for i, atom in enumerate(you.atoms):
                # loop over atoms
                if atom.element_id != min_elt:
                    continue

                test_struct.coords -= test_struct[i].coord
                # check if all sites have a match
                match = True
                matches = []
                vecs = []
                for atom2 in test_struct:
                    best = 1000
                    id = None
                    vec = None
                    for j, atom3 in enumerate(me):
                        if j in matches:
                            continue
                        if atom2.element_id != atom3.element_id:
                            continue
                        d = me._get_vector(atom2, atom3)
                        if any([ abs(dd) > eps for dd in d ]):
                            continue
                        d2 = d.dot(d)
                        if d2 > eps2:
                            continue

                        # matching case
                        if d2 < best:
                            best = d2
                            id = j
                            vec = d

                    if id is None:
                        match = False
                        break
                    matches.append(id)
                    vecs.append(vec)

                if match == False:
                    continue
                vecs = np.array(vecs)
                err = np.average(vecs, 0)
                vecs -= err
                if all([ d.dot(d)**0.5 < tol*atom_tol for d in vecs ]):
                    return True
                #else:
                #    print vecs

        logger.debug("Atoms don't match.")
        return False

    def get_coord(self, vec, wrap=True):
        trans = self.inv.T.dot(vec)
        if wrap:
            return wrap(trans)
        else:
            return trans

    def contains(self, atom, tol=0.01):
        atom.structure = self
        for atom2 in self.atoms:
            if not atom2.element_id == atom.element_id:
                continue
            if abs(atom2.dist - atom.dist) > tol:
                continue
            d = self.get_distance(atom, atom2, limit=1)
            if d < tol and not d is None:
                return True
        return False

    def get_distance(self, atom1, atom2, limit=None, wrap_self=True):
        """
        Calculate the shortest distance between two atoms.

        .. Note::
            This is not as trivial a problem as it sounds. It is easy to
            demonstrate that for any non-cubic cell, the normal method of
            calculating the distance by wrapping the vector in fractional
            coordinates to the range (-0.5, 0.5) fails for cases near (0.5,0.5)
            in Type I cells and near (0.5, -0.5) for Type II. 

            To get the correct distance, the vector must be wrapped into the
            Wigner-Seitz cell. 

        Arguments:
            atom1, atom2: (:mod:`~qmpy.Atom`, :mod:`~qmpy.Site`, int).

        Keyword Arguments:
            limit: 
                If a limit is provided, returns None if the distance is
                greater than the limit.

            wrap_self: 
                If True, the distance from an atom to itself is 0, otherwise it
                is the distance to the shortest periodic image of itself.

        """
        if isinstance(atom1, int):
            atom1 = self.atoms[atom1].coord
        elif isinstance(atom1, (Atom,Site)):
            atom1 = atom1.coord
        if isinstance(atom2, int):
            atom2 = self.atoms[atom2].coord
        elif isinstance(atom2, (Atom,Site)):
            atom2 = atom2.coord

        x, y, z = self.cell
        xx = self.metrical_matrix[0,0]
        yy = self.metrical_matrix[1,1]
        zz = self.metrical_matrix[2,2]

        vec = atom2 - atom1
        vec -= np.round(vec)
        dist = np.dot(vec, self.cell)

        dist -= np.round(dist.dot(x)/xx)*x
        dist -= np.round(dist.dot(y)/yy)*y
        dist -= np.round(dist.dot(z)/zz)*z

        if limit:
            if any([ abs(d) > limit for d in dist]):
                return None

        dist = la.norm(dist)
        if not wrap_self:
            if abs(dist) < 1e-4:
                dist = min(self.lp[:3])

        if limit:
            if dist > limit:
                return None

        return dist

    def _get_vector(self, atom1, atom2):
        x, y, z = self.cell
        xx = self.metrical_matrix[0,0]
        yy = self.metrical_matrix[1,1]
        zz = self.metrical_matrix[2,2]

        vec = atom2.coord - atom1.coord
        vec -= np.round(vec)
        dist = np.dot(vec, self.cell)

        dist -= round(dist.dot(x)/xx)*x
        dist -= round(dist.dot(y)/yy)*y
        dist -= round(dist.dot(z)/zz)*z
        return dist

    def add_site(self, site):
        site.structure = self
        self.sites.append(site)
        for a in site.atoms:
            a.structure = self
            self.atoms.append(a)
        self.spacegroup = None

    def add_atom(self, atom, tol=0.01):
        """
        Adds `atom` to the structure if it isn't already contained.
        """
        if self.contains(atom, tol=tol):
            return
        atom.structure = self
        self.atoms.append(atom)
        for site in self.sites:
            if atom.is_on(site, tol=tol):
                site.add_atom(atom)
                break
        else:
            site = atom.get_site()
            self.sites.append(site)
        self.spacegroup = None

    def sort(self):
        self.atoms = sorted(self.atoms) 

    def set_composition(self, value=None):
        if value is None:
            self.composition = Composition.get(self.comp)
        return self.composition

    def set_magnetism(self, order, elements=None, scheme='primitive'):
        """
        Assigns magnetic moments to all atoms in accordance with the specified
        magnetism scheme.

        Schemes:

        +---------+-------------------------------------+
        | Keyword | Description                         |
        +=========+=====================================+
        |  None   | all magnetic moments = None         |
        +---------+-------------------------------------+
        | "ferro" | atoms with partially filled d and   |
        |         | f shells are assigned a magnetic    |
        |         | moment of 5 mu_b and 7 mu_b         |
        |         | respectively                        |
        +---------+-------------------------------------+
        | "anti"  | finds a highly ordererd arrangement |
        |         | arrangement of up and down spins.   |
        |         | If only 1 magnetic atom is found    |
        |         | a ferromagnetic arrangment is used. |
        |         | raises NotImplementedError          |
        +---------+-------------------------------------+

        """
        if order == 'none':
            for atom in self.atoms:
                atom.magmom = 0
                if atom.id is not None:
                    atom.save()
        if order == 'ferro':
            for atom in self.atoms:
                if atom.element.d_elec > 0 and atom.element.d_elec < 10:
                    atom.magmom = 5
                elif atom.element.f_elec > 0 and atom.element.f_elec < 14:
                    atom.magmom = 7
                else:
                    atom.magmom = 0
                if atom.id is not None:
                    atom.save()
        elif order == 'anti-ferro':
            if not elements:
                raise NotImplementedError
            ln = self.get_lattice_network(elements)

        self.spacegroup = None

    @property
    def comp(self):
        """Composition dictionary."""
        comp = {}
        for atom in self.atoms:
            elt = atom.element_id
            comp[elt] = comp.get(elt, 0) + atom.occupancy
        return comp

    @property
    def spec_comp(self):
        """Species composition dictionary."""
        spec_comp = {}
        for atom in self.atoms:
            spec = atom.species
            spec_comp[spec] = spec_comp.get(spec, 0) + atom.occupancy
        return spec_comp

    @property
    def name(self):
        """Unformatted name."""
        return format_comp(self.comp)

    @property
    def html(self):
        return html_comp(self.comp)

    @property
    def unit_comp(self):
        """Composition dict, where sum(self.unit_comp.values()) == 1"""
        return unit_comp(self.comp)

    @property
    def coords(self):
        """numpy.ndarray of atom coordinates."""
        return np.array([ atom.coord for atom in self.atoms ])

    @property
    def site_coords(self):
        """numpy.ndarray of site coordinates."""
        return np.array([ site.coord for site in self.sites ]) 

    @site_coords.setter
    def site_coords(self, coords):
        assert len(self.sites) == len(coords)
        for site, coord in zip(self.sites, coords):
            site.coord = wrap(coord)
            site._dist = None

    @property
    def site_types(self):
        return sorted(set([ format_comp(s.comp) for s in self.sites]))

    @coords.setter
    def coords(self, coords):
        if len(coords) != len(self.atoms):
            raise ValueError('%s != %s' % (len(coords), len(self)))
        for a, c in zip(self.atoms, coords):
            c = np.array(map(float,c))
            a.coord = wrap(c)
            a._dist = None

    @property
    def magmoms(self):
        """numpy.ndarray of magnetic moments of shape (natoms,)."""
        return np.array([ atom.magmom for atom in self.atoms ])

    @magmoms.setter
    def magmoms(self, moms):
        for mom, atom in zip(self, moms):
            atom.magmom = mom

    @property
    def cartesian_coords(self):
        """Return atomic positions in cartesian coordinates."""
        return np.array([ atom.cart_coord for atom in self.atoms ]) 

    @cartesian_coords.setter
    def cartesian_coords(self, cc):
        for atom, coord in zip(self.atoms, cc):
            atom.cart_coord = coord

    @property
    def forces(self):
        """numpy.ndarray of forces on atoms."""
        forces = []
        for atom in self.atoms:
            forces.append(atom.forces)
        return np.array(forces)

    @forces.setter
    def forces(self, forces):
        for forces, atom in zip(forces, self.atoms):
            atom.forces = force

    @property
    def reciprocal_lattice(self):
        """Reciprocal lattice of the structure."""
        if self._reciprocal_lattice is None:
            self._reciprocal_lattice = la.inv(self.cell).T
        return self._reciprocal_lattice

    _inv = None
    @property
    def inv(self):
        """
        Precalculates the inverse of the lattice, for faster conversion
        between cartesian and direct coordinates.
        
        """
        if self._inv is None:
            self._inv = la.inv(self.cell)
        return self._inv

    @property
    def relative_rec_lat(self):
        rec_lat = self.reciprocal_lattice
        rec_mags = map(la.norm, rec_lat)
        r0 = min(rec_mags)
        return np.array([ np.round(r/r0, 4) for r in rec_mags ])

    def get_kpoint_mesh(self, kppra):
        recs = self.reciprocal_lattice
        rec_mags = [ norm(recs[0]), norm(recs[1]), norm(recs[2])]
        r0 = max(rec_mags)
        refr = np.array([ roundclose(r/r0, 1e-2) for r in rec_mags ])
        refr = np.round(refr, 4)
        scale = 1.0
        kpts = np.ones(3)

        while self.natoms*np.product(kpts) < kppra:
            prev_kpts = kpts.copy()
            refk = np.array(np.ones(3)*refr)*scale
            kpts = np.array(map(np.round, refk))
            scale += 1

        upper = kppra - np.product(prev_kpts)*self.natoms
        lower = np.product(kpts)*self.natoms - kppra
        if upper < lower:
            kpts = prev_kpts.copy()
        return kpts

    def copy(self):
        """
        Create a complete copy of the structure, with any primary keys
        removed, so it is not associated with the original.

        """
        new = Structure()
        new.cell = self.cell
        new.sites = []
        new.atoms = [ atom.copy() for atom in self.atoms ]
        new.entry = self.entry
        new.composition = self.composition
        return new

    @property
    def similar(self):
        return Structure.objects.filter(natoms=self.natoms,
                composition=self.composition, 
                spacegroup=self.spacegroup,
                label=self.label).exclude(id=self.id)

    def set_natoms(self, n):
        """Set self.atoms to n blank Atoms."""
        self.atoms = [ Atom() for i in range(n) ]
        self._sites = None

    def set_nsites(self, n):
        """Sets self.sites to n blank Sites."""
        self.sites = [ Site() for i in range(n) ]
        self._atoms = None

    def make_conventional(self, in_place=True, tol=1e-5):
        """Uses spglib to convert to the conventional cell.

        Keyword Arguments:
            in_place: 
                If True, changes the current structure. If false returns
                a new one

            tol: 
                Symmetry precision for symmetry analysis
        
        Examples::

            >>> s = io.read(INSTALL_PATH+'io/files/POSCAR_FCC_prim')
            >>> print len(s)
            1
            >>> s.make_conventional()
            >>> print len(s)
            4

        """
        if not in_place:
            new = self.copy()
            new.make_conventional(tol=tol)
            return new

        refine_cell(self, symprec=tol)

    def make_primitive(self, in_place=True, tol=1e-5):
        """Uses spglib to convert to the primitive cell.

        Keyword Arguments:
            in_place: 
                If True, changes the current structure. If false returns
                a new one

            tol: 
                Symmetry precision for symmetry analysis
        
        Examples::

            >>> s = io.read(INSTALL_PATH+'io/files/POSCAR_FCC')
            >>> print len(s)
            4
            >>> s.make_primitive()
            >>> print len(s)
            1

        """
        if not in_place:
            new = self.copy()
            new.make_primitive(tol=tol)
            return new

        find_primitive(self, symprec=tol)

    def get_sites(self, tol=0.1):
        """
        From self.atoms, creates a list of Sites. Atoms which are closer
        than tol from one another are considered on the same site.

        """
        if not any([ a.occupancy < 1 for a in self.atoms ]):
            self._sites = [ a.get_site() for a in self.atoms ]
            return self._sites

        _sites = []
        for atom in self.atoms:
            site = atom.get_site()
            site.structure = self
            if not any([ site is site2 for site2 in _sites ]):
                _sites.append(site)
        self._sites = _sites
        return self.sites

    def group_atoms_by_symmetry(self):
        """Sort self.atoms according to the site they occupy."""
        eq = get_symmetry_dataset(self)['equivalent_atoms']
        resort = np.argsort(eq)
        self._atoms = list(np.array(self._atoms)[resort])

    def is_buerger_cell(self, tol=1e-5):
        """
        Tests whether or not the structure is a Buerger cell.
        """
        G = self.metrical_matrix
        if G[0,0] < G[1,1] - tol or G[1,1] < G[2,2] - tol:
            return False
        if abs(G[0,0] - G[1,1]) < tol:
            if abs(G[1,2]) > abs(G[0,2]) - tol:
                return False
        if abs(G[1,1] - G[2,2]) < tol:
            if abs(G[0,2]) > abs(G[0,1]) - tol:
                return False

    def is_niggli_cell(self, tol=1e-5):
        """
        Tests whether or not the structure is a Niggli cell.
        """
        if not self.is_grueber_cell():
            return False
        (a,b,c),(d,e,f) = self.niggli_form
        if abs(d-b) < tol:
            if f > 2*e - tol:
                return False
        if abs(e-a) < tol:
            if f > 2*d - tol:
                return False
        if abs(f-a) < tol:
            if e > 2*d - tol:
                return False
        if abs(d+b) < tol:
            if abs(f) > tol:
                return False
        if abs(e+a) < tol:
            if abs(f) > tol:
                return False
        if abs(f+a) < tol:
            if abs(f) > tol:
                return False
        if abs(d+e+f+a+b) < tol:
            if 2*a+2*e+f > -tol:
                return False
        return True

    def find_nearest_neighbors(self, method='closest', tol=0.05, limit=5.0,
            **kwargs):
        """
        Determine the nearest neighbors for all Atoms in Structure.

        Calls :func:`~qmpy.get_nearest_neighbors()` and assigns the nearest
        neighbor dictionary to `Structure._neighbor_dict`. Each atom is also
        given a list, `nearest_neighbors` that contains the nearest neighbor
        atoms. For atoms which have the "same" atom as a nearest neighbor across
        different periodic boundaries, a single atom may appear multiple times
        on the list.

        Keyword Arguments:
            limit: How far to look from each atom for nearest neighbors.
            Default=5.0.

            tol: A tolerance which determines how much further than the closest
            atom a second atom can be and still be a part of the nearest
            neighbor shell.

        Returns: None
        """
        self._neighbor_dict = find_nearest_neighbors(self, method=method,
                                                           tol=tol, 
                                                           limit=limit,
                                                           **kwargs)

    _neighbor_dict = None
    @property
    def nearest_neighbor_dict(self):
        """
        Dict of Atom:[list of Atom] pairs.
        """
        if self._neighbor_dict is None:
            self.find_nearest_neighbors()
        return self._neighbor_dict

    def get_sublattice(self, elements, new=True):
        if isinstance(elements, basestring):
            elements = [elements]
        if new:
            struct = self.copy()
            return struct.get_sublattice(elements, new=False)
        self.atoms = [ a for a in self if a.element_id in elements ]
        return self

    def get_lattice_network(self, elements=None, supercell=None, **kwargs):
        """
        Constructs a :mod:`networkx.Graph` of lattice sites.

        Keyword Arguments:
            elements:
                If `elements` is supplied, get_lattice_network will return the 
                lattice of those elements only. 

            supercell:
                Accepts any valid input to Structure.transform to construct a
                supercell, and return its lattice. Useful for finding AFM
                orderings for structures which have a smaller periodicity than
                their magnetic structure.

        Returns:
            A LatticeNetwork, which is a container for a lattice graph, which
            contains nodes which are atoms and edges which indicate nearest
            neighbors.

        Examples::
            
            >>> s = io.read(INSTALL_PATH+'/io/files/fe3o4.cif')
            >>> sl = s.get_lattice_network(elements=['Fe'])
            >>> sl.set_fraction(0.33333)
            >>> sl.fraction
            0.3333333333333333
            >>> sl.run_MC()

        """

        if supercell:
            new = self.transform(supercell, in_place=False)
            return new.get_lattice_network(elements=elements, **kwargs)
        pairs = set()
        if elements:
            struct = self.get_sublattice(elements)
            return struct.get_lattice_network()
        self.find_nearest_neighbors(**kwargs)
        for s1 in self.sites:
            n0 = len(pairs)
            lp1 = LatticePoint(s1.coord)
            for s2 in s1.neighbors:
                #if a1 < a2:
                #    continue
                lp2 = LatticePoint(s2.coord)
                #pairs.append((s1, s2))
                pairs.add(frozenset([lp1, lp2]))
        pairs = list(pairs)

        lattice = LatticeNetwork(pairs)
        lattice.structure = self
        return lattice

    def displace_atom(structure, index, vector):
        vector = np.array(vector)
        if not vector.shape == (3,):
            raise ValueError('Provide a 3x1 translation array')

        structure[index].coord += vector
        return structure

    def joggle_atoms(self, distance=1e-3, in_place=True):
        """
        Randomly displace all atoms in each direction by a distance up to +/- the
        distance keyword argument (in Angstroms).

        Optional keyword arguments:
            *distance*      : Range within all internal coordinates are
                                displaced. Default=1e-3
            *in_place*      : If True, returns an ndarray of the applied
                                translations. If False, returns (Structure,
                                translations).

        Examples::

            >>> s = io.read('POSCAR')
            >>> s2, trans = s.joggle_atoms(in_place=False)
            >>> trans = s.joggle_atoms(1e-1)
            >>> trans = s.joggle_atoms(distance=1e-1)

        """

        if not in_place:
            new = self.copy()
            new.joggle_atoms(distance=distance)
            return new

        def disp():
            dists = np.array([ distance/i for i in self.lp[:3]])
            rands = [ random.random() for i in range(3) ]
            return dists*rands

        translations = np.zeros(np.shape(self.coords))
        for i, atom in enumerate(self.atoms):
            tvec = disp()
            translations[i,:] = tvec
            atom.coord += tvec
        return translations

    def recenter(self, atom, in_place=True, middle=False):
        """
        Translate the internal coordinates to center the specified atom. Atom
        can be an actual Atom from the Structure.atoms list, or can be
        identified by index.

        Keyword Arguments:
            in_place: 
                If False, return a new Structure with the transformation applied.
                defaults to True.

            middle:
                If False, "centers" the cell by putting the atom at the origin.
                If True, "centers" the cell by putting the atom at
                (0.5,0.5,0.5). defaults to False.

        Examples::

            >>> s = io.read('POSCAR')
            >>> s.recenter(s[2])
            >>> s2 = s.recenter(s[0], in_place=False)
            >>> s2.recenter(2)
            >>> s == s2
            True

        """
        if not in_place:
            new = self.copy()
            new.recenter(atom, in_place=True)
            return new
        
        if isinstance(atom, int):
            atom = self.atoms[atom]

        new_center = np.array(atom.coord, dtype="float64")
        if middle:
            new_center += 0.5

        return self.translate(-new_center, cartesian=False, in_place=True)

    def translate(self, cv, cartesian=True, in_place=True):
        """
        Shifts the contents of the structure by a vector. 

        Optional keyword arguments:
            *cartesian*     : If True, translation vector is taken to be
                                cartesian coordinates. If False, translation
                                vector is taken to be in fractional
                                coordinates. Default=True
            *in_place*      : If False, return a new Structure with the
                                transformation applied.

        Examples::

            >>> s = io.read('POSCAR')
            >>> s.translate([1,2,3])
            >>> s.translate([0.5,0.5, 0.5], cartesian=False)
            >>> s2 = s.translate([-1,2,1], in_place=False)

        """

        if not in_place:
            new = self.copy()
            new.translate(cv, cartesian=cartesian, in_place=True)
            return new

        cv = np.array(cv)
        if not cv.shape == (3,):
            raise ValueError

        if all([ abs(v) < 1e-4 for v in cv]):
            return self

        if cartesian:
            cv = np.array(map(float, np.dot(self.inv.T, cv)))

        coords = self.coords + cv
        self.coords = wrap(coords)
        return self

    def find_lattice_points_within_distance(self, distance, tol=1e-6):
        """
        Find the lattice points contained within radius `distance` from the
        origin.

        """
        limits = [ int(np.ceil(distance/self.lp[i])) for i in range(3) ]
        ranges = [ range(0, l+1) for l in limits ]
        d2 = distance**2
        lattice_points = []
        for i, j, k in itertools.product(*ranges):
            #if (i,j,k) == (0,0,0):
            #    continue
            point = np.dot([i,j,k], self.cell)
            if any([ abs(p) > distance for p in point ]):
                continue
            if np.dot(point, point) < d2:
                lattice_points.append([i,j,k])
        return np.vstack(lattice_points)

    def find_lattice_points_by_transform(self, transform, tol=1e-6):
        """
        Find the lattice points contained within the transformation.

        """
        transform = np.array(transform)
        inv_trans = la.inv(transform.T)
        lattice_points = [None, None, None]

        for i in range(3):
            is_new = True
            cur_vec = np.array([0,0,0])
            trans_vecs = [np.array(cur_vec)]
            lattice_points[i] = [cur_vec]
            while is_new:
                cur_vec[i] += 1
                trans_vec = inv_trans.dot(cur_vec)
                trans_vec = wrap(trans_vec)

                # check for found
                for known in trans_vecs:
                    diff = known - trans_vec
                    diff = wrap(diff)

                    if all([ abs(x) < tol for x in diff ]):
                        is_new = False
                        break

                if is_new:
                    trans_vecs.append(np.array(trans_vec))
                    lattice_points[i].append(np.array(cur_vec))

        # loop over permutations of vectors
        enough = round(la.det(transform))
        trans_vecs = []
        dists = []
        for x, y, z in itertools.product(*lattice_points):
            cur_vec = x + y + z
            trans_vec = inv_trans.dot(cur_vec)
            trans_vec = wrap(trans_vec)

            found = False
            for known in trans_vecs:
                diff = known - trans_vec
                diff = wrap(diff)

                if all([ abs(x) < tol or abs(abs(x)-1) < tol for x in diff ]):
                    found = True
                    break

            if not found:
                trans_vecs.append(trans_vec)
            if len(trans_vecs) == enough:
                break

        return [ transform.T.dot(vec) for vec in trans_vecs ]

    def remove_atom(self, atom):
        ind = self.sites.index(atom.site)
        self.sites[ind].atoms.remove(atom)
        if len(self.sites[ind]) == 0:
            del self.sites[ind]
        self.atoms.remove(atom)

    def transform(self, transform, in_place=True, tol=1e-5):
        """
        Apply lattice transform to the structure. Accepts transformations of
        shape (3,) and (3,3).
        
        Optional keyword arguments:
            *in_place*      : If False, return a new Structure with the
                                transformation applied.

        Examples::

            >>> s = io.read('POSCAR')
            >>> s.transform([2,2,2]) # 2x2x2 supercell
            >>> s.transform([[0,1,0],[1,0,0],[0,0,1]]) # swap axis 1 for 2
            >>> s2 = s.transform([2,2,2], in_place=False)

        """

        if not in_place:
            new = self.copy()
            new.transform(transform)
            return new

        transform = np.array(transform)
        if transform.shape == (3,3):
            pass
        elif transform.shape in [ (1,3), (3,) ]:
            transform = np.eye(3)*transform
        else:
            raise ValueError

        # test for singular matrix

        #if la.det(transform) < 0:
        #    transform = np.dot([[-1,0,0],[0,-1,0],[0,0,-1]], transform)
        if la.det(transform) == 1:
            # if cell size doesn't change
            new_cell = transform.dot(self.cell)
            inv = la.inv(transform.T)
            coords = np.array([ inv.dot(c) for c in self.coords ])
            self.coords = coords
            self.cell = new_cell
            return self

        # Test for simple IxJxK lattice multiplication        
        diag = True
        for i, j in itertools.combinations(range(3), r=2):
            if i == j:
                continue
            if transform[i,j] != 0:
                diag = False
                break
        if diag:
            # do simple expansion
            i = int(transform[0,0])
            j = int(transform[1,1])
            k = int(transform[2,2])
            points = itertools.product(range(i), range(j), range(k))
        else:
            points = self.find_lattice_points_by_transform(transform)

        # construct the new lattice
        cell = list(self.cell)
        elts = list(self.atom_types)
        new_cell = transform.dot(cell)
        inv = la.inv(transform.T)
        n_cells = abs(roundclose(la.det(transform)))

        sites = []
        self.lattice_points = points
        self.sites_by_lattice_point = {}
        self.atoms_by_lattice_point = {}
        for point in points:
            lp_sites = []
            lp_atoms = []
            for site in self.sites:
                new = site.copy()
                coord = point + site.coord
                new.coord = inv.dot(coord)
                new.base_site = site
                sites.append(new)

                lp_atoms += new.atoms
                lp_sites.append(new)
            self.sites_by_lattice_point[tuple(point)] = lp_sites
            self.atoms_by_lattice_point[tuple(point)] = lp_atoms

        self.cell = new_cell
        self.sites = sites
        return self

    t = transform

    def substitute(self, replace, 
                         rescale=True, rescale_method="relative",
                         in_place=False, 
                         **kwargs):
        """Replace atoms, as specified in a dict of pairs. 

        Keyword Arguments:
            rescale: 
                rescale the volume of the final structure based on the per 
                atom volume of the new composition.

            rescale_method:
                How to rescale the 

            in_place: 
                change the species of the current Structure or return a new 
                one.

        Examples::

            >>> s = io.read('POSCAR-Fe2O3')
            >>> s2 = s.substitute({'Fe':'Ni', 'O':'F'} rescale=True)
            >>> s2.substitute({'Ni':'Co'}, in_place=True, rescale=False)

        """

        if not in_place:
            new = self.copy()
            new.substitute(replace, rescale=rescale, in_place=True)
            return new

        volume = self.get_volume()
        for atom in self:
            if atom.element_id in replace:
                volume -= atom.element.volume
                atom.element = Element.get(replace[atom.element_id])
                volume += atom.element.volume
        if rescale and rescale_method == "relative":
            self.set_volume(volume)
        elif rescale and rescale_method == "absolute":
            self.set_volume_to_sum_of_elements()
        self.set_composition()
        return self
    sub = substitute
    replace = substitute

    def refine(self, tol=1e-3, recurse=True):
        """
        Identify atoms that are close to high symmetry sites (within `tol` and
        shift them onto them.

        Note: 
            "symprec" doesn't appear to do anything with spglib, so I am
            unable to get "loose" symmetry operations. Without which, this 
            doesn't work.

        Examples::

            >>> s = io.read('POSCAR')
            >>> s.symmetrize()
            >>> print s.spacegroup
            225L
            >>> s.refine()
            >>> print s.spacegroup
            1L

        """

        self.reduce()
        self.symmetrize(tol=tol)
        new_coords = []
        for atom in self:
            coords = []
            for rot, trans in self.operations:
                test = rot.dot(atom.coord) + trans
                test = wrap(test)
                if not any([all(test==c) for c in coords]):
                    if self.get_distance(test, atom, limit=1) < tol:
                        coords.append(test)
            central = np.average(coords, 0)
            new_coords.append(central)
        self.coords = new_coords
        if recurse:
            self.refine(tol=tol, recurse=False)

    def reduce(self, tol=1e-3, limit=1000, in_place=True):
        """
        Get the transformation matrix from unit to reduced cell
        Acta. Cryst. (1976) A32, 297
        Acta. Cryst. (2003) A60, 1

        Optional keyword arguments:
            *tol* : 
                eps_rel in Acta. Cryst. 2003 above. Similar to 
                tolerance for floating point comparisons. Defaults to 1e-5.
            *limit* : 
                maximum number of loops through the algorithm. Defaults to 
                1000. 
            *in_place* : 
                Change the Structure or return a new one. If True, the 
                transformation matrix is returned. If False, a tuple of
                (Structure, transformation_matrix) is returned. 

        Examples::

            >>> s = io.read('POSCAR')
            >>> s.reduce()
            >>> s.reduce(in_place=False, get_transform=False)

        """

        if not in_place:
            new = self.copy()
            trans = new.reduce(tol=tol, limit=limit)
            return new, trans

        # reduction parameters
        vectors = self.cell.copy()
        (a,b,c), (ksi,eta,zeta) = basis_to_niggli(vectors)
        trans = np.eye(3)

        # convergence variables
        _a, _b, _c = a*10, b*10, c*10
        mult = 10

        # tolerance and tests
        eps = tol * self.get_volume()**(1./3)

        def lt(x, y):
            return x < y - eps

        def gt(x, y):
            return x > y + eps

        def eq(x, y):
            return abs(x - y) < eps

        def update(mod, trans):
            trans = trans.dot(mod)
            return basis_to_niggli(trans.T.dot(vectors)), trans

        step = 0
        while step < limit:
            step += 1

            # N 1
            if gt(a,b) or (eq(a,b) and gt(abs(ksi),abs(eta))):
                r = np.array([[0,-1,0],[-1,0,0],[0,0,-1]])
                ((a,b,c),(ksi,eta,zeta)),trans = update(r, trans)
                logger.debug('reduction: test 1')

            # N 2
            if gt(b, c) or ( eq(b,c) and gt(abs(eta),abs(zeta))):
                r = np.array([[-1,0,0],[0,0,-1],[0,-1,0]])
                ((a,b,c),(ksi,eta,zeta)),trans = update(r, trans)
                logger.debug('reduction: test 2')
                continue

            # N 3
            if gt(ksi*eta*zeta, 0):
                i = ( -1 if lt(ksi, 0) else 1 )
                j = ( -1 if lt(eta, 0) else 1 )
                k = ( -1 if lt(zeta, 0) else 1 )
                r = np.eye(3)*np.array([i,j,k])
                ((a,b,c),(ksi,eta,zeta)),trans = update(r, trans)
                logger.debug('reduction: test 3 True path')
            else:
                vals = [1,1,1]
                p=0
                for i, x in enumerate([ksi, eta, zeta]):
                    if gt(x, 0):
                        vals[i] = -1
                    elif not lt(x, 0):
                        p = i
                if np.product(vals) < 0:
                    vals[p] = -1
                r = np.eye(3)*vals
                ((a,b,c),(ksi,eta,zeta)),trans = update(r, trans)
                logger.debug('reduction: test 3 False path')

                # test minimum reduction
            if ( mult*a + (a - _a) - (a*mult) == 0 
                    and 
                 mult*b + (b - _b) - (b*mult) == 0
                    and 
                 mult*c + (c - _c) - (c*mult) == 0 ):
                logger.debug('reduction: Minimum reduction test passed')
                #break
            _a, _b, _c = a, b, c

            # N 5
            if (gt(abs(ksi), b) or 
                    (eq(ksi,b) and lt(2*eta,zeta)) or 
                    (eq(ksi,-b) and lt(zeta,0))):
                r = np.array([[1,0,0], [0,1,-sign(ksi)], [0,0,1]])
                ((a,b,c),(ksi,eta,zeta)),trans = update(r, trans)
                logger.debug('reduction: test 5')
                continue

            # N 6
            if (gt(abs(eta),a) or 
                    ( eq(eta,a) and lt(2*ksi,zeta)) or 
                    ( eq(eta,-a) and lt(zeta,0))):
                r = np.array([[1,0,-sign(eta)], [0,1,0], [0,0,1]])
                ((a,b,c),(ksi,eta,zeta)),trans = update(r, trans)
                logger.debug('reduction: test 6')
                continue
            
            # N 7
            if (gt(abs(zeta),a) or 
                    ( eq(zeta, a) and lt(2*ksi, eta)) or 
                    ( eq(zeta, -a) and lt(eta, 0))):
                r = np.array([[1,-sign(zeta),0], [0,1,0], [0,0,1]])
                ((a,b,c),(ksi,eta,zeta)),trans = update(r, trans)
                logger.debug('reduction: test 7')
                continue

            # N 8
            if (lt(ksi + eta + zeta + a + b, 0) or 
                    (eq(ksi + eta + zeta + a + b, 0) and gt(2*(a+eta)+zeta, 0))):
                r = np.array([[1,0,1], [0,1,1], [0,0,1]])
                ((a,b,c),(ksi,eta,zeta)),trans = update(r, trans)
                logger.debug('reduction: test 8')
                continue
            break

        # temporarily stored transformations
        self._original_cell = self.cell.copy()
        self._unit_to_reduced = trans.T
        self._reduced_point_to_unit = trans
        self._unit_point_to_reduced = la.inv(trans)

        self.transform(trans.T)
        return trans

    def get_xrd(self, **kwargs):
        xrd = XRD(self)
        xrd.get_peaks()
        xrd.get_intensities()
        return xrd

    def get_pdf(self, **kwargs):
        self.pdf = PDF(self, **kwargs)
        self.pdf.get_pair_distances()
        return self.pdf

    _cart_rots = None
    def get_cartesian_rotations(self):
        if self._cart_rots is None:
            self.symmetrize()
            p = self.cell.T
            q = la.inv(self.cell.T)
            cr = []
            for rot in self.rotations:
                c1 = p.dot(rot).dot(q)
                if any([ np.allclose(c1, c2) for c2 in cr ]):
                    continue
                cr.append(c1)
            self._cart_rots = cr
        return self._cart_rots

    @property
    def is_perfect(self):
        if any([s.partial for s in self.sites ]):
            return False
        return True

    def create_slab(self, indices, vacuum=10.0, surface=None, in_place=True):
        if not in_place:
            new = self.copy()
            return new.create_slab(indices, vacuum=vacuum, surface=surface)

    def create_vacuum(self, direction, amount, in_place=True):
        """
        Add vacuum along a lattice direction.

        Arguments:
            direction: direction to add the vacuum along. (0=x, 1=y, 2=z)
            amount: amount of vacuum in Angstroms.

        Keyword Arguments:
            in_place: apply change to current structure, or return a new one.

        Examples::
            
            >>> s = io.read(INSTALL_PATH+'/io/files/POSCAR_FCC')
            >>> s.create_vacuum(2, 5)
        """
        if not in_place:
            new = self.copy()
            return new.create_vacuum(direction, amount)

        cart_coords = self.cartesian_coords
        new_cell = self.lat_params
        new_cell[direction] += float(amount)
        self.lat_params = new_cell
        self.cartesian_coords = cart_coords
        return self

    def make_perfect(self, in_place=True, tol=1e-1):
        """
        Constructs options for a 'perfect' lattice from the structure.

        If a site is not fully occupied, but has only one atom type on it, it
        will be filled the rest of the way.
        If a site has two or more atom types on it, the higher fraction element
        will fill the site. 

        Keyword Arguments:
            in_place: If False returns a new :mod:`~qmpy.Structure`, otherwise
            returns None

            tol: maximum defect concentration.

        Examples::
            
            >>> s = io.read(INSTALL_PATH+'/io/files/partial_vac.cif')
            >>> s
            <Structure: Mn3.356Si4O16>
            >>> s.make_perfect()
            >>> s
            <Structure: MnSiO4>
            >>> s = io.read(INSTALL_PATH+'/io/files/partial_mix.cif')
            >>> s
            <Structure: Mn4.264Co3.736Si4O16>
            >>> s2 = s.make_perfect(in_place=False)
            >>> s2
            <Structure: MnCoSiO4>

        """
        if not in_place:
            new = self.copy()
            return new.make_perfect(True, tol=tol)

        init_atoms = [ a.copy() for a in self.atoms ]
        init_comp = dict(self.comp)
        n = sum(init_comp.values())
        atom_tol = tol*n
        hopeless = False

        for s1, s2 in itertools.combinations(self.sites, r=2):
            d = self.get_distance(s1, s2, limit=1, wrap_self=True) 
            if d is None:
                continue
            if d < 0.8:
                return self

        atoms = []
        for atom in self.atoms:
            if abs(1-atom.occupancy) < 0.5:
                # first, fill any nearly full sites
                new = atom.copy()
                new.occupancy = 1.0
                new.site = None
                atoms.append(new)
            elif abs(atom.occupancy) <= 0.5:
                # then, empty any nearly empty sites
                continue
            elif atom.occupancy >= 2:
                raise StructureError('Site occupied by a molecule')

        self._sites = []
        self.atoms = atoms
        self.get_sites()

        if self.is_perfect:
            # total
            if abs(sum(self.comp.values()) - n) > tol:
                hopeless = True

            for k in init_comp.keys():
                d = init_comp[k] - self.comp.get(k, 0.0)
                if abs(d) > tol:
                    hopeless = True
                    break
            self.composition = Composition.get(self.comp)
            
            if not hopeless:
                return self

        self._sites = []
        self.atoms = init_atoms 
        self.get_sites()
        return self

class Prototype(models.Model):
    """
    Base class for a prototype structure. 

    Relationships:
        | :mod:`~qmpy.Composition` via composition_set
        | :mod:`~qmpy.Structure` via structure_set
        | :mod:`~qmpy.Entry` via entry_set

    Attributes:
        | name: Prototype name.

    """

    name = models.CharField(max_length=63, primary_key=True)
    structure = models.ForeignKey(Structure, related_name='+', 
                                  blank=True, null=True)
    composition = models.ForeignKey('Composition', blank=True, null=True)

    class Meta:
        app_label = 'qmpy'
        db_table = 'prototypes'

    @classmethod
    def get(cls, name):
        """
        Retrieves a :mod:`~qmpy.Prototype` named `name` if it exists. If not, creates
        a new one.

        Examples:

          >>> proto = Prototype.get('Corundum')

        """
        obj, new = cls.objects.get_or_create(name=name)
        if new:
            obj.save()
        return obj

    def __str__(self):
        if not self.structure is None:
            sname = self.structure.name
            return '%s - %s' % (self.name, self.structure.name)
        else:
            return self.name

