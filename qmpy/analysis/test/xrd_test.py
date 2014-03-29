from qmpy import *
from qmpy.analysis.xrd import *

s = io.read(INSTALL_PATH+'/io/files/POSCAR_FCC')

#lat_params = [7.016, 7.545, 9.728, 90., 99.69, 90]
#expt_peaks = np.array(map(float, open('peaks.txt').read().split()))
#calc_peaks = np.array(get_all_peaks(lat_params))

xrd = XRD(s)
xrd.get_peaks()
xrd.get_intensities()
