from qmpy import *
from qmpy.analysis.miedema import *
import matplotlib
import matplotlib.pylab as plt
import matplotlib.gridspec as gridspec

comps = Composition.objects.filter(ntypes__gt=1)
comps = comps.filter(exptformationenergy__dft=False)

f = open('data.txt', 'w')
for comp in comps.distinct():
    print comp
    # OQMD deltaH
    gs = comp.ground_state
    if gs is None:
        continue
    calc = gs.calculation
    if calc is None:
        continue
    if not 'icsd' in calc.path:
        continue

    dft1 = calc.formation_energy(reference='nothing')
    dft2 = calc.formation_energy(reference='standard')
    dft3 = calc.formation_energy(reference='everything')
    
    # Experimental deltaH
    expts = comp.exptformationenergy_set.filter(dft=False)
    expts = np.array(expts.values_list('delta_e', flat=True))
    diffs = abs(expts - dft3)
    ind = np.argsort(diffs)[0]
    expt = expts[ind]

    # materials project
    mat_proj = comp.exptformationenergy_set.filter(dft=True)
    mat_proj_data = mat_proj.values_list('delta_e', flat=True)
    mat_proj = None
    if mat_proj_data:
        mat_proj = min(mat_proj_data)

    # meidema 
    if not set(comp.comp.keys()) < set(element_groups['DD']):
        meidema = None
    else:
        meidema = Miedema.get(comp.comp)

    if calc.hub_comp:
        dft1 = None

    f.write(' '.join(map(str,[comp.name,
                              expt, 
                              dft1, dft2, dft3, 
                              mat_proj, meidema, 
                              calc.band_gap, calc.magmom]))+'\n')
f.close()
