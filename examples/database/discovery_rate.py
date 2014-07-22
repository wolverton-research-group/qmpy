#from qmpy import *
from matplotlib import rc
rc('font', **{'family':'serif', 'serif':['Century']})
params = {'font.size': 48}
import matplotlib
matplotlib.rcParams.update(params)
import matplotlib.pylab as plt
import pickle
import sys
import numpy as np

def get_data():
    if not 'new' in sys.argv:
        return pickle.loads(open('dates.txt').read())

    forms = Formation.objects.filter(fit='diff_refs', 
            hull_distance__lte=0.025,
            entry__ntypes__gt=1,
            entry__icsd__coll_code__gt=0).select_related()
    
    
    dates = []
    
    for form in forms:
        try:
            struct = form.entry.input
            sdates = struct.similar.values_list('entry__reference__year', flat=True)
            dates.append(min(sdates))
        except:
            continue

    result = open('dates.txt', 'w')
    result.write(pickle.dumps(dates))
    result.close()

dates = np.array(get_data())

plt.hist(dates, bins=max(dates)-min(dates), cumulative=True)
plt.xlabel('Year')
plt.ylabel('# of Stable Structures')
plt.savefig('test.eps', bbox_inches='tight')
