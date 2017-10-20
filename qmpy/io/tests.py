from qmpy import *
import unittest
from django.test import TestCase

def simple_equal(s1, s2):
    if not all(s1.atom_types == s2.atom_types):
        return False
    if not np.allclose(s1.cell, s2.cell):
        return False
    if not np.allclose(s1.coords, s2.coords):
        return False
    return True

class POSCARTestCase(TestCase):
    def setUp(self):
        read_elements()
        a = 3.54
        cell = [[a,0,0],[0,a,0],[0,0,a]]
        atoms = [('Cu', [0,0,0]),
                         ('Cu', [0.5, 0.5, 0.5])]
        self.struct = Structure.create(cell=cell, atoms=atoms)

    def test_vasp4(self):
        s = io.poscar.read(INSTALL_PATH+'/io/files/POSCAR_vasp4')
        self.assertTrue(simple_equal(self.struct, s))

    def test_vasp5(self):
        s = io.poscar.read(INSTALL_PATH+'/io/files/POSCAR_vasp5')
        self.assertTrue(simple_equal(self.struct, s))

    def test_write_vasp5(self):
        ans = open(INSTALL_PATH+'/io/files/POSCAR_vasp5').read()
        self.assertEqual(io.poscar.write(self.struct), ans)

    def test_write_vasp5(self):
        ans = open(INSTALL_PATH+'/io/files/POSCAR_vasp4').read()
        self.assertEqual(io.poscar.write(self.struct, vasp4=True), ans)


class CifTestCase(TestCase):
    def setUp(self):
        read_elements()
        a = 3.54
        cell = [[a,0,0],[0,a,0],[0,0,a]]
        atoms = [('Cu', [0,0,0]),
                         ('Cu', [0.5, 0.5, 0.5])]
        self.struct = Structure.create(cell=cell, atoms=atoms)

    def test_read(self):
        s = io.poscar.read(INSTALL_PATH+'/io/files/POSCAR_vasp4')
        self.assertTrue(simple_equal(self.struct, s))

    def test_write(self):
        s = io.poscar.read(INSTALL_PATH+'/io/files/POSCAR_vasp4')
        with open(INSTALL_PATH+'/io/files/test.cif') as fr:
            self.assertEqual(io.cif.write(s), fr.read())
