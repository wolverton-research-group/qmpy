from qmpy import *

comps = [ parse_comp('Na0.48 O3 W1'),
          {'Fe':2, 'O':3},
          {'Fe':1, 'O':1.5},
          {'Fe':0.4, 'O':0.6},
          {'Ni':0.333333333333333333333, 'O':0.666666666666667},
          {'Ni':0.333333333, 'O':0.6666667},
          {'Ni':0.333, 'O':0.667},
          {'Ni':0.33, 'O':0.67},
          {'Ni':0.3, 'O':0.7},
          {'Bi':0.1231, 'Na':0.2324, 'Ar':0.6445} ]

for c in comps:
    print format_comp(c),
    print format_comp(reduce_comp(c))
