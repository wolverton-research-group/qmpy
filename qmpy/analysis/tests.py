import os

from qmpy import *
from django.test import TestCase

peak_locations = []

class MiedemaTestCase(TestCase):
    def setUp(self):
        read_elements()

    def test_methods(self):
        ## test that it generally works
        self.assertEqual(Miedema('FeNi').energy, -0.03)
        self.assertEqual(Miedema('FeNi').energy, -0.03)
        c = Composition.get('LiBe')
        self.assertEqual(Miedema(c).energy, -0.08)
        self.assertEqual(Miedema({'Pt':1,'Ti':3}).energy, -0.76)

        ## test that non-metals are ignored
        self.assertEqual(Miedema('Fe2O3').energy, None)

        ## test that it is quantity invariant
        self.assertEqual(Miedema('Fe5Ni5').energy, -0.03)

class PDFTestCase(TestCase):
    def test_distances(self):
        pass

class NearestNeighborTestCase(TestCase):
    def setUp(self):
        read_elements()

        sample_files_loc = os.path.join(INSTALL_PATH, 'io', 'files')
        self.fcc = io.poscar.read(os.path.join(sample_files_loc, 'POSCAR_FCC'))
        self.bcc = io.poscar.read(os.path.join(sample_files_loc, 'POSCAR_BCC'))
        self.sc = io.poscar.read(os.path.join(sample_files_loc, 'POSCAR_SC'))

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

