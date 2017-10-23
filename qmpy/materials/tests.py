from qmpy import *
import time
import tempfile
import shutil
from django.test import TestCase
from django.db.models import F

class ElementTestCase(TestCase):
    def setUp(self):
        read_elements()

    def test_get(self):
        fe = Element.get('Fe')
        elements = open(INSTALL_PATH+'/data/elements/data.yml').read()
        elements = yaml.load(elements)
        for k, v in elements.items():
            elt = Element.get(k)
            self.assertEqual(elt.z, v['z'])
            self.assertEqual(elt.symbol, v['symbol'])
            self.assertEqual(elt.production, v['production'])
            self.assertEqual(elt.mass, v['mass'])

class AtomTestCase(TestCase):
    def setUp(self):
        self.a1 = Atom.create('Fe', [0,0,0], forces=[0, 1, 2], ox=3)
        self.a1p = Atom.create('Fe', [0,0,0])
        self.a2 = Atom.create('Fe', [0,0,0])
        self.a3 = Atom.create('Ni', [0,0,0])
        self.a4 = Atom.create('Fe', [0.5,0.5,0.5])
        self.a5 = Atom.create('Fe', [0.5,0.5,0.5])
        self.a7 = Atom.create('O', [0,0,0], ox=-2)
        self.s1 = Structure.create(cell=[[3,0,0],[0,3,0],[0,0,3]])
        self.s2 = Structure.create(cell=[[4,0,0],[0,3,0],[0,0,3]])
        self.s1.atoms = [self.a1, self.a1p, self.a3]
        self.s2.atoms = [self.a2, self.a4]

    def test_equal(self):
        self.assertTrue(self.a1 == self.a1p)
        self.assertTrue(self.a1 == self.a2)
        self.assertTrue(self.a1 != self.a3)

    def test_create(self):
        atom = Atom(element_id='Fe', x=0, y=0, z=0, fx=0, fy=0, fz=0)
        created = Atom.create('Fe', [0,0,0])
        created.forces = [0, 1, 2]
        self.assertEqual( atom, created )

    def test_index(self):
        self.assertEqual(self.a1.index, 0)
        self.assertEqual(self.a3.index, 1)

    def test_cart(self):
        self.assertTrue(np.allclose(self.a4.coord, [0.5,0.5,0.5]))
        self.assertTrue(np.allclose(self.a4.cart_coord, [2,1.5,1.5]))
        with self.assertRaises(AtomError):
            self.a5.cart_coord
        self.a4.cart_coord = [3,2,1]
        self.assertTrue(np.allclose(self.a4.cart_coord, [3,2,1]))
        self.assertTrue(np.allclose(self.a4.coord, 
                         [ 0.75 , 0.66666667, 0.333333333]))

    def test_species(self):
        self.assertEqual(self.a1.species, 'Fe3+')
        self.assertEqual(self.a7.species, 'O2-')

class CompositionTestCase(TestCase):
    def setUp(self):
        read_elements()

    def test_get(self):
        for c, a in [ ('Fe2O3', {'Fe':2, 'O':3}),
                      ('In1As1', {'In':1, 'As':1}),
                      ('Fe0.3333O0.666666', {'Fe':1, 'O':2})]:
            comp = Composition.get(c)

            self.assertEqual(comp.comp, a)
            self.assertEqual(comp.space, set(a.keys()))

class StructureTestCase(TestCase):
    def setUp(self):
        read_elements()
        read_spacegroups([229, 221, 225, 216])

        self.bcc = io.read(INSTALL_PATH+'/io/files/POSCAR_BCC')
        self.fcc = io.read(INSTALL_PATH+'/io/files/POSCAR_FCC')
        self.nacl = io.read(INSTALL_PATH+'/io/files/POSCAR_NaCl')
        self.cscl = io.read(INSTALL_PATH+'/io/files/POSCAR_CsCl')
        self.zns = io.read(INSTALL_PATH+'/io/files/POSCAR_ZnS')

    def test_name(self):
        self.assertEqual(str(self.bcc), 'Cu')
        self.assertEqual(str(self.fcc), 'Fe')
        self.assertEqual(str(self.nacl), 'NaCl')
        self.assertEqual(str(self.zns), 'ZnS')

    def test_transformations(self):

        # transform
        self.assertTrue(np.allclose(self.bcc.cell,3*np.eye(3)))

        # simple multiplication along lattice
        self.bcc.transform([2,1,1])
        self.assertTrue(np.allclose(self.bcc.cell,[6,3,3]*np.eye(3)))
        self.assertTrue(np.allclose(self.bcc.coords, [[0,0,0],
                                                      [0.25,0.5,0.5],
                                                      [0.5,0,0],
                                                      [0.75,0.5,0.5]]))
        self.bcc.transform([0.5,1,1])
        self.assertTrue(np.allclose(self.bcc.cell,3*np.eye(3)))

        self.zns.transform([[2,-1,1],[0,1,1],[-1,2,2]])
        self.assertTrue(np.allclose([[0.0, 8.208183, 2.736061], 
                                     [5.472122, 2.736061, 2.736061], 
                                     [10.944244, 2.736061, 2.736061]],
                                     self.zns.cell))
        self.assertTrue(np.allclose(self.zns.coords,[[0.0, 0.0, 0.0],
                                                     [0.0, 0.75, 0.75],
                                                     [0.5, 0.5, 0.0],
                                                     [0.5, 0.25, 0.75]]))

        natoms = len(self.fcc) * roundclose(la.det([[1,1,0],[-1,2,1],[0,1,2]]))
        new = self.fcc.transform([[1,1,0],[-1,2,1],[0,1,2]], in_place=False)
        self.assertEqual(len(new), natoms)
        right = io.read(INSTALL_PATH+'/io/files/POSCAR_trans')
        new.sort()
        right.sort()
        self.assertTrue(np.allclose(new.coords, right.coords))
        self.assertTrue(np.allclose(new.cell, right.cell))
        self.assertEqual(new, self.fcc)

        # translate
        new = self.fcc.recenter(1, in_place=False)
        self.assertTrue(np.allclose(new.coords[0], [0.5,0.5,0.0]))
        self.assertEqual(new, self.fcc)

        new = self.fcc.translate([0.5,0.1,-0.9], in_place=False)
        self.assertTrue(np.allclose(new.coords[0], 
            [ 0.13794435, 0.02758887, 0.75170016]))
        self.assertEqual(self.fcc, new)


    def test_substitute(self):
        s2 = self.nacl.substitute({'Na': 'Cs'}, rescale=False)
        s3 = self.nacl.sub({'Na': 'Cs'}, rescale=True,
                                         rescale_method="relative")
        s4 = self.nacl.replace({'Na': 'Cs'}, rescale=True,
                                             rescale_method="absolute")
        self.assertEqual(str(s2), 'CsCl')
        self.assertEqual(str(s3), 'CsCl')
        self.assertEqual(str(s4), 'CsCl')

        self.assertFalse(self.cscl.compare(s2, volume=True))
        self.assertTrue(self.cscl.compare(s3, volume=True))
        self.assertTrue(self.cscl.compare(s4, volume=True))

    def test_compare(self):
        zns2 = self.zns.copy()
        zns2.transform([[2,-1,-1],[1,2,0],[0,0,1]])
        zns2.translate([0.41, -0.14, 0.74], cartesian=False)
        self.assertTrue(zns2, self.zns)

class EntryTestCase(TestCase):
    def setUp(self):
        read_elements()
        read_spacegroups([62, 74, 225, 123])
        self.dirs = {}
        self.entries = {}
        for f in ['POSCAR_FCC', 'POSCAR_FCC2', 'partial.cif',
                     'perfect.cif', 'partial_mix.cif', 'partial_vac.cif']:
            tdir = tempfile.mkdtemp(dir='/tmp/')
            shutil.copy(INSTALL_PATH+'/io/files/'+f, tdir)
            self.dirs[f] = tdir
            self.entries[f] = Entry.create(tdir+'/'+f)

    def tearDown(self):
        for d in self.dirs.values():
            for f in os.listdir(d):
                os.remove(d+'/'+f)
            os.removedirs(d)

    def test_create(self):
        # normal
        entry = Entry.create(self.dirs['POSCAR_FCC']+'/POSCAR_FCC')
        self.assertEqual(entry.holds, [])
        self.assertEqual(entry.keywords, [])
        entry.save()

        # duplicate
        ##entry = Entry.create(self.dirs['POSCAR_FCC2']+'/POSCAR_FCC2')
        ##self.assertEqual(entry.holds, ['duplicate'])
        ##self.assertEqual(entry.keywords, [])
        ##entry.save()
        #TODO: hegdevinayi@gmail.com. Fix the issue of duplicate_of

        # solid solution
        entry = Entry.create(self.dirs['partial.cif']+'/partial.cif')
        self.assertEqual(set(entry.holds), set(['partial occupancy', 
                                       'composition mismatch in cif']))
        self.assertEqual(entry.keywords, [])
        entry.save()

        # perfect reference structure
        perfect = Entry.create(self.dirs['perfect.cif']+'/perfect.cif')
        self.assertEqual(perfect.holds, [])
        self.assertEqual(perfect.keywords, [])
        perfect.save()

        # vacancies
        entry = Entry.create(self.dirs['partial_vac.cif']+'/partial_vac.cif')
        self.assertEqual(set(entry.holds), set(['partial occupancy',
                                           'composition mismatch in cif']))
        self.assertEqual(entry.keywords, [])
        #self.assertEqual(entry.duplicate_of.id, perfect.id)

        # anti-site defects
        entry = Entry.create(self.dirs['partial_mix.cif']+'/partial_mix.cif')
        self.assertEqual(set(entry.holds), set(['partial occupancy']))
        #self.assertEqual(entry.keywords, ['solid solution'])
        #self.assertEqual(entry.duplicate_of.id, perfect.id)
