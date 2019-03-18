# qmpy/materials/entry.py

from datetime import datetime
import time
import os

from django.db import models
from django.db import transaction
import networkx as nx

from qmpy.db.custom import *
from qmpy.materials.composition import *
from qmpy.materials.element import Element, Species
from qmpy.materials.structure import Structure, StructureError
from qmpy.utils import *
from qmpy.computing.resources import Project
from qmpy.data.meta_data import *
import qmpy.io as io
import qmpy.computing.scripts as scripts
import qmpy.analysis.vasp as vasp

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

k_desc = 'Descriptive keyword for looking up entries'
h_desc = 'A note indicating a reason the entry should not be calculated'
@add_meta_data('keyword', description=k_desc)
@add_meta_data('hold', description=h_desc)
class Entry(models.Model):
    """Base class for a database entry.

    The core model for typical database entries. An Entry model represents an
    input structure to the database, and can be created from any input file.
    The Entry also ties together all of the associated :mod:`qmpy.Structure`,
    :mod:`qmpy.Calculation`, :mod:`qmpy.Reference`,
    :mod:`qmpy.FormationEnergies`, and other associated databas entries.

    Relationships:
        | :mod:`~qmpy.Calculation` via calculation_set
        | :mod:`~qmpy.DOS` via dos_set
        | :mod:`~qmpy.Entry` via duplicate_of
        | :mod:`~qmpy.Entry` via duplicates
        | :mod:`~qmpy.Element` via element_set
        | :mod:`~qmpy.FormationEnergy` via formationenergy_set
        | :mod:`~qmpy.Job` via job_set
        | :mod:`~qmpy.MetaData` via meta_data
        | :mod:`~qmpy.Project` via project_set
        | :mod:`~qmpy.Prototype` via prototype
        | :mod:`~qmpy.Species` via species_set
        | :mod:`~qmpy.Structure` via structure_set
        | :mod:`~qmpy.Task` via task_set
        | :mod:`~qmpy.Reference` via reference
        | :mod:`~qmpy.Composition` via composition

    Attributes:
        | id: Primary key (auto-incrementing int)
        | label: An identifying name for the structure. e.g. icsd-1001 or A3

    """
    ### structure properties
    path = models.CharField(max_length=255, unique=True)
    meta_data = models.ManyToManyField('MetaData')
    label = models.CharField(max_length=20, null=True)

    ### record keeping
    duplicate_of = models.ForeignKey('Entry', related_name='duplicates',
            null=True)
    ntypes = models.IntegerField(blank=True, null=True)
    natoms = models.IntegerField(blank=True, null=True)

    ### links
    element_set = models.ManyToManyField('Element')
    species_set = models.ManyToManyField('Species')
    project_set = models.ManyToManyField('Project')
    composition = models.ForeignKey('Composition', blank=True, null=True)
    reference = models.ForeignKey('Reference', null=True, blank=True)
    prototype = models.ForeignKey('Prototype', null=True, blank=True)

    class Meta:
        app_label = 'qmpy'
        db_table = 'entries'

    def __str__(self):
        return '%s - %s' % (self.id, self.name)

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Saves the Entry, as well as all associated objects."""
        if not self.reference is None:
            if self.reference.id is None:
                self.reference.save()
                self.reference = self.reference
        super(Entry, self).save(*args, **kwargs)
        if self._structures:
            for k, v in self.structures.items():
                v.label = k
                v.entry = self
                v.save()
            #self.structure_set = self.structures.values()
        if self._calculations:
            for k, v in self.calculations.items():
                v.label = k
                v.entry = self
                v.save()
            #self.calculation_set = self.calculations.values()
        if self._elements:
            self.element_set = self.elements
        if self._species:
            self.species_set = self.species
        if self._projects:
            self.project_set = self.projects
        if self._keywords or self._holds:
            self.meta_data = self.hold_objects + self.keyword_objects

    @staticmethod
    def create(source, keywords=[], projects=[], prototype=None, **kwargs):
        """
        Attempts to create an Entry object from a provided input file.

        Processed in the following way:

        #. If an Entry exists at the specified path, returns that Entry.
        #. Create an Entry, and assign all fundamental attributes. (natoms,
           ntypes, input, path, elements, keywords, projects).
        #. If the input file is a CIF, and because CIF files have additional
           composition and reference information, if that file format is
           found, an additional test is performed to check that the reported
           composition matches the composition of the resulting structure. The
           reference for the work is also created and assigned to the entry.
        #. Attempt to identify another entry that this is either exactly
           equivalent to, or a defect cell of.

        Keywords:
            keywords: list of keywords to associate with the entry.
            projects: list of project names to associate with the entry.

        """
        source_file = os.path.abspath(source)
        path = os.path.dirname(source_file)

        # Step 1
        if Entry.objects.filter(path=path).exists():
            return Entry.objects.get(path=path)

        # Step 2
        entry = Entry(**kwargs)
        try:
            structure = io.poscar.read(source_file)
        except ValueError:
            structure = io.cif.read(source_file)
        structure.make_primitive()
        entry.source_file = source_file
        entry.path = os.path.dirname(source_file)
        entry.input = structure
        entry.ntypes = structure.ntypes
        entry.natoms = len(structure.sites)
        entry.elements = entry.comp.keys()
        entry.composition = Composition.get(structure.comp)
        for kw in keywords:
            entry.add_keyword(kw)
        entry.projects = projects
        entry.prototype = prototype

        # Step 3
        c1 = structure.composition
        if 'cif' in source_file:
            c2 = structure.reported_composition
            if not c1.compare(c2, 5e-2):
                entry.add_hold("composition mismatch in cif")
                entry.composition = c2
            entry.reference = io.cif.read_reference(source_file)

        # check for perfect crystals
        if not any([ s.partial for s in structure.sites ]):
            dup = Entry.get(structure)
            if not dup is None:
                entry.duplicate_of = dup
                entry.add_hold('duplicate')
            return entry

        # detect solid solution
        if all([ s.occupancy > 0.99 for s in structure.sites ]):
            if any([ len(s) > 1 for s in structure.sites ]):
                entry.add_keyword('solid solution')
        if any([ s.partial for s in structure.sites ]):
            entry.add_hold('partial occupancy')

        return entry

    @staticmethod
    def get(structure, tol=1e-1):
        if isinstance(structure, Structure):
            return Entry.search_by_structure(structure, tol=tol)

    @staticmethod
    def search_by_structure(structure, tol=1e-2):
        c = Composition.get(structure.comp)
        for e in c.entries:
            if e.structure.compare(structure, tol=tol):
                return e
        return None

    _elements = None
    @property
    def elements(self):
        """List of Elements"""
        if self._elements is None:
            self._elements = [ Element.get(e) for e in self.comp.keys() ]
        return self._elements

    @elements.setter
    def elements(self, elements):
        self._elements = [ Element.get(e) for e in elements ]

    _species = None
    @property
    def species(self):
        """List of Species"""
        if self._species is None:
            self._species = [ Species.get(s) for s in self.spec_comp.keys() ]
        return self._species

    @species.setter
    def species(self, species):
        self._species = [ Species.get(e) for e in species ]

    _projects = None
    @property
    def projects(self):
        """List of Projects"""
        if self._projects is None:
            self._projects = list(self.project_set.all())
        return self._projects

    @projects.setter
    def projects(self, projects):
        self._projects = [ Project.get(p) for p in projects ]

    _structures = None
    @property
    def structures(self):
        if self._structures is None:
            if self.id is None:
                self._structures = {}
            else:
                structs = {}
                for s in self.structure_set.exclude(label=''):
                    structs[s.label] = s
                self._structures = structs
        return self._structures
    s = structures

    @structures.setter
    def structures(self, structs):
        if not isinstance(structs, dict):
            raise TypeError('structures must be a dict')
        if not all( isinstance(v, Structure) for v in structs.values()):
            raise TypeError('structures must be a dict of Calculations')
        self._structures = structs

    @structures.deleter
    def structures(self, struct):
        self._structures[struct].delete()
        del self._structures[struct]


    _calculations = None
    @property
    def calculations(self):
        """Dictionary of label:Calculation pairs."""
        if self._calculations is None:
            if self.id is None:
                self._calculations = {}
            else:
                calcs = {}
                for c in self.calculation_set.exclude(label=''):
                    calcs[c.label] = c
                self._calculations = calcs
        return self._calculations
    c = calculations

    @calculations.setter
    def calculations(self, calcs):
        if not isinstance(calcs, dict):
            raise TypeError('calculations must be a dict')
        if not all( isinstance(v, vasp.Calculation) for v in calcs.values()):
            raise TypeError('calculations must be a dict of Calculations')
        self._calculations = calcs

    @calculations.deleter
    def calculations(self, calc):
        self._calculations[calc].delete()
        del self._calculations[calc]

    @property
    def input(self):
        return self.structures.get('input')

    @property
    def structure(self):
        if 'final' in self.structures:
            return self.structures['final']
        elif 'relaxed' in self.structures:
            return self.structures['relaxed']
        elif 'relaxation' in self.structures:
            return self.structures['relaxation']
        elif 'standard' in self.structures:
            return self.structures['standard']
        elif 'fine_relax' in self.structures:
            return self.structures['fine_relax']
        else:
            try:
                return self.structures['input']
            except KeyError:
                return None

    @input.setter
    def input(self, structure):
        self.structures['input'] = structure

    @property
    def tasks(self):
        return list(self.task_set.all())
    @property
    def jobs(self):
        return list(self.job_set.all())

    @property
    def comp(self):
        if not self.composition_id is None:
            return parse_comp(self.composition_id)
        elif not self.input is None:
            return self.input.comp
        else:
            return {}

    @property
    def spec_comp(self):
        """
        Composition dictionary, using species (element + oxidation state)
        instead of just the elements.

        """
        if self.input is None:
            return {}
        else:
            return self.input.spec_comp

    @property
    def unit_comp(self):
        """Composition dictionary, normalized to 1 atom."""
        return unit_comp(self.comp)

    @property
    def red_comp(self):
        """Composition dictionary, in reduced form."""
        return reduce_comp(self.comp)

    @property
    def name(self):
        """Unformatted name"""
        return format_comp(reduce_comp(self.comp))

    @property
    def latex(self):
        """LaTeX formatted name"""
        return format_latex(reduce_comp(self.comp))

    @property
    def html(self):
        """HTML formatted name"""
        return format_html(reduce_comp(self.comp))

    @property
    def proto_label(self):
        #if not self.prototype is None:
        #    return self.prototype.name
        protos = []
        for e in self.duplicates.all():
            if not e.prototype is None:
                protos.append(e.prototype.name)

        protos = list(set(protos))
        if len(protos) == 1:
            return protos[0]
        else:
            return ', '.join(protos)

    @property
    def space(self):
        """Return the set of elements in the input structure.

        Examples::

            >>> e = Entry.create("fe2o3/POSCAR") # an input containing Fe2O3
            >>> e.space
            set(["Fe", "O"])

        """
        return set([ e.symbol for e in self.elements])

    @property
    def total_energy(self):
        """
        If the structure has been relaxed, returns the formation energy of the
        final relaxed structure. Otherwise, returns None.

        """
        es = []
        if 'static' in self.calculations:
            if self.calculations['static'].converged:
                return self.calculations['static'].energy_pa
                #es.append(self.calculations['static'].energy_pa)
        if 'standard' in self.calculations:
            if self.calculations['standard'].converged:
                return self.calculations['standard'].energy_pa
                #es.append(self.calculations['standard'].energy_pa)
        if not es:
            return None
        #else:
        #    return min(es)

    _energy = None
    @property
    def energy(self):
        """
        If the structure has been relaxed, returns the formation energy of the
        final relaxed structure. Otherwise, returns None.
        """
        if self._energy is None:
            fes = self.formationenergy_set.filter(fit='standard').order_by('delta_e')
            if fes.exists():
                self._energy = fes[0].delta_e
            #if 'static' in self.calculations:
            #    if self.calculations['static'].converged:
            #        de = self.calculations['static'].formation_energy()
            #        self._energy = de
            #elif 'standard' in self.calculations:
            #    if self.calculations['standard'].converged:
            #        de = self.calculations['standard'].formation_energy()
            #        self._energy = de
        return self._energy

    @property
    def stable(self):
        forms = self.formationenergy_set.filter(fit='standard')
        forms = forms.exclude(stability=None)
        if not forms.exists():
            return None
        return any([ f.stability <= 1E-3 for f in forms ])
        

    _history = None
    @property
    def history_graph(self):
        if self._history is None:
            G = nx.Graph()

            for c in self.calculation_set.all():
                G.add_edge(c.input, c.output, object=c)
            self._history = G
        return self._history

    @property
    def history(self):
        steps = []
        if 'static' in self.calculations:
            step = self.calculations['static']
        elif 'standard' in self.calculations:
            step = self.calculations['standard']
        while step:
            if isinstance(step, vasp.Calculation):
                step.type = 'calculation'
                steps.append(step)
                step = step.input
            if isinstance(step, Structure):
                step.type = 'structure'
                steps.append(step)
                try:
                    step = step.source.all()[0]
                except:
                    step = None
        return steps

    @property
    def spacegroup(self):
        return self.structure.spacegroup

    @property
    def mass(self):
        """Return the mass of the entry, normalized to per atom."""
        return sum( Element.objects.get(symbol=elt).mass*amt for 
                elt, amt in self.unit_comp)

    @property
    def volume(self):
        """
        If the entry has gone through relaxation, returns the relaxed
        volume. Otherwise, returns the input volume.
        
        """
        if not self.relaxed is None:
            return self.relaxed.volume/self.natoms
        else:
            return self.input.volume/self.natoms

    @property
    def errors(self):
        """List of errors encountered in all calculations."""
        return dict( ( c.path, c.errors) for c in
                self.calculation_set.all() )

    @property
    def chg(self):
        """
        Attempts to load the charge density of the final calculation, if it is
        done. If not, returns False.

        """
        if not hasattr(self, '_chg'):
            if not self.done:
                self._chg = False
            else:
                self._chg = Grid.load_xdensity(self.path+'/standard/CHGCAR.gz')
        return self._chg

    def do(self, module, *args, **kwargs):
        """
        Looks for a computing script matching the first argument, and attempts
        to run it with itself as the first argument. Sends args and kwargs
        to the script. Should return a Calculation object, or list of
        Calculation objects. 

        Examples::

            >>> e = Entry.objects.get(id=123)
            >>> e.do('relaxation')
            <Calculation: 523 @ relaxation settings>

        """
        script = getattr(scripts, module)
        return script(self, *args, **kwargs)

    @transaction.atomic
    def move(self, path):
        """
        Moves all calculation files to the specified path.

        """
        path = os.path.abspath(path)
        try:
            os.system('mv %s %s' % (self.path, path))
        except Exception, err:
            logger.warn(err)
            return
        old_path = self.path
        old_base = os.path.basename(os.path.abspath(old_path.strip('/')))
        en_newpath = os.path.join(path, old_base)
        Entry.objects.filter(id=self.id).update(path=en_newpath)
        self.save()
        #labels = [ c.label.strip('_[0-9]') for c in self.calculation_set.all() ]
        for calc in self.calculation_set.all():
            calc_base = os.path.basename(calc.path.strip('/'))
            if calc_base != calc.label.strip('_[0-9]'):
                calc_base = os.path.join(calc.label.strip('_[0-9]'), calc_base)
            newpath = os.path.join(self.path, calc_base)
            #newpath = calc.path.replace(old_path, path)
            vasp.Calculation.objects.filter(id=calc.id).update(path=newpath)
        logger.info('Moved %s to %s', self, path)

    @property
    def running(self):
        return self.job_set.filter(state=1)

    @property
    def todo(self):
        return self.task_set.filter(state=0)

    def wipe(self):
        self.structure_set.exclude(label='input').delete()
        self.calculation_set.all().delete()
        self.task_set.update(state=0)

    def reset(self):
        """
        Deletes all calculations, removes all associated structures - returns
        the entry to a pristine state.

        """

        self.structure_set.exclude(label='input').delete()
        self._structures = None

        self.calculation_set.all().delete()
        self._calculations = None

        for task in self.tasks:
            task.state = 0 
            task.save()

        for job in self.job_set.filter(state=1):
            job.collect()
            job.delete()

        self.job_set.all().delete()

        for dir in os.listdir(self.path):
            if os.path.isdir(self.path+'/'+dir):
                logger.debug('rm -rf %s/%s &> /dev/null', self.path, dir)
                os.system('rm -rf %s/%s &> /dev/null' % (self.path, dir))

    def visualize(self, structure='source'):
        """Attempts to open the input structure for visualization using VESTA"""
        os.system('VESTA %s/POSCAR' % self.path)

