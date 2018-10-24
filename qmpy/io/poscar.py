#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
import logging
import gzip
import os
from os.path import exists, isfile, isdir
import time

from django.db import models
import numpy as np

import qmpy
import qmpy.materials.structure as st
import qmpy.materials.composition as comp
import qmpy.data.meta_data as ref
from qmpy.utils import *

logger = logging.getLogger(__name__)

class POSCARError(Exception):
    pass

def write(struct, filename=None, comments=None, direct=True, 
            distinct_by_ox=False, vasp4=False, **kwargs):
    """
    Write a :mod:`~qmpy.Structure` to a file or string.

    Arguments:
        struct: A `~qmpy.Structure` object.

    Keyword Arguments:
        filename:
            If None, returns a string.

        direct:
            If True, write POSCAR in fractional coordinates. If False, returns
            a POSCAR in cartesian coordinates. 

        distinct_by_ox: 
            If True, elements with different specified oxidation states will be
            treated as different species. i.e. the elements line of Fe3O4 would
            read Fe Fe O (Fe3+, Fe4+, O2-). This can be useful for breaking
            symmetry, or for specifying different U-values for different
            oxidation state elements.

        vasp4:
            If True, omits the species line.

    Examples::
        
        >>> s = io.read(INSTALL_PATH+'/io/files/POSCAR_BCC')
        >>> print io.poscar.write(s)
        Cu
         1.0
        3.000000 0.000000 0.000000
        0.000000 3.000000 0.000000
        0.000000 0.000000 3.000000
        Cu
        2
        direct
         0.0000000000 0.0000000000 0.0000000000
         0.5000000000 0.5000000000 0.5000000000

        >>> io.poscar.write(s, '/tmp/POSCAR')

    """
    comp = struct.comp
    struct.atoms = atom_sort(struct.atoms)

    cdict = defaultdict(int)
    if not distinct_by_ox:
        ordered_keys = sorted(comp.keys())
        for a in struct:
            cdict[a.element_id] += 1
        counts = [ int(cdict[k]) for k in ordered_keys ]
    else:
        for a in struct.atoms:
            if int(a.oxidation_state) != a.oxidation_state:
                cdict['%s%+f' % (a.element_id, a.oxidation_state)] += 1
            else:
                cdict['%s%+d' % (a.element_id, a.oxidation_state)] += 1
        ordered_keys = sorted([ k for k in cdict.keys() ])
        counts = [ int(cdict[k]) for k in ordered_keys ]

    if comments is not None:
        poscar = '# %s \n 1.0\n' %(comments)
    else:
        poscar = ' '.join(set(a.element_id for a in struct.atoms)) + '\n 1.0\n'
    cell = '\n'.join([ ' '.join([ '%f' % v  for v in vec ]) for vec in
        struct.cell ])
    poscar += cell +'\n'
    names = ' '.join( a for a in ordered_keys ) + '\n'
    ntypes = ' '.join( str(n) for n in counts ) + '\n'
    if not vasp4:
        poscar += names
    poscar += ntypes
    if direct:
        poscar += 'direct\n'
        for x,y,z in struct.coords:
            poscar += ' %.10f %.10f %.10f\n' % (x,y,z)
    else:
        poscar += 'cartesian\n'
        for x, y, z in struct.cartesian_coords:
            poscar += ' %.10f %.10f %.10f\n' % (x,y,z)

    if filename:
        open(filename, 'w').write(poscar)
    else:
        return poscar

def read(poscar, species=None):
    """
    Read a POSCAR format file.

    Reads VASP 4.x and 5.x format POSCAR files.

    Keyword Arguments:
        `species`:
            If the file is 4.x format and the title line doesn't indicate what
            species are present, you must supply them (in the correct order)
            with the `species` keyword.

    Raises:
        POSCARError: If species data is not available.

    Examples::
        
        >>> io.poscar.read(INSTALL_PATH+'/io/files/POSCAR_FCC')

    """

    # Initialize the structure output
    struct = st.Structure()

    # Read in the title block, and system sell
    poscar = open(poscar,'r')
    title = poscar.readline().strip()
    scale = float(poscar.readline().strip())
    s = float(scale)
    cell = [[ float(v) for v in poscar.readline().strip().split() ],
            [ float(v) for v in poscar.readline().strip().split() ],
            [ float(v) for v in poscar.readline().strip().split() ]]
    cell = np.array(cell)

    if s > 0:
        struct.cell = cell*s
    else:
        struct.cell = cell
        struct.volume = -1*s

    # Determine whether POSCAR is in VASP 5 format
    #   VASP 5 has the elements listed after the 
    #   the cell parameters
    vasp5 = False
    _species = poscar.readline().strip().split()
    try:
        float(_species[0])
    except:
        vasp5 = True
        counts = [ int(v) for v in poscar.readline().strip().split() ]

    # If the format is not VASP 5, the elements should
    #  have been listed in the title
    if not vasp5:
        counts = map(int, _species)
        if not species:
            _species = title.strip().split()
            for s in _species:
                if not s in qmpy.elements.keys():
                    msg = 'In VASP4.x format, title line MUST be species present'
                    raise POSCARError
        else:
            _species = species
    species = _species

    # Prepare a list of numbers of atom types
    atom_types = []
    for n,e in zip(counts, species):
        atom_types += [e]*n

    # Determine whether coordinates are in direct or cartesian
    direct = False
    style = poscar.readline().strip()

    if style[0].lower() == 's':
        # The POSCAR contains selective dynamics info
        style = poscar.readline().strip()

    if style[0] in ['D', 'd']:
        direct = True

    # Read in the atom coordinates
    struct.natoms = sum(counts)
    struct.ntypes = len(counts)
    atoms = []
    inv = np.linalg.inv(cell).T
    for i in range(struct.natoms):
        atom = st.Atom()
        atom.element_id = atom_types[i]
        if direct:
            atom.coord = [ float(v) for v in poscar.readline().strip().split()[0:3] ]
        else:
            cart = [ float(v) for v in poscar.readline().strip().split()[0:3] ]
            atom.coord = np.dot(inv, cart)
        struct.add_atom(atom)
    struct.get_volume()
    struct.set_composition()
    return struct
