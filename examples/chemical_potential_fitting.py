from qmpy import *
from qmpy.analysis.thermodynamics.chemical_potential_fitting import fit
from qmpy.data import save_chem_pots, element_groups

calcs = Calculation.objects.filter(converged=True, configuration='standard')

calcs = calcs.filter(path__contains='icsd') | calcs.filter(path__contains='elements')

expts = ExptFormationEnergy.objects.filter(dft=False, 
        source__in=['ssub', 'konig', 'iit', 'corrections'])

fitall = element_groups['all']
fitstd = ['H', 'N', 'O', 'F', 'Cl',
          'Hg', 'Br',
          'Na', 'Sn', 'Ti',
          'I', 'P', 'S']

elts, hubs = fit(calculations=calcs, 
                 experiments=expts,
                 fit_for=fitstd)

chem_pots['standard'] = {'elements': elts,
                         'hubbards': hubs}

save_chem_pots(chem_pots)

