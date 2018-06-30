from pprint import pprint
import yaml
import logging

import qmpy
from qmpy.utils.strings import *
from qmpy.data import *

logger = logging.getLogger(__name__)

def fit(name, calculations=None, experiments=None, fit_for=[]):
    f = qmpy.Fit.get(name)
    f.save()

    f.elements = fit_for
    data = []
    hub_data = []

    elements = set()  # list of all elements in any compound in fit
    hubbards = set() # list of all hubbards in any calc in fit
    fit_set = set(fit_for)
    expts = {}
    calcs = {}

    expt_data = experiments.values_list('composition_id', 'delta_e')
    calc_data = calculations.values_list('composition_id', 'energy_pa')
    base_mus = dict( (elt, qmpy.Composition.get(elt).total_energy) for elt in
            element_groups['all'])

    for (name, delta_e), expt in zip(expt_data, experiments):
        if expt.delta_e is None:
            continue
        if not set(parse_comp(name).keys()) & fit_set:
            continue

        if not name in expts:
            expts[name] = expt
        elif delta_e < expts[name].delta_e:
            expts[name] = expt
    f.experiments = expts.values()

    for (name, energy_pa), calc in zip(calc_data, calculations):
        if energy_pa is None:
            continue
        if not set(parse_comp(name).keys()) & fit_set:
            continue

        if not name in calcs:
            calcs[name] = calc
        elif energy_pa < calcs[name].energy_pa:
            calcs[name] = calc
    f.dft = calcs.values()

    valid_pairs = set(calcs.keys()) & set(expts.keys())
    for name in valid_pairs:
        for elt in parse_comp(name):
            elements.add(elt)
        if not calcs[name].hub_comp:
            data.append(name)
        else:
            hub_data.append(name)
            for hub in calcs[name].hubbards:
                if hub: 
                    hubbards.add(hub)

    elements = list(elements)
    hubbards = list(hubbards)
    f.elements = elements
    f.hubbards = hubbards
    hubbard_elements = [ hub.element.symbol for hub in hubbards ]

    A = []
    b = []

    for name in data:
        uc = unit_comp(parse_comp(name))
        # remove non-fitting elements
        b.append(calcs[name].energy_pa - expts[name].delta_e - sum( base_mus[elt]*amt 
                for elt, amt in uc.items() if elt not in fit_for ))
        A.append([ uc.get(elt,0) for elt in fit_for ])
    
    A = np.array(A)
    b = np.array(b)
    i = 0
    if len(A) == 0 and len(b) == 0:
        element_mus = {}
    else:
        old_std = 1000
        std = 0
        while int(old_std*1000) - int(std*1000) != 0:
            old_std = std

            result = np.linalg.lstsq(A, b)[0]
            ### Identify existing bad errors
            b_hats = np.dot(A, result)

            errs = b - b_hats
            std = np.std(errs)
            print "iter %s: std: %0.3f" % (i, std)
            inds = np.argwhere(np.abs(errs) < std*4)
            A = A[np.abs(errs) < std*4]
            b = b[np.abs(errs) < std*4]
            i += 1

        element_mus = dict(zip(fit_for, result))

    ### Second fit
    A = []
    b = []
    for name in hub_data:
        uc = unit_comp(parse_comp(name))
        b.append(calcs[name].energy_pa - expts[name].delta_e -
                sum( base_mus[elt]*amt
                    for elt, amt in uc.items() 
                    if elt not in fit_for) - 
                sum( element_mus.get(elt, 0)*amt
                    for elt, amt in uc.items()))
        A.append([ uc.get(elt, 0) for elt in hubbard_elements ])

    A = np.array(A)
    b = np.array(b)
    if len(A) == 0 and len(b) == 0:
        hubbard_mus = {}
    else:
        old_std = 1000
        std = 0
        i = 0
        while int(old_std*1000) - int(std*1000) != 0:
            old_std = std

            result = np.linalg.lstsq(A, b)[0]
            ### Identify existing bad errors
            b_hats = np.dot(A, result)
            errs = b - b_hats
            std = np.std(errs)
            print "iter %s: std: %0.3f" % (i, std)
            A = A[np.abs(errs) < std*4]
            b = b[np.abs(errs) < std*4]
            i += 1

        hubbard_mus = dict(zip(hubbards, result))

    for elt, mu in base_mus.items():
        if elt not in element_mus:
            element_mus[qmpy.Element.get(elt)] = float(mu)

        if abs(element_mus.get(qmpy.Element.get(elt), 0.0)) > 100:
            element_mus[qmpy.Element.get(elt)] = float(mu)

    #element_mus = dict( (str(e), float(val)) for e, val in element_mus.items())
    #hubbard_mus = dict( (str(h.key), float(val)) for h, val in hubbard_mus.items())

    new_e_mus = {}
    for elt, val in element_mus.items():
        if val > 100:
            val = base_mus[str(elt)]
        mu = qmpy.ReferenceEnergy(element_id=elt, value=val)
        f.reference_energy_set.add(mu)
        new_e_mus[str(elt)] = float(val)

    new_h_corrs = {}
    for hub, val in hubbard_mus.items():
        hm = qmpy.HubbardCorrection(hubbard=hub, value=val, element=hub.element)
        f.hubbard_correction_set.add(hm)
        new_h_corrs[str(hub.key)] = float(val)
    return new_e_mus, new_h_corrs

