from qmpy import Structure
import numpy as np
from numpy.linalg import norm
import itertools

s1 = Structure.create('POSCAR_other')
s2 = Structure.create('POSCAR_C')

tolerance = 0.1 # maximum allowed strain

def check_strain(lva1, lva2, lvb1, lvb2):
    lva1 = np.array(lva1)
    lva2 = np.array(lva2)
    lvb1 = np.array(lvb1)
    lvb2 = np.array(lvb2)
    #if lva1-lvb1 < lva2-lvb2:
    #    lvb1, lvb2 = lvb2, lvb1

    e1 = (norm(lva1)-norm(lvb1))/norm(lva1)
    e2 = (norm(lva2)-norm(lvb2))/norm(lva2)
    g1 = np.arcsin(np.dot(lva1, lva2)/(norm(lva1)*norm(lva2)))*180/np.pi -\
            np.arcsin(np.dot(lvb1, lvb2)/(norm(lvb1)*norm(lvb2)))*180/np.pi

    return abs(e1), abs(e2), abs(g1)

def combi(iterable, r):
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


def choices_2D(vec1, vec2, size=5):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    for i1, i2, j1, j2 in combi(range(-size,size), r=4):
        yield i1*vec1 + j1*vec1, i2*vec2+j2*vec2

def choices_3D(vec1, vec2, vec3, size=5):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    vec3 = np.array(vec3)
    for i1, i2, j1, j2, k1, k2 in combi(range(-size,size), r=6):
        yield i1*vec1+j1*vec2+k1*vec3, i2*vec2+j2*vec2+k2*vec3
