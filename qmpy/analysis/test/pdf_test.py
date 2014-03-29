from qmpy import *
from qmpy.analysis.pdf import *
import matplotlib.pylab as plt

s = io.read('files/POSCAR')

get_pdf(s, smearing=0.05, max_dist=6)

#plt.plot(x, y)

#plt.savefig('pdf.png')
