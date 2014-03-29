from qmpy import *
from qmpy.analysis.nearest_neighbors import *
import os.path

path = os.path.dirname(os.path.abspath(__file__))
#s = io.read(INSTALL_PATH+'/io/files/POSCAR_SC')
#s = io.read(INSTALL_PATH+'/io/files/POSCAR_BCC')
s = io.read(INSTALL_PATH+'/io/files/fe3o4.cif')

nns = find_neighbors(s)
