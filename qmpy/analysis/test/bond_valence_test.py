from qmpy.analysis.bond_valence import total_valence_sum
from qmpy.io.cif import read_cif
from qmpy import INSTALL_PATH

structure = read_cif(INSTALL_PATH+'/analysis/test/files/fe3o4.cif')
structure.save()

total_valence_sum(structure)


