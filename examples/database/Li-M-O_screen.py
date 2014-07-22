from qmpy import *
import itertools
import numpy as np
from numpy.linalg import det
import sys
import pprint

### add o2 chemical potential stability ranges

icsd=Project.objects.get(name='icsd')

def full_search():
    li2o = Composition.get('Li2O')

    o = Element.get('O').composition_set.all()
    li = Element.get('Li').composition_set.all()
    lio = o & li 
    quats = lio.all().filter(ntypes__gt=2)#.exclude(formationenergy=None)

    terns = defaultdict(list)

    for quat in quats:
        comp = dict(quat.comp)
        comp['O'] -= 0.5* comp['Li']
        del comp['Li']
        c = Composition.get(comp)
        if not c.formationenergy_set.exists():
            continue
        comp2 = dict(quat.unit_comp)
        comp2['O'] -= 0.5* comp2['Li']
        comp2['Li'] = 0
        terns[c].append([ quat, sum(comp2.values()) ])

    print len(terns)

    pdata = PhaseData()
    pdata.load_oqmd()
    for p in pdata.phase_dict.values():
        p._energy += 0.32*p.unit_comp.get('O', 0.0)
    pdata.phase_dict['LiO3']._energy = 10
    pdata.phase_dict['LiO2']._energy = 10
    for key, vals in terns.items():
        print key.name
        vals = sorted(vals, key=lambda x: x[1] )
        space = PhaseSpace('%s-Li2O' % key.name, data=pdata, load=None)
        #space.get_qhull()
        space.plot_reactions('Li2O', electrons=2.0)
        plt.savefig('%s.eps' % key.name)
        reacts= space.get_reactions('Li2O', electrons=2.0)
        f = open('%s-Li2O.txt' % key.name, 'w')
        f.write(' : '.join([
            'voltage',
            'react_phases', 'prod_phases',
            'react_Li2O_frac', 'prod_Li2O_frac',
            'react_bgap', 'prod_bgap',
            'react_mass', 'prod_mass',
            'react_vol', 'prod_vol',
            'react_latex', 'prod_latex'
            ])+'\n')
        for r in sorted(reacts, key=lambda x: -x.voltage):
            f.write(' : '.join([ str(s) for s in 
                [
                    r.voltage, 
                    r.reactant_string.count('+')+1, r.product_string.count('+')+1,
                    r.r_var_comp, r.p_var_comp,
                    r.r_bgap, r.p_bgap,
                    r.react_mass, r.prod_mass,
                    r.react_vol, r.prod_vol,
                    r.reactant_latex, r.product_latex
                    ]])+'\n')
        f.close()
        time.sleep(1)

def how_many():
    o = Element.get('O').composition_set.all()
    li = Element.get('Li').composition_set.all()
    lio = o & li

    print '%s Li-O-M ternary compounds' % lio.filter(ntypes=3).count()
    print '%s Li-O-M1-M2 quaternary compounds' % lio.filter(ntypes=4).count()
    print '%s Li-O-M1-M2-M3 pentenary compounds' % lio.filter(ntypes=5).count()
    print '%s Li-O-M1-...-Mn N-nary compounds' % lio.filter(ntypes__gt=5).count()

if __name__ == '__main__':
    if 'scope' in sys.argv:
        how_many()
        exit()
    pdata = full_search()
