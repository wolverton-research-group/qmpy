# qmpy/analysis/thermodynamics/space.py

import networkx as nx
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
import logging

from django.db import transaction

import qmpy
from qmpy.utils import *
import phase
from reaction import Reaction
from equilibrium import Equilibrium

logger = logging.getLogger(__name__)

if qmpy.FOUND_PULP:
    import pulp
else:
    logger.warn('Cannot import PuLP, cannot do GCLP')

class PhaseSpaceError(Exception):
    pass

class Heap(dict):
    def add(self, seq):
        if len(seq) == 1:
            self[seq[0]] = Heap()
            return 
        seq = sorted(seq)
        e0 = seq[0]
        if e0 in self:
            self[e0].add(seq[1:])
        else:
            self[e0] = Heap()
            self[e0].add(seq[1:])

    @property
    def sequences(self):
        seqs = []
        for k, v in self.items():
            if not v:
                seqs.append([k])
            else:
                for v2 in v.sequences:
                    seqs.append([k] + v2)
        return seqs

class PhaseSpace(object):
    """
    A PhaseSpace object represents, naturally, a region of phase space.

    The most fundamental property of a PhaseSpace is its bounds,
    which are given as a hyphen-delimited list of compositions. These represent
    the extent of the phase space, and determine which phases are within the
    space.

    Next, a PhaseSpace has an attribute, data, which is a PhaseData object,
    and is a container for Phase objects, which are used when performing
    thermodynamic analysis on this space.

    The majority of attributes are lazy, that is, they are only computed when
    they are requested, and how to get them (of which there are often several
    ways) is decided based on the size and shape of the phase space.

    """

    def __init__(self, bounds, mus=None, data=None, **kwargs):
        """
        Arguments:
            bounds:
                Sequence of compositions. Can be comma-delimited ("Fe,Ni,O"),
                an actual list (['Fe', 'Ni', 'O']) or any other python
                sequence. The compositions need not be elements, if you want to
                take a slice through the Fe-Ni-O phase diagram between Fe3O4
                and NiO, just do "Fe3O4-NiO".

        Keyword Arguments
            mus:
                define a dictionary of chemical potentials. Will adjust all
                calculated formation energies accordingly.

            data:
                If supplied with a PhaseData instance, it will be used
                instead of loading from the OQMD. Can be used to significantly
                reduce the amount of time spent querying the database when looping
                through many PhaseSpaces.

        Examples::

            >>> ps = PhaseSpace('Fe-Li-O', load="legacy.dat")
            >>> ps2 = PhaseSpace(['Fe','Li','O'], data=ps.data)
            >>> ps = PhaseSpace(set(['Li', 'Ni', 'O']))
            >>> ps = PhaseSpace('Li2O-Fe2O3')

        """
        self.clear_all()
        self.set_mus(mus)
        self.set_bounds(bounds)
        if data is None:
            self.data = phase.PhaseData()
            if bounds:
                self.load(**kwargs)
        else:
            self.data = data.get_phase_data(self.space)

    def __repr__(self):
        if self.bounds is None:
            return '<unbounded PhaseSpace>'
        names = [ format_comp(reduce_comp(b)) for b in self.bounds ]
        bounds = '-'.join(names)
        if self.mus:
            bounds += ' ' + format_mus(self.mus)
        return '<PhaseSpace bound by %s>' % bounds

    def __getitem__(self, i):
        return self.phases[i]

    def __len__(self):
        return len(self.phases)

    def set_bounds(self, bounds):
        bounds = parse_space(bounds)
        if bounds is None:
            self.bounds = None
            return 

        elements = sorted(set.union(*[ set(b.keys()) for b in bounds ]))
        basis = []
        for b in bounds:
            basis.append([ b.get(k, 0) for k in elements])

        self.bounds = bounds
        self.basis = np.array(basis)

    def infer_formation_energies(self):
        mus = {}
        for elt in self.space:
            if elt in self.phase_dict:
                mus[elt] = self.phase_dict[elt].energy
            else:
                mus[elt] = 0.0

        for phase in self.phases:
            for elt in self.space:
                phase.energy -= phase.unit_comp.get(elt, 0)*mus[elt]

    def set_mus(self, mus):
        self.mus = {}
        if mus is None:
            return
        elif isinstance(mus, basestring):
            mus = mus.replace(',', ' ')
            for mu in mus.split():
                self.mus.update(parse_mu(mu))
        elif isinstance(mus, dict):
            self.mus = mus

    def load(self, **kwargs):
        """
        Loads oqmd data into the associated PhaseData object.
        """
        target = kwargs.get('load', 'oqmd')
        if not target:
            return

        stable = kwargs.get('stable', False)
        fit = kwargs.get('fit', 'standard')
        total = kwargs.get('total', (fit is None))
        if target == 'oqmd':
            self.data.load_oqmd(self.space, fit=fit, 
                    stable=stable, total=total)
        elif 'legacy' in target:
            self.data.load_library('legacy.dat')
        elif target == 'icsd':
            self.data.load_oqmd(self.space, fit=fit,
                    search={'entry__path__contains':'icsd'},
                    stable=stable, total=total_energy)
        elif target == 'prototypes':
            self.data.load_oqmd(space=self.space, fit=fit,
                    search={'path__contains':'prototypes'},
                    stable=stable, total=total_energy)
        elif target == None:
            pass
        else:
            raise ValueError("Unknown load argument: %s" % target)

    def get_subspace(self, space):
        data = self.data.get_phase_data(space)
        return PhaseSpace(space, data=data)

    _phases = None
    @property
    def phases(self):
        if self._phases:
            return self._phases
        phases = [ p for p in self.data.phases if self.in_space(p) and p.use ]
        self._phases = phases
        return self._phases

    @phases.setter
    def phases(self, phases):
        self.clear_all()
        self.data = phase.PhaseData()
        self.data.phases = phases

    _phase_dict = None
    @property
    def phase_dict(self):
        if self._phase_dict:
            return self._phase_dict
        phase_dict = dict([ (k, p) for k, p in self.data.phase_dict.items()
                if p.use and self.in_space(p) ])
        self._phase_dict = phase_dict
        return self._phase_dict

    @phase_dict.setter
    def phase_dict(self, phase_dict):
        self.clear_all()
        self.data = phase.PhaseData()
        self.data.phases = phase_dict.values()

    def phase_energy(self, p):
        dE = sum([self.mus.get(k, 0)*v for k,v in p.unit_comp.items()])
        N = sum(v for k,v in p.unit_comp.items() if k in self.bound_space)
        if N == 0:
            N = 1
        return (p.energy - dE)/N

    def phase_comp(self, p):
        comp = dict((k,v) for k,v in p.comp.items() 
                 if k in self.bound_elements)
        return unit_comp(comp)

    def clear_data(self):
        """
        Clears all phase data.
        """
        self._phases = None
        self._phase_dict = None

    def clear_analysis(self):
        """
        Clears all calculated results.
        """
        self._stable = None
        self._tie_lines = None
        self._hull = None
        self._spaces = None
        self._dual_spaces = None
        self._cliques = None
        self._graph = None

    def clear_all(self):
        """
        Clears input data and analyzed results. 
        Same as:
        >>> PhaseData.clear_data() 
        >>> PhaseData.clear_analysis()
        """
        self.clear_data()
        self.clear_analysis()

    def load_tie_lines(self):
        raise NotImplementedError

    @property
    def comp_dimension(self):
        """
        Compositional dimension of the region of phase space.

        Examples::

            >>> s = PhaseSpace('Fe-Li-O')
            >>> s.comp_dimension
            2
            >>> s = PhaseSpace('FeO-Ni2O-CoO-Ti3O4')
            >>> s.comp_dimension
            3

        """
        return len(self.bounds) - 1

    @property
    def chempot_dimension(self):
        """
        Chemical potential dimension.

        Examples::

            >>> s = PhaseSpace('Fe-Li', 'O=-2.5')
            >>> s.chempot_dimension
            0
            >>> s = PhaseSpace('Fe-Li', 'N=0:-5')
            >>> s.chempot_dimension
            1
            >>> s = PhaseSpace('Fe-Li', 'N=0:-5 F=0:-5')
            >>> s.chempot_dimension
            2

        """
        cpdims = [ k for k,v in self.mus.items() if isinstance(v, list) ]
        return len(cpdims)

    @property
    def shape(self):
        """
        (# of compositional dimensions, # of chemical potential dimensions)
        The shape attribute of the PhaseSpace determines what type of phase
        diagram will be drawn.

        Examples::

            >>> s = PhaseSpace('Fe-Li', 'O=-1.2')
            >>> s.shape
            (1, 0)
            >>> s = PhaseSpace('Fe-Li', 'O=0:-5')
            >>> s.shape
            (1, 1)
            >>> s = PhaseSpace('Fe-Li-P', 'O=0:-5')
            >>> s.shape
            (2,1)
            >>> s = PhaseSpace('Fe', 'O=0:-5')
            >>> s.shape
            (0, 1)

        """
        return (self.comp_dimension, self.chempot_dimension)

    @property
    def bound_space(self):
        """
        Set of elements _of fixed composition_ in the PhaseSpace.

        Examples::

            >>> s = PhaseSpace('Fe-Li', 'O=-1.4')
            >>> s.bound_space
            set(['Fe', 'Li'])

        """
        if self.bounds is None:
            return set()
        return set.union(*[ set(b.keys()) for b in self.bounds ])

    @property
    def bound_elements(self):
        """
        Alphabetically ordered list of elements with constrained composition.
        """
        return sorted(self.bound_space)

    @property
    def space(self):
        """
        Set of elements present in the PhaseSpace.

        Examples::

            >>> s = PhaseSpace('Pb-Te-Se')
            >>> s.space
            set(['Pb', 'Te', 'Se'])
            >>> s = PhaseSpace('PbTe-Na-PbSe')
            >>> s.space
            set(['Pb', 'Te', 'Na', 'Se'])

        """
        return self.bound_space | set(self.mus.keys())

    @property
    def elements(self):
        """
        Alphabetically ordered list of elements present in the PhaseSpace.
        """
        return sorted(self.space)

    def coord(self, composition, tol=1e-4):
        """Returns the barycentric coordinate of a composition, relative to the
        bounds of the PhaseSpace. If the object isn't within the bounds, raises
        a PhaseSpaceError.

        Examples::

            >>> space = PhaseSpace('Fe-Li-O')
            >>> space.coord({'Fe':1, 'Li':1, 'O':2})
            array([ 0.25,  0.25,  0.5 ])
            >>> space = PhaseSpace('Fe2O3-Li2O')
            >>> space.coord('Li5FeO4')
            array([ 0.25,  0.75])

        """
        if isinstance(composition, phase.Phase):
            composition = composition.comp
        elif isinstance(composition, basestring):
            composition = parse_comp(composition)

        composition = defaultdict(float, composition)
        if self.bounds is None:
            return np.array([ composition[k] for k in self.bound_elements ])

        bcomp = dict((k,v) for k,v in composition.items() if k in
                self.bound_space)
        composition = unit_comp(bcomp)
        cvec = np.array([ composition.get(k, 0) for k in self.bound_elements ])
        coord = np.linalg.lstsq(self.basis.T, cvec, rcond=None)[0]
        if abs(sum(coord) - 1) > 1e-3 or any(c < -1e-3 for c in coord):
            raise PhaseSpaceError
        return coord

    def comp(self, coord):
        """
        Returns the composition of a coordinate in phase space.

        Examples::

            >>> space = PhaseSpace('Fe-Li-O')
            >>> space.comp([0.2, 0.2, 0.6])
            {'Fe': 0.2, 'O': 0.6, 'Li': 0.2}

        """
        if self.bounds is None:
            return defaultdict(float, zip(self.elements, coord))
        if len(coord) != len(self.bounds):
            raise PhaseSpaceError
        if len(coord) != len(self.bounds):
            raise ValueError("Dimensions of coordinate must match PhaseSpace")

        tot = sum(coord)
        coord = [ c/float(tot) for c in coord ]
        comp = defaultdict(float)
        for b, x in zip(self.bounds, coord):
            for elt, val in b.items():
                comp[elt] += val*x
        return dict( (k,v) for k,v in comp.items() if v > 1e-4 )

    _spaces = None
    @property
    def spaces(self):
        """
        List of lists of elements, such that every phase in self.phases
        is contained in at least one set, and no set is a subset of
        any other. This corresponds to the smallest subset of spaces that must
        be analyzed to determine the stability of every phase in your dataset.

        Examples::

            >>> pa, pb, pc = Phase('A', 0), Phase('B', 0), Phase('C', 0)
            >>> p1 = Phase('AB2', -1)
            >>> p2 = Phase('B3C', -4)
            >>> s = PhaseSpace('A-B-C', load=None)
            >>> s.phases = [ pa, pb, pc, p1, p2 ]
            >>> s.spaces
            [['C', 'B'], ['A', 'B']]

        """
        if self._spaces:
            return self._spaces
        spaces = set([ frozenset(p.space) for p in self.phase_dict.values() ])
        spaces = [ space for space in spaces if not 
                any([ space < space2 for space2 in spaces ])]
        self._spaces = list(map(list, spaces))
        return self._spaces

    def find_stable(self):
        stable = set()
        for space in self.spaces:
            subspace = self.get_subspace(space)
            stable |= set(subspace.stable)
        self._stable = stable
        return stable

    _dual_spaces = None
    @property
    def dual_spaces(self):
        """
        List of sets of elements, such that any possible tie-line
        between two phases in phases is contained in at least one
        set, and no set is a subset of any other.
        """
        if self._dual_spaces is None:
            #self._dual_spaces = self.get_dual_spaces()
            self._dual_spaces = self.heap_structure_spaces()
        return self._dual_spaces

    def heap_structure_spaces(self):
        if len(self.spaces) == 1:
            return self.spaces
        heap = Heap()
        for i, (c1, c2) in enumerate(itertools.combinations(self.spaces, r=2)):
            heap.add(set(c1 + c2))
        return heap.sequences

    def get_dual_spaces(self):
        if len(self.spaces) == 1:
            return self.spaces

        dual_spaces = []
        imax = len(self.spaces)**2 / 2
        spaces = sorted(self.spaces, key=lambda x: -len(x))
        for i, (c1, c2) in enumerate(itertools.combinations(spaces, r=2)):
            c3 = frozenset(c1 + c2)
            if c3 in sizes[n]:
                break
            for j, c4 in enumerate(dual_spaces):
                if c3 <= c4:
                    break
                elif c4 < c3:
                    dual_spaces[j] = c3
                    break
            else:
                dual_spaces.append(c3)

        self._dual_spaces = dual_spaces
        return self._dual_spaces

    def find_tie_lines(self):
        phases = self.phase_dict.values()
        indict = dict((k, v) for v, k in enumerate(phases))
        adjacency = np.zeros((len(indict), len(indict)))
        for space in self.dual_spaces:
            subspace = self.get_subspace(space)
            for p1, p2 in subspace.tie_lines:
                i1, i2 = sorted([indict[p1], indict[p2]])
                adjacency[i1, i2] = 1
        tl = set( (phases[i], phases[j]) for i, j in 
                zip(*np.nonzero(adjacency)) )
        self._tie_lines = tl
        return tl

    @property
    def stable(self):
        """
        List of stable phases
        """
        if self._stable is None:
            self.hull
            #self.compute_hull()
        return self._stable

    @property
    def unstable(self):
        """
        List of unstable phases.
        """
        if self._stable is None:
            self.hull
            #self.compute_hull()
        return [ p for p in self.phases if
            ( not p in self.stable ) and self.in_space(p) ]

    _tie_lines = None
    @property
    def tie_lines(self):
        """
        List of length 2 tuples of phases with tie lines between them
        """
        if self._tie_lines is None:
            self.hull
            #self.compute_hull()
        return [ list(tl) for tl in self._tie_lines ]

    @property
    def tie_lines_list(self):
        return list(self.tie_lines)

    @property
    def hull(self):
        """
        List of facets of the convex hull.
        """
        if self._hull is None:
            self.get_hull()
        return list(self._hull)

    def get_hull(self):
        if any( len(b) > 1 for b in self.bounds ):
            points = self.get_hull_points()
            self.get_qhull(phases=points)
        else:
            self.get_qhull()

    @property
    def hull_list(self):
        return list(self.hull)

    _graph = None
    @property
    def graph(self):
        """
        :mod:`networkx.Graph` representation of the phase space.
        """
        if self._graph:
            return self._graph
        graph = nx.Graph()
        graph.add_edges_from(self.tie_lines)
        self._graph = graph
        return self._graph

    _cliques = None
    @property
    def cliques(self):
        """
        Iterator over maximal cliques in the phase space. To get a list of
        cliques, use list(PhaseSpace.cliques).
        """
        if self._cliques is None:
            self.find_cliques()
        return self._cliques

    def find_cliques(self):
        self._cliques = nx.find_cliques(self.graph)
        return self._cliques

    def cliques_to_hull(self, cliques):
        raise NotImplementedError

    def stability_range(self, p, element=None):
        """
        Calculate the range of phase `p` with respect to `element`.
        """
        if element is None and len(self.mus) == 1:
            element = self.mus.keys()[0]
        tcomp = dict(p.unit_comp)
        e, c = self.gclp(tcomp, mus=None)
        tcomp[element] = tcomp.get(element, 0) + 0.001
        edo, xdo = self.gclp(tcomp, mus=None)
        tcomp[element] -= 0.001
        if element in p.comp.keys():
            tcomp[element] -= 0.001
            eup, xup = self.gclp(tcomp, mus=None)
            return (edo-e)/0.001, (e-eup)/0.001
        else:
            return (edo-e)/0.001, -20

    def chempot_bounds(self, composition, total=False):
        energy, phases = self.gclp(composition)
        chems = {}
        for eq in self.hull_list:
            if not phases in eq:
                continue
            pots = eq.chemical_potentials
            if total:
                for k in pots:
                    pots[k] += qmpy.chem_pots['standard']['elements'][k]
            chems[eq] = pots
        return chems

    def chempot_range(self, p, element=None):
        pot_bounds = {}
        tcomp = dict(p.unit_comp)
        e, c = self.gclp(tcomp, mus=None)
        for elt in p.comp.keys():
            tcomp = dict(p.unit_comp)
            tcomp[elt] -= 0.001
            eup, xup = self.gclp(tcomp)
            tcomp[elt] += 0.002
            edo, xdo = self.gclp(tcomp)
            pot_bounds[elt] = [ (edo-e)/0.001, (e-eup)/0.001 ]
        return pot_bounds

    def get_tie_lines_by_gclp(self, iterable=False):
        """
        Runs over pairs of Phases and tests for equilibrium by GCLP. Not
        recommended, it is very slow.

        """
        tie_lines=[]
        self.get_gclp_stable()

        for k1, k2 in itertools.combinations(self.stable, 2):
            testpoint = (self.coord(k1.unit_comp) + self.coord(k2.unit_comp))/2
            energy, phases = self.gclp(self.comp(testpoint))
            if abs(energy - (k1.energy + k2.energy)/2) < 1e-8:
                tie_lines.append([k1,k2])
                if iterable:
                    yield [k1, k2]
        self._tie_lines = tie_lines

    def in_space(self, composition):
        """
        Returns True, if the composition is in the right elemental-space 
        for this PhaseSpace.

        Examples::

            >>> space = PhaseSpace('Fe-Li-O')
            >>> space.in_space('LiNiO2')
            False
            >>> space.in_space('Fe2O3')
            True

        """

        if self.bounds is None:
            return True
        if isinstance(composition, phase.Phase):
            composition = composition.comp
        elif isinstance(composition, basestring):
            composition = parse_comp(composition)

        if set(composition.keys()) <= self.space:
            return True
        else:
            return False

    def in_bounds(self, composition):
        """
        Returns True, if the composition is within the bounds of the phase space

        Examples::

            >>> space = PhaseSpace('Fe2O3-NiO2-Li2O')
            >>> space.in_bounds('Fe3O4')
            False
            >>> space.in_bounds('Li5FeO8')
            True

        """
        if self.bounds is None:
            return True
        if isinstance(composition, phase.Phase):
            composition = composition.unit_comp
        elif isinstance(composition, basestring):
            composition = parse_comp(composition)

        if not self.in_space(composition):
            return False

        composition = dict( (k,v) for k,v in composition.items() if k in
                self.bound_elements )
        composition = unit_comp(composition)

        try:
            c = self.coord(composition)
            if len(self.bounds) < len(self.space):
                comp = self.comp(c)
                if set(comp.keys()) != set(composition.keys())-set(self.mus.keys()):
                    return False
                if not all([abs(comp.get(k,0)- composition.get(k,0)) < 1e-3 for k in
                                                   self.bound_elements]):
                    return False
        except PhaseSpaceError:
            return False
        return True

    ### analysis stuff

    def get_qhull(self, phases=None, mus={}):
        """
        Get the convex hull for a given space.
        """
        if phases is None: ## ensure there are phases to get the hull of
            phases = self.phase_dict.values()

        ## ensure that all phases have negative formation energies
        _phases = []
        for p in phases:
            if not p.use:
                continue
            if self.phase_energy(p) > 0:
                continue
            if not self.in_bounds(p):
                continue
            _phases.append(p)

        phases = _phases

        phase_space = set()
        for p in phases:
            phase_space |= p.space

        A = []
        for p in phases:
            A.append(list(self.coord(p))[1:] + [self.phase_energy(p)])

        dim = len(A[0])
        for i in range(dim):
            tmparr = [ 0 if a != i-1 else 1 for a in range(dim) ]
            if not tmparr in A:
                A.append(tmparr)

        A = np.array(A)
        if len(A) == len(A[0]):
            self._hull = set([frozenset([ p for p in phases])])
            self._tie_lines = set([ frozenset([k1, k2]) for k1, k2 in
                    itertools.combinations(phases, r=2) ])
            self._stable = set([ p for p in phases])
            return
        conv_hull = ConvexHull(A)

        hull = set()
        tie_lines = set()
        stable = set()
        for facet in conv_hull.simplices:
            ### various exclusion rules
            if any([ ind >= len(phases) for ind in facet ]):
                continue

            if all( phases[ind].energy == 0 for ind in facet
                    if ind < len(phases)):
                continue

            dim = len(facet)
            face_matrix = np.array([ A[i] for i in facet ])
            face_matrix[:, -1] = 1
            v = np.linalg.det(face_matrix)

            if abs(v) < 1e-8:
                continue

            face = frozenset([ phases[ind] for ind in facet
                if ind < len(phases)])

            stable |= set(face)
            tie_lines |= set([ frozenset([k1, k2]) for k1, k2 in
                    itertools.combinations(face, r=2)])
            hull.add(Equilibrium(face))

        self._hull = hull
        self._tie_lines = tie_lines
        self._stable = stable
        return hull

    def get_chempot_qhull(self):
        faces = list(self.hull)
        A = []
        for face in faces:
            A.append([face.chem_pots[e] for e in self.elements])
        A = np.array(A)

        conv_hull = ConvexHull(A)

        uhull = set()
        for facet in conv_hull.simplices:
            face = frozenset([ faces[i] for i in facet 
                if i < len(faces) ])
            uhull.add(face)

        return uhull

    def get_hull_points(self):
        """
        Gets out-of PhaseSpace points. i.e. for FeSi2-Li, there are no other
        phases in the space, but there are combinations of Li-Si phases and
        Fe-Si phases. This method returns a list of phases including composite
        phases from out of the space.

        Examples::
            
            >>> space = PhaseSpace('FeSi2-Li')
            >>> space.get_hull_points()
            [<Phase FeSi2 (23408): -0.45110217625>,
            <Phase Li (104737): 0>,
            <Phase 0.680 Li13Si4 + 0.320 FeSi : -0.3370691816>,
            <Phase 0.647 Li8Si3 + 0.353 FeSi : -0.355992801765>,
            <Phase 0.133 Fe3Si + 0.867 Li21Si5 : -0.239436904167>,
            <Phase 0.278 FeSi + 0.722 Li21Si5 : -0.306877209723>]

        """
        self._hull = set() # set of lists
        self._stable = set() # set
        done_list = [] # list of sorted lists
        hull_points = [] # list of phases

        if len(self.phases) == len(self.space):
            self._hull = set(frozenset(self.phases))
            self._stable = set(self.phases)
            return

        for b in self.bounds:
            e, x = self.gclp(b)
            p = phase.Phase.from_phases(x)
            hull_points.append(p)

        facets = [list(hull_points)]
        while facets:
            facet = facets.pop(0)
            done_list.append(sorted(facet))
            try:
                phases, E = self.get_minima(self.phase_dict.values(), facet)
            except:
                continue
            p = phase.Phase.from_phases(phases)
            if p in self.phases:
                p = self.phase_dict[p.name]
            if not p in hull_points:
                hull_points.append(p)
                for new_facet in itertools.combinations(facet, r=len(facet)-1):
                    new_facet = list(new_facet) + [p]
                    if new_facet not in done_list:
                        facets.append(new_facet)
        return hull_points

    def gclp(self, composition={}, mus={}, phases=[]):
        """
        Returns energy, phase composition which is stable at given composition

        Examples::

            >>> space = PhaseSpace('Fe-Li-O')
            >>> energy, phases = space.gclp('FeLiO2')
            >>> print phases
            >>> print energy

        """
        if not composition:
            return 0.0, {}

        if isinstance(composition, basestring):
            composition = parse_comp(composition)
            
        if not phases:
            phases = [ p for p in self.phase_dict.values() if p.use ]

        _mus = self.mus
        if mus is None:
            _mus = {}
        else:
            _mus.update(mus)

        in_phases = []
        space = set(composition.keys()) | set(_mus)
        for p in phases:
            if p.energy is None:
                continue
            #if self.in_bounds(p):
            if not set(p.comp.keys()) <= space:
                continue
            in_phases.append(p)
        ##[vh]
        ##print "in_phases: ", in_phases

        return self._gclp(composition=composition,
                mus=_mus, phases=in_phases)

    def _gclp(self, composition={}, mus={}, phases=[]):
        if not qmpy.FOUND_PULP:
            raise Exception('Cannot do GCLP without installing PuLP and an LP',
                    'solver')
        prob = pulp.LpProblem('GibbsEnergyMin', pulp.LpMinimize)
        phase_vars = pulp.LpVariable.dicts('lib', phases, 0.0)
        prob += pulp.lpSum([ (p.energy -
            sum([ p.unit_comp.get(elt,0)*mu
                for elt, mu in mus.items() ])) * phase_vars[p]
            for p in phases]),\
                    "Free Energy"
        for elt, constraint in composition.items():
            prob += pulp.lpSum([
                p.unit_comp.get(elt,0)*phase_vars[p]
                for p in phases ]) == float(constraint),\
                        'Conservation of '+elt
        ##[vh]
        ##print prob
        if pulp.GUROBI().available():
            prob.solve(pulp.GUROBI(msg=False))
        elif pulp.COIN_CMD().available():
            prob.solve(pulp.COIN_CMD())
        else:
            prob.solve()

        phase_comp = dict([ (p, phase_vars[p].varValue)
            for p in phases if phase_vars[p].varValue > 1e-5])
        
        energy = sum( p.energy*amt for p, amt in phase_comp.items() )
        energy -= sum([ a*composition.get(e, 0) for e,a in mus.items()])
        return energy, phase_comp

    def get_minima(self, phases, bounds):
        """
        Given a set of Phases, get_minima will determine the minimum
        free energy elemental composition as a weighted sum of these
        compounds
        """

        prob = pulp.LpProblem('GibbsEnergyMin', pulp.LpMinimize)
        pvars = pulp.LpVariable.dicts('phase', phases, 0)
        bvars = pulp.LpVariable.dicts('bound', bounds, 0.0, 1.0)
        prob += pulp.lpSum( self.phase_energy(p)*pvars[p] for p in phases ) - \
                pulp.lpSum( self.phase_energy(bound)*bvars[bound] for bound in bounds ), \
                                "Free Energy"
        for elt in self.bound_space:
            prob += sum([ p.unit_comp.get(elt,0)*pvars[p] for p in phases ])\
                        == \
                sum([ b.unit_comp.get(elt, 0)*bvars[b] for b in bounds ]),\
                            'Contraint to the proper range of'+elt
        prob += sum([ bvars[b] for b in bounds ]) == 1, \
                'sum of bounds must be 1'

        if pulp.GUROBI().available():
            prob.solve(pulp.GUROBI(msg=False))
        elif pulp.COIN_CMD().available():
            prob.solve(pulp.COIN_CMD())
        elif pulp.COINMP_DLL().available():
            prob.solve(pulp.COINMP_DLL())
        else:
            prob.solve()

        E = pulp.value(prob.objective)
        xsoln = defaultdict(float,
            [(p, pvars[p].varValue) for p in phases if
                abs(pvars[p].varValue) > 1e-4])
        return xsoln, E

    def compute_hull(self):
        phases = [ p for p in self.phase_dict.values() if (
            self.phase_energy(p) < 0 and len(p.space) > 1 ) ]
        region = Region([self.phase_dict[elt] for elt in self.space ])
        region.contained = phases

    def compute_stability(self, p):
        """
        Compute the energy difference between the formation energy of a Phase,
        and the energy of the convex hull in the absence of that phase. 
        """
        #if self.phase_dict[p.name] != p:
        #    stable = self.phase_dict[p.name]
        #    p.stability = p.energy - stable.energy
        if len(p.comp) == 1:
            stable = self.phase_dict[p.name]
            p.stability = p.energy - stable.energy
        else:
            phases = list(self.phase_dict.values())
            # < Mohan
            # Add Error Handling for phase.remove(p)
            # Old Code:
            # phases.remove(p)
            # New Code:
            try:
                phases.remove(p)
            except ValueError:
                import copy
                _ps_dict = copy.deepcopy(self.phase_dict)
                _ps_dict.pop(p.name, None)
                phases = list(_ps_dict.values())
            # Mohan >
            energy, gclp_phases = self.gclp(p.unit_comp, phases=phases)
            ##print p, energy, gclp_phases
            #vh
            #print p,  '------', gclp_phases
            p.stability = p.energy - energy
            #vh
            return energy, gclp_phases

    @transaction.atomic
    def compute_stabilities(self, phases=None, save=False, reevaluate=True):
        """
        Calculate the stability for every Phase.

        Keyword Arguments:
            phases:
                List of Phases. If None, uses every Phase in PhaseSpace.phases

            save:
                If True, save the value for stability to the database. 

            new_only:
                If True, only compute the stability for Phases which did not
                import a stability from the OQMD. False by default.
        """
        from qmpy.analysis.vasp.calculation import Calculation
        if phases is None:
            phases = self.phases

        if reevaluate:
            for p in self.phases:
                p.stability = None

        for p in phases:
            if p.stability is None:
                if p in self.phase_dict.values():
                    self.compute_stability(p)
                else:
                    p2 = self.phase_dict[p.name]
                    if p2.stability is None:
                        self.compute_stability(p2)
                    base = max(0, p2.stability)
                    diff = p.energy - p2.energy
                    p.stability = base + diff

            if save:
                qs = qmpy.FormationEnergy.objects.filter(id=p.id)
                qs.update(stability=p.stability)

    def save_tie_lines(self):
        """
        Save all tie lines in this PhaseSpace to the OQMD. Stored in
        Formation.equilibrium
        """
        for p1, p2 in self.tie_lines:
            p1.formation.equilibrium.add(p2.formation)

    def compute_formation_energies(self):
        """
        Evaluates the formation energy of every phase with respect to the
        chemical potentials in the PhaseSpace.
        """
        ref = []
        for b in self.bounds:
            if format_comp(b) in self.mus:
                ref.append(self.mus[format_comp[b]])
            else:
                ref.append(self.gclp(b)[0])
        ref = np.array(ref)

        for p in self.phases:
            p.energy = p.energy - sum(self.coord(p) * ref)

    renderer = None
    @property
    def phase_diagram(self, **kwargs):
        """Renderer of a phase diagram of the PhaseSpace"""
        if self.renderer is None:
            self.get_phase_diagram(**kwargs)
        return self.renderer

    @property
    def neighboring_equilibria(self):
        neighbors = []
        for eq1, eq2 in itertools.combinations(self.hull, r=2):
            if eq1.adjacency(eq2) == 1:
                neighbors.append([eq1, eq2])
        return neighbors

    def find_reaction_mus(self, element=None):
        """
        Find the chemical potentials of a specified element at which reactions
        occur. 

        Examples::

            >>> s = PhaseSpace('Fe-Li-O')
            >>> s.find_reaction_mus('O')

        """
        if element is None and len(self.mus) == 1:
            element = self.mus.keys()[0]
        ps = PhaseSpace('-'.join(self.space), data=self.data)
        chem_pots = set()
        for p in ps.stable:
            chem_pots |= set(self.stability_range(p, element))
        return sorted(chem_pots)

    def chempot_scan(self, element=None, umin=None, umax=None):
        """
        Scan through chemical potentials of `element` from `umin` to `umax`
        identifing values at which phase transformations occur.

        """
        if element is None and len(self.mus) == 1:
            element = self.mus.keys()[0]
        mus = self.find_reaction_mus(element=element)
        if umin is None:
            umin = min(mus)
        if umax is None:
            umax = max(mus)

        windows = {}
        hulls = []
        mus = sorted(mus)
        for i in range(len(mus)):
            mu = mus[i]
            if mu < umin or mu > umax:
                continue

            if i == 0:
                nu = mu - 1
                window = (None, mu)
            elif i == len(mus) - 1:
                nu = mu + 1
                window = (mu, None)
            else:
                nu = np.average([mu, mus[i+1]])
                window = (mu, mus[i+1])

            self.mus[element] = nu
            self.get_hull()
            windows[window] = list(self.stable)
        return windows

    def get_phase_diagram(self, **kwargs):
        """
        Creates a Renderer attribute with appropriate phase diagram components.

        Examples::

            >>> space = PhaseSpace('Fe-Li-O')
            >>> space.get_renderer()
            >>> plt.show()

        """
        self.renderer = Renderer()
        if self.shape == (0,0):
            self.make_as_unary(**kwargs)
        elif self.shape == (1,0):
            self.make_as_binary(**kwargs)
        elif self.shape == (2,0):
            self.make_as_ternary(**kwargs)
        elif self.shape == (3,0):
            self.make_as_quaternary(**kwargs)
        elif self.shape == (0,1):
            self.make_1d_vs_chempot(**kwargs)
        elif self.shape == (1,1):
            self.make_vs_chempot(**kwargs)
        else:
            ps = PhaseSpace('-'.join(self.space), data=self.data,
                    load=None)
            ps.renderer = Renderer()
            ps.make_as_graph(**kwargs)
            self.renderer = ps.renderer

    def make_as_unary(self, **kwargs):
        """
        Plot of phase volume vs formation energy.

        Examples::
            
            >>> s = PhaseSpace('Fe2O3')
            >>> r = s.make_as_unary()
            >>> r.plot_in_matplotlib()
            >>> plt.show()

        """
        bottom, gclp = self.gclp(self.bounds[0])
        bottom /= sum(self.bounds[0].values())
        gs = phase.Phase.from_phases(gclp)
        points = []
        for p in self.phases:
            if not self.in_bounds(p):
                continue
            if not p.calculation:
                continue
            v = p.calculation.volume_pa
            pt = Point([v, self.phase_energy(p)-bottom], label=p.label)
            points.append(pt)
            #self.renderer.text.append(Text(pt, p.calculation.entry_id))
        pc = PointCollection(points, color='red')
        self.renderer.add(pc)
        pt = Point([gs.volume, 0], label=gs.label, color='green')
        self.renderer.add(pt)

        xaxis = Axis('x', label='Volume', units="&#8491;<sup>3</sup>/atom")
        yaxis = Axis('y', label='Relative Energy', units='eV/atom')
        self.renderer.xaxis = xaxis
        self.renderer.yaxis = yaxis
        self.renderer.options['grid']['hoverable'] = True
        self.renderer.options['tooltip'] = True

    def make_1d_vs_chempot(self, **kwargs):
        """ 
        Plot of phase stability vs chemical potential for a single composition.

        Examples::
            
            >>> s = PhaseSpace('Fe', mus={'O':[0,-4]})
            >>> r = s.make_vs_chempot()
            >>> r.plot_in_matplotlib()
            >>> plt.show()

        """
        self.make_vs_chempot(**kwargs)
        self.renderer.xaxis.min = 0.5
        self.renderer.xaxis.max = 1.5
        self.renderer.xaxis.options['show'] = False

    def make_vs_chempot(self, **kwargs):
        """
        Plot of phase stability vs chemical potential for a range of
        compositions.

        Examples::
            
            >>> s = PhaseSpace('Fe-Li', mus={'O':[0,-4]})
            >>> r = s.make_vs_chempot()
            >>> r.plot_in_matplotlib()
            >>> plt.show()

        """
        xaxis = Axis('x')
        xaxis.min, xaxis.max = (0, 1)
        xaxis.label = '-'.join([format_comp(b) for b in self.bounds])
        elt = self.mus.keys()[0]
        yaxis = Axis('y', label='&Delta;&mu;<sub>'+elt+'</sub>', units='eV/atom')
        murange = self.mus.values()[0]
        yaxis.min = min(murange)
        yaxis.max = max(murange)
        self.renderer.xaxis = xaxis
        self.renderer.yaxis= yaxis

        if False:
            points = []
            for window, hull in self.chempot_scan().items():
                hull = sorted(hull, key=lambda x: self.coord(x)[0])
                for i in range(len(hull)-1):
                    p1 = hull[i]
                    p2 = hull[i+1]
                    x1 = self.coord(p1)[0]
                    x2 = self.coord(p2)[0]
                    line = Line([Point([x1, window[0], window[1]]),
                                 Point([x2, window[0], window[1]])],
                                 fill=True)
                    self.renderer.add(line)

        ps = PhaseSpace('-'.join(self.space), data=self.data, load=None)
        points = set()
        lines = []
        hlines = set()
        for p in ps.stable:
            if not self.in_bounds(p):
                continue
            bot, top = ps.stability_range(p, elt)
            x = self.coord(p)[0]
            line = Line([Point([x, bot]), Point([x, top])], color='blue')
            lines.append(line)
            hlines |= set([bot, top])
            points.add(Point([x, bot]))
            points.add(Point([x, top]))

            y = np.average([bot, top])
            if y < min(murange):
                y = min(murange)
            elif y > max(murange):
                y = max(murange)
            t = Text([x, y], '<b>%s</b>' % p.name)
            self.renderer.add(t)

        pc = PointCollection(list(points), color='green')

        for h in hlines:
            self.renderer.add(Line([[0,h], [1,h]], color='grey'))

        for l in lines:
            self.renderer.add(l)

        self.renderer.add(pc)

        self.renderer.options['grid']['hoverable'] = True
            
    def make_as_binary(self, **kwargs):
        """
        Construct a binary phase diagram (convex hull) and write it to a
        :mod:`~qmpy.Renderer`.

        Examples::
            
            >>> s = PhaseSpace('Fe-P')
            >>> r = s.make_as_binary()
            >>> r.plot_in_matplotlib()
            >>> plt.show()

        """

        xlabel = '%s<sub>x</sub>%s<sub>1-x</sub>' % (
                format_comp(self.bounds[0]),
                format_comp(self.bounds[1]))
        xaxis = Axis('x', label=xlabel)
        xaxis.min, xaxis.max = (0, 1)
        yaxis = Axis('y', label='Delta H', units='eV/atom')
        self.renderer.xaxis = xaxis
        self.renderer.yaxis = yaxis

        for p1, p2 in self.tie_lines:
            pt1 = Point([self.coord(p1)[0], self.phase_energy(p1)])
            pt2 = Point([self.coord(p2)[0], self.phase_energy(p2)])
            self.renderer.lines.append(Line([pt1, pt2], color='grey'))

        points = []
        for p in self.unstable:
            if not p.use:
                continue
            if self.phase_energy(p) > 0:
                continue
            if not self.in_bounds(p):
                continue
            x = self.coord(p.unit_comp)[0]
            pt = Point([x, self.phase_energy(p)], label=p.label)
            points.append(pt)

        self.renderer.point_collections.append(PointCollection(points,
            fill=1,
            color='red'))

        points = []
        for p in self.stable:
            if not self.in_bounds(p):
                continue
            x = self.coord(p.unit_comp)[0]
            pt = Point([x, self.phase_energy(p)], label=p.label)
            if p.show_label:
                self.renderer.text.append(Text(pt, p.name))
            points.append(pt)
        self.renderer.point_collections.append(PointCollection(points,
                                               fill=True, color='green'))

        self.renderer.options['grid']['hoverable'] = True
        self.renderer.options['tooltip'] = True
        self.renderer.options['tooltipOpts'] = {'content': '%label'}

    def make_as_ternary(self, **kwargs):
        """
        Construct a ternary phase diagram and write it to a
        :mod:`~qmpy.Renderer`.

        Examples::
            
            >>> s = PhaseSpace('Fe-Li-O-P')
            >>> r = s.make_as_quaternary()
            >>> r.plot_in_matplotlib()
            >>> plt.show()

        """

        for p1, p2 in self.tie_lines:
            pt1 = Point(coord_to_gtri(self.coord(p1)))
            pt2 = Point(coord_to_gtri(self.coord(p2)))
            line = Line([pt1, pt2], color='grey')
            self.renderer.lines.append(line)

        points = []
        for p in self.unstable:
            if not self.in_bounds(p):
                continue
            if self.phase_dict[p.name] in self.stable:
                continue
            ##pt = Point(coord_to_gtri(self.coord(p)), label=p.label)
            options = {'hull_distance': p.stability}
            pt = Point(coord_to_gtri(self.coord(p)), label=p.label, **options)
            points.append(pt)
        self.renderer.point_collections.append(PointCollection(points,
            fill=True, color='red'))

        self.renderer.options['xaxis']['show'] = False
        points = []
        for p in self.stable:
            if not self.in_bounds(p):
                continue
            pt = Point(coord_to_gtri(self.coord(p)), label=p.label)
            if p.show_label:
                self.renderer.add(Text(pt, p.name))
            points.append(pt)
        self.renderer.point_collections.append(PointCollection(points,
            fill=True,
            color='green'))

        self.renderer.options['grid']['hoverable'] = True, 
        self.renderer.options['grid']['borderWidth'] = 0
        self.renderer.options['grid']['margin'] = 4
        self.renderer.options['grid']['show'] = False
        self.renderer.options['tooltip'] = True

    def make_as_quaternary(self, **kwargs):
        """
        Construct a quaternary phase diagram and write it to a
        :mod:`~qmpy.Renderer`.

        Examples::
            
            >>> s = PhaseSpace('Fe-Li-O-P')
            >>> r = s.make_as_quaternary()
            >>> r.plot_in_matplotlib()
            >>> plt.show()

        """
        #plot lines
        for p1, p2 in self.tie_lines:
            pt1 = Point(coord_to_gtet(self.coord(p1)))
            pt2 = Point(coord_to_gtet(self.coord(p2)))
            line = Line([pt1, pt2], color='grey')
            self.renderer.add(line)

        #plot compounds
        ### < Mohan
        # Use phase_dict to collect unstable phases, which will 
        # return one phase per composition
        points = []
        for c, p in self.phase_dict.items():
            if not self.in_bounds(p):
                continue
            if p in self.stable:
                continue
            label = '{}<br> hull distance: {:.3f} eV/atom<br> formation energy: {:.3f} eV/atom'.format(
                p.name, p.stability, p.energy
            )
            pt = Point(coord_to_gtet(self.coord(p)), label=label)
            points.append(pt)
        self.renderer.add(PointCollection(points, 
                                          color='red', label='Unstable'))

        ## Older codes:
        #for p in self.unstable:
        #    if not self.in_bounds(p):
        #        continue
        #    pt = Point(coord_to_gtet(self.coord(p)), label=p.name)
        #    points.append(pt)
        #self.renderer.add(PointCollection(points, 
        #                                  color='red', label='Unstable'))
        ### Mohan >

        points = []
        for p in self.stable:
            if not self.in_bounds(p):
                continue
            label = '%s:<br>- ' % p.name
            label += ' <br>- '.join(o.name for o in self.graph[p].keys())
            pt = Point(coord_to_gtet(self.coord(p)), label=label)
            points.append(pt)
            if p.show_label:
                self.renderer.add(Text(pt, format_html(p.comp)))
        self.renderer.add(PointCollection(points, 
                                          color='green', label='Stable'))

        self.renderer.options['grid']['hoverable'] = True, 
        self.renderer.options['grid']['borderWidth'] = 0
        self.renderer.options['grid']['show'] = False
        self.renderer.options['tooltip'] = True

    def make_as_graph(self, **kwargs):
        """
        Construct a graph-style visualization of the phase diagram.
        """
        G = self.graph
        positions = nx.drawing.nx_agraph.pygraphviz_layout(G)
        for p1, p2 in self.tie_lines:
            pt1 = Point(positions[p1])
            pt2 = Point(positions[p2])
            line = Line([pt1, pt2], color='grey')
            self.renderer.add(line)

        points = []
        for p in self.stable:
            label = '%s:<br>' % p.name
            for other in G[p].keys():
                label += '  -%s<br>' % other.name
            pt = Point(positions[p], label=label)
            points.append(pt)
            if p.show_label:
                self.renderer.add(Text(pt, p.name))
        pc = PointCollection(points, color='green')
        self.renderer.add(pc)

        self.renderer.options['grid']['hoverable'] = True
        self.renderer.options['grid']['borderWidth'] = 0
        self.renderer.options['grid']['show'] = False
        self.renderer.options['tooltip'] = True

    def stability_window(self, composition, **kwargs):
        self.renderer = Renderer()
        chem_pots = self.chempot_bounds(composition)
        for eq, pots in chem_pots.items():
            pt = Point(coord_to_point([ pots[k] for k in self.elements ]))
            self.renderer.add(pt)

    def get_reaction(self, var, facet=None):
        """
        For a given composition, what is the maximum delta_composition reaction
        on the given facet. If None, returns the whole reaction for the given
        PhaseSpace.

        Examples::

            >>> space = PhaseSpace('Fe2O3-Li2O')
            >>> equilibria = space.hull[0]
            >>> space.get_reaction('Li2O', facet=equilibria)

        """

        if isinstance(var, basestring):
            var = parse_comp(var)

        if facet:
            phases = facet
        else:
            phases = self.stable

        prob = pulp.LpProblem('BalanceReaction', pulp.LpMaximize)
        pvars = pulp.LpVariable.dicts('prod', phases, 0)
        rvars = pulp.LpVariable.dicts('react', phases, 0)
        prob += sum([ p.fraction(var)['var']*pvars[p] for p in phases ])-\
                sum([ p.fraction(var)['var']*rvars[p] for p in phases ]),\
                "Maximize delta comp"
        for celt in self.space:
            prob += sum([ p.fraction(var)[celt]*pvars[p] for p in phases ]) ==\
                    sum([ p.fraction(var)[celt]*rvars[p] for p in phases ]),\
                    'identical %s composition on both sides' % celt
        prob += sum([ rvars[p] for p in phases ]) == 1
        
        if pulp.GUROBI().available():
            prob.solve(pulp.GUROBI(msg=False))
        elif pulp.COIN_CMD().available():
            prob.solve(pulp.COIN_CMD())
        elif pulp.COINMP_DLL().available():
            prob.solve(pulp.COINMP_DLL())
        else:
            prob.solve()

        prods = defaultdict(float,[ (c, pvars[c].varValue) for c in phases
            if pvars[c].varValue > 1e-4 ])
        reacts = defaultdict(float,[ (c, rvars[c].varValue) for c in phases
            if rvars[c].varValue > 1e-4 ])
        n_elt = pulp.value(prob.objective)
        return reacts, prods, n_elt

    def get_reactions(self, var, electrons=1.0):
        """
        Returns a list of Reactions.

        Examples::

            >>> space = PhaseSpace('Fe-Li-O')
            >>> space.get_reactions('Li', electrons=1)

        """
        if isinstance(var, basestring):
            var = parse_comp(var)
        vname = format_comp(reduce_comp(var))
        vphase = self.phase_dict[vname]
        vpd = dict( (self.phase_dict[k], v) for k,v in var.items() )
        for facet in self.hull:
            reacts, prods, delta_var = self.get_reaction(var, facet=facet)
            if vphase in facet:
                yield Reaction(
                    products={vphase:sum(vphase.comp.values())}, 
                    reactants={}, delta_var=1.0,
                    electrons=electrons, variable=var)
                continue
            elif delta_var < 1e-6:
                pass
            yield Reaction(products=prods, reactants=reacts, 
                delta_var=delta_var,
                variable=var, electrons=electrons)

    def plot_reactions(self, var, electrons=1.0, save=False):
        """
        Plot the convex hull along the reaction path, as well as the voltage
        profile.
        """
        if isinstance(var, basestring):
            var = parse_comp(var)
        vname = format_comp(var)

        fig = plt.figure()
        ax1 = fig.add_subplot(211)

        #plot tie lines
        for p1, p2 in self.tie_lines:
            c1 = p1.fraction(var)['var']
            c2 = p2.fraction(var)['var']
            if abs(c1) < 1e-4 or abs(c2) < 1e-4:
                if abs(c1 - 1) < 1e-4 or abs(c2 - 1) < 1e-4:
                    if len(self.tie_lines) > 1:
                        continue
            ax1.plot([c1,c2], [self.phase_energy(p1),
                               self.phase_energy(p2)], 'k')

        #plot compounds
        for p in self.stable:
            x = p.fraction(var)['var']
            ax1.plot(x, self.phase_energy(p), 'bo')
            ax1.text(x, self.phase_energy(p), '$\\rm{%s}$' % p.latex,
                            ha='left', va='top')
        plt.ylabel('$\\rm{\Delta H}$ $\\rm{[eV/atom]}$')
        ymin, ymax = ax1.get_ylim()
        ax1.set_ylim(ymin - 0.1, ymax)

        ax2 = fig.add_subplot(212, sharex=ax1)
        points = set()
        for reaction in self.get_reactions(var, electrons=electrons):
            if reaction.delta_var == 0:
                continue
            voltage = reaction.delta_h/reaction.delta_var/electrons
            x1 = reaction.r_var_comp
            x2 = reaction.p_var_comp
            points |= set([(x1, voltage), 
                    (x2, voltage)])

        points = sorted( points, key=lambda x: x[0] )
        points = sorted( points, key=lambda x: -x[1] )
        #!v
        #print points

        base = sorted(self.stable, key=lambda x:
                x.amt(var)['var'])[0]

        max_x = max([ k[0] for k in points ])

        if len(points) > 1:
            for i in range(len(points) - 2):
                ax2.plot([points[i][0], points[i+1][0]],
                        [points[i][1], points[i+1][1]], 'k')

            ax2.plot([points[-2][0], points[-2][0]], 
                    [points[-2][1], points[-1][1]], 'k')
            ax2.plot([points[-2][0], max_x], 
                    [points[-1][1], points[-1][1]], 'k')
        else:
            ax2.plot([0, max_x], [points[0][1], points[0][1]], 'k')
        
        plt.xlabel('$\\rm{x}$ $\\rm{in}$ $\\rm{(%s)_{x}(%s)_{1-x}}$' % ( 
           format_latex(var),
            base.latex))
        plt.ylabel('$\\rm{Voltage}$ $\\rm{[V]}$')

        return ax1, ax2

        #if not save:
        #    plt.show()
        #else:
        #    plt.savefig('%s-%s.eps' % (save, vname),
        #            bbox_inches='tight', 
        #            transparent=True,
        #            pad_inches=0) 
