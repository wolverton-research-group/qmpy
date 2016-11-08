from qmpy import *
from django.test import TestCase

peak_locations = [
        ]

class MiedemaTestCase(TestCase):
    def setUp(self):
        read_elements()

    def test_methods(self):
        ## test that it generally works
        self.assertEquals(Miedema('FeNi').energy, -0.03)
        self.assertEquals(Miedema('FeNi').energy, -0.03)
        c = Composition.get('LiBe')
        self.assertEquals(Miedema(c).energy, -0.08)
        self.assertEquals(Miedema({'Pt':1,'Ti':3}).energy, -0.76)

        ## test that non-metals are ignored
        self.assertEquals(Miedema('Fe2O3').energy, None)

        ## test that it is quantity invariant
        self.assertEquals(Miedema('Fe5Ni5').energy, -0.03)

class PDFTestCase(TestCase):
    def test_distances(self):
        pass

class NearestNeighborTestCase(TestCase):
    def setUp(self):
        read_elements()

        self.fcc = io.read(INSTALL_PATH+'/io/files/POSCAR_FCC')
        self.bcc = io.read(INSTALL_PATH+'/io/files/POSCAR_BCC')
        self.sc = io.read(INSTALL_PATH+'/io/files/POSCAR_SC')

    def test_heuristic(self):
        self.fcc.find_nearest_neighbors()
        self.assertEqual(len(self.fcc[0].neighbors), 12)

        self.bcc.find_nearest_neighbors()
        self.assertEqual(len(self.bcc[0].neighbors), 8)

        self.sc.find_nearest_neighbors()
        self.assertEqual(len(self.sc[0].neighbors), 6)

    def test_voronoi(self):
        self.fcc.find_nearest_neighbors(method='voronoi')
        self.assertEqual(len(self.fcc[0].neighbors), 12)

        self.bcc.find_nearest_neighbors(method='voronoi')
        self.assertEqual(len(self.bcc[0].neighbors), 14)
        self.bcc.find_nearest_neighbors(method='voronoi', tol=5)
        self.assertEqual(len(self.bcc[0].neighbors), 8)

        self.sc.find_nearest_neighbors(method='voronoi')
        self.assertEqual(len(self.sc[0].neighbors), 6)

