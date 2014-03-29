import time
from qmpy import *
import os, os.path
import tempfile

root = os.path.dirname(os.path.abspath(__file__))

## can read?
#calc = Calculation.read(root+'/files/normal/initialize')

#exit()
calcs = []

for cond in [ 'normal', 'magnetic', 'ldau' ]:
    for path in [ 'initialize', 'coarse_relax', 'fine_relax', 'standard']:
        #for type in [ 'initialize', 'coarse_relax', 'fine_relax', 'standard']:
        struct = io.read('%s/%s/%s/POSCAR' % (root, cond, path))
        calc = Calculation.setup(struct, 
                configuration=path, 
                path='%s/%s/%s' % (root, cond, path))
        calcs.append(calc)
        assert calc.converged
        print cond, path
