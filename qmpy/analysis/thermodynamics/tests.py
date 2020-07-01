from django.test import TestCase
from qmpy.analysis.thermodynamics import *

class PhaseTestCase(TestCase):
    def test_create(self):
        test = Phase(composition={'Li':2,'Fe':4,'O':6}, 
                     energy=-1.2345)
        self.assertEqual(test.name, 'LiFe2O3')
        self.assertEqual(test.space, set(['Fe', 'Li', 'O']))
        self.assertEqual(test.unit_comp, {'Fe': 0.33333333333333331, 
                                          'O': 0.5, 
                                          'Li': 0.16666666666666666})
        self.assertEqual(test.nom_comp, {'Fe': 2, 'O': 3, 'Li':1})
        self.assertEqual(test.comp, {'Fe': 4, 'O': 6, 'Li': 2})
        self.assertEqual(test.latex, 'Li$_{}$Fe$_{2}$O$_{3}$')

class PhaseSpaceTestCase(TestCase):
    def test_create(self):
        test = PhaseSpace('Li-Fe-O', load='legacy.dat')
