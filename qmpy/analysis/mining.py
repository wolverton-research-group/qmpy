# qmpy/analysis/miner.py

import pickle
import os.path

import numpy as np

import qmpy
from qmpy.utils import unit_comp, format_comp, parse_comp
elts = qmpy.data.elements

def max_diff(data):
    """max_diff"""
    return max(data) - min(data)

def average(data):
    """avg"""
    return np.average(data)

def get_npoint_statistics(comp):
    desc = {}
    for e1, e2 in itertools.combinations(elts, r=2):
        desc['frac_%s_%s' % (e1, e2)] = comp.get(e1,0)*comp.get(e2,0)
    return desc

def get_composition_descriptors(comp):
    if isinstance(comp, basestring):
        comp = parse_comp(comp)
    elif isinstance(comp, qmpy.Composition):
        comp = comp.comp
    desc = {}
    for elt in elts:
        desc['frac_%s' % elt] = comp.get(elt,0)
    return desc

def get_basic_composition_descriptors(comp):
    if isinstance(comp, basestring):
        comp = parse_comp(comp)
    elif isinstance(comp, qmpy.Composition):
        comp = comp.comp
    comp = unit_comp(comp)
    desc = {}

    for attr in ['electronegativity', 'period', 'group', 
            'mass', 'atomic_radii', 'z']:
        data = [ elts[elt][attr] for elt in comp ]
        for func in [ max_diff, average ]:
            desc['%s_%s' % (func.__doc__, attr)] = func(data)

    desc['s_val'] = sum([ elts[e]['s_elec']*x for e,x in comp.items() ])
    desc['p_val'] = sum([ elts[e]['p_elec']*x for e,x in comp.items() ])
    desc['d_val'] = sum([ elts[e]['d_elec']*x for e,x in comp.items() ])
    desc['f_val'] = sum([ elts[e]['f_elec']*x for e,x in comp.items() ])
    return desc

def get_rich_composition_descriptors(comp):
    comp = qmpy.Composition(comp)
    desc = {}
    forms = comp.formationenergy_set.all()
    desc['stable'] = forms.filter(stability__lte=0).exists()
    desc['near_stable'] = forms.filter(stability__lte=0.025).exists()

    near_forms = qmpy.Formation.search(comp.comp.keys())
    desc['stable_in_space'] = near_forms.filter(stability__lt=0).count()
    desc['near_statble_in_space'] = near_forms.filter(stability__lt=0.025).count()
    return desc

def get_calculation_descriptors(calc):
    raise NotImplementedError

def save_model(model, name=None):
    s = pickle.dumps(model)
    if name is None:
        return s
    fpath = os.path.join(INSTALL_PATH, 'data', 'data_mining', name+'.pkl')
    f = open(fpath)
    f.write(s)
    f.close()

def load_model(name):
    name = name.replace('.pkl', '')
    fpath = os.path.join(INSTALL_PATH, 'data', 'data_mining', name+'.pkl')
    s = open(fpath, 'rb')
    return pickle.loads(s)

