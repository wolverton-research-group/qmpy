#!/usr/bin/env python

import os, os.path

from math import *
from strings import *
from rendering import *
from daemon import Daemon

def mkdir(path):
    """
    Makes the specified folder, including required folders "below"
    """
    if not path:
        return
    bpath = os.path.split(path)[0]
    mkdir(bpath)
    if not os.path.exists(path):
        os.mkdir(path)

def assign_type(string):
    res = string
    try:
        res = float(string)
    except ValueError:
        pass
    try:
        res = int(string)
    except ValueError:
        pass
    if string.lower() == 'true':
        res = True
    elif string.lower() == 'false':
        res = False
    elif string.lower() == 'none':
        res = None
    return res

def combinations_with_replacement(iterable, r):
    # combinations_with_replacement('ABC', 2) --> AA AB AC BB BC CC
    pool = tuple(iterable)
    n = len(pool)
    if not n and r:
        return
    indices = [0] * r
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != n - 1:
                break
        else:
            return
        indices[i:] = [indices[i] + 1] * (r - i)
        yield tuple(pool[i] for i in indices)

def atom_sort(atoms):
    atoms = np.array(atoms)
    x = [ a.x for a in atoms ]
    y = [ a.y for a in atoms ]
    z = [ a.z for a in atoms ]
    ox = [ a.ox for a in atoms ]
    elt = [ a.element_id for a in atoms ]
    comps = []
    for l in [x, y, z, ox, elt ]:
        if any(l):
            comps.append(l)
    if len(comps) == 0:
        return atoms
    return atoms[np.lexsort(comps)].tolist()

def get_docstring(model):
    names = model._meta.get_all_field_names()
    longest = max(map(len, names))

    print "+-" + '-'*longest + '-+'
    for n in names:
        print '| '+ n.ljust(longest) + ' |'
        print "+-" + '-'*longest + '-+'

def get_field_list(model):
    print ', '.join(model._meta.get_all_field_names())
