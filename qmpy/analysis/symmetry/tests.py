from django.test import TestCase
from qmpy import *

class SpacegroupTestCase(TestCase):
    def setUp(self):
        read_spacegroups([225])

    def test_translations(self):
        trans = Translation.get([0,0,0])
        self.assertEqual(str(trans), '0,0,0')
        self.assertTrue(np.allclose(trans.vector, [0,0,0]))
        trans = Translation.get([0,0,0.5])
        self.assertEqual(str(trans), '0,0,+1/2')
        self.assertTrue(np.allclose(trans.vector, [0,0,0.5]))
        trans = Translation.get([-0.5, 0, 0.5])
        self.assertEqual(str(trans), '-1/2,0,+1/2')
        self.assertTrue(np.allclose(trans.vector, [-0.5, 0, 0.5]))

    def test_rotations(self):
        rot = Rotation.get([[0,1,0],[1,0,0],[0,0,1]])
        self.assertEqual(str(rot), '+y,+x,+z')
        self.assertTrue(np.allclose(rot.matrix, [[0,1,0],[1,0,0],[0,0,1]]))
        rot = Rotation.get([[-1,-1,-1],[1,0,-1],[1,-1,1]])
        self.assertEqual(str(rot), '-x-y-z,+x-z,+x-y+z')
        self.assertTrue(np.allclose(rot.matrix,
            [[-1,-1,-1],[1,0,-1],[1,-1,1]]))

    def test_operations(self):
        op = Operation.get('x,y,-y')
        self.assertTrue(np.allclose(op.rotation.matrix,
            [[1,0,0],[0,1,0],[0,-1,0]]))
        self.assertEqual(str(op.rotation), '+x,+y,-y')
        self.assertTrue(np.allclose(op.translation.vector, [0,0,0]))
        self.assertEqual(str(op.translation), '0,0,0')

        op = Operation.get('x+z+1/2,y-z-1/3,x+y+z')
        self.assertEqual(str(op), '+x+z+1/2,+y-z+333333/1000000,+x+y+z')
        self.assertTrue(np.allclose(op.rotation.matrix, 
            [[1,0,1],[0,1,-1],[1,1,1]]))
        self.assertTrue(np.allclose(op.translation.vector, 
            [0.5, 0.333333, 0.0]))

    def test_wyckoff(self):
        site = WyckoffSite.get('a', 225)
        self.assertEqual(str(site), 'a4')
        self.assertEqual(site.multiplicity, 4)

    def test_spacegroup(self):
        ## getter
        self.assertRaises(Spacegroup.DoesNotExist, Spacegroup.get, 500)

        # some basic attributes
        sg = Spacegroup.get(225)
        self.assertEqual(len(sg.sym_ops), 48)
        self.assertEqual(sg.hm, 'Fm-3m')
        self.assertEqual(sg.symbol, 'Fm-3m')
        self.assertEqual(sg.schoenflies, 'Oh^5')
        self.assertEqual(sg.hall, '-F 4 2 3')

        # a simple application of symmetry operations
        self.assertEqual(len(sg.equivalent_sites([0.25,0.25,0.25])), 8)
