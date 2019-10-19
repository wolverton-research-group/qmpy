from qmpy import *

elts = element_groups['all-sub']

for e1, e2 in itertools.combinations(elts, r=2):
    # do logic
    if e1 == e2:
        break
    try:
        ps = PhaseSpace([e1,e2])
        k = frozenset([e1,e2])
        bonds = []
        for p in ps.stable:
            s = p.calculation.input
            if s.ntypes < 2:
                continue
            dists = get_pair_distances(s, 10)
            bonds.append(min(dists[k]))
        print e1, e2, np.average(bonds), np.std(bonds)
    except:
        continue
