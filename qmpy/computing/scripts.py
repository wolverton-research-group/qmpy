import logging
import time
from django.db import models
from datetime import datetime
import os

import qmpy.utils as utils
from qmpy.analysis.vasp import *
from qmpy.analysis.thermodynamics.space import PhaseSpace
from qmpy.computing.resources import *

logger = logging.getLogger(__name__)

def initialize(entry, **kwargs):
    entry.input.set_magnetism('ferro')
    calc = Calculation.setup(entry.input, entry=entry,
            configuration='initialize', path=entry.path+'/initialize', 
            **kwargs)

    calc.set_label('initialize')
    if not calc.converged:
        calc.write()
        return calc

    if calc.converged:
        if calc.magmom > 0.1:
            entry.keywords.append('magnetic')
    return calc

def coarse_relax(entry, **kwargs):
    if entry.calculations.get('coarse_relax', Calculation()).converged:
        return entry.calculations['coarse_relax']

    calc = initialize(entry, **kwargs)
    if not calc.converged:
        calc.write()
        return calc

    calc.set_label('coarse_relax')
    inp = entry.structures['input']
    if not 'magnetic' in entry.keywords:
        inp.set_magnetism('none')

    calc = Calculation.setup(inp, entry=entry,
        configuration='coarse_relax', path=entry.path+'/coarse_relax',
        **kwargs)

    if calc.converged:
        calc.output.set_label('coarse_relax')
    return calc

def fine_relax(entry, **kwargs):
    if entry.calculations.get('fine_relax', Calculation()).converged:
        return entry.calculations['fine_relax']

    calc = coarse_relax(entry, **kwargs)
    if not calc.converged:
        calc.write()
        return calc
    inp = entry.structures['coarse_relax']
    if 'magnetic' in entry.keywords:
        inp.set_magnetism('ferro')

    calc = Calculation.setup(inp, entry=entry,
        configuration='fine_relax', path=entry.path+'/fine_relax', **kwargs)
    if calc.converged:
        entry.structures['fine_relax'] = calc.output
        entry.calculations['fine_relax'] = calc
    return calc

def standard(entry, **kwargs):
    if entry.calculations.get('standard', Calculation()).converged:
        return entry.calculations['standard']

    calc = fine_relax(entry, **kwargs)
    if not calc.converged:
        calc.write()
        return calc

    inp = entry.structures['fine_relax']
    if 'magnetic' in entry.keywords:
        inp.set_magnetism('ferro')

    calc = Calculation.setup(inp, entry=entry,
        configuration='standard', path=entry.path+'/standard', **kwargs)
    if calc.converged:
        f = calc.get_formation()
        f.save()
        entry.calculations['standard'] = calc
        entry.structures['standard'] = calc.output
        ps = PhaseSpace(calc.input.comp.keys())
        ps.compute_stabilities(save=True)
    return calc

def check_spin(entry):
    if entry.calculations.get('relaxation', Calculation()).converged:
        e1 = entry.calculations['relaxation'].energy
        entry.calculations['relaxation'].Co_lowspin = False
        if entry.calculations.get('Co_lowspin', Calculation()).converged:
            e2 = entry.calculations['Co_lowspin'].energy
            entry.calculations['Co_lowspin'].Co_lowspin = True
            if e1-e2 <= 0.005:
                return entry.calculations['relaxation']
            else:
                return entry.calculations['Co_lowspin']
    return None

def relaxation(entry, **kwargs):
    if 'Co' in entry.comp:
        spin = check_spin(entry)
        if not spin is None:
            return spin
    else:
        if entry.calculations.get('relaxation', Calculation()).converged:
            return entry.calculations['relaxation']

    if not entry.calculations.get('relaxation', Calculation()).converged:
        input = entry.input
        input.make_primitive()

        # because max likes to calculate fucking slowly
        projects = entry.project_set.all()
        if Project.get('max') in projects:
            calc = Calculation.setup(input, entry=entry,
                                            configuration='relaxation', 
                                            path=entry.path+'/relaxation', 
                                            settings={'algo':'Normal'},
                                            **kwargs)
        else:

            if 'relax_high_cutoff' in entry.keywords:
                calc = Calculation.setup(input,  entry=entry,
                                                 configuration='relaxation',
                                                 path=entry.path+'/relaxation',
                                                 settings={'prec':'ACC'},
                                                 **kwargs)
            else:
                calc = Calculation.setup(input,  entry=entry,
                                                 configuration='relaxation',
                                                 path=entry.path+'/relaxation',
                                                 **kwargs)

        entry.calculations['relaxation'] = calc
        entry.Co_lowspin = False
        if not calc.converged:
            calc.write()
            return calc

    if 'Co' in entry.comp:
        if not entry.calculations.get('Co_lowspin', Calculation()).converged:
            input = entry.input
            input.make_primitive()
            calc = Calculation.setup(input,  entry=entry,
                                             configuration='relaxation',
                                             path=entry.path+'/Co_lowspin',
                                             **kwargs)
            
            for atom in calc.input:
                if atom.element.symbol == 'Co':
                    atom.spin = 0.01

            entry.calculations['Co_lowspin'] = calc
            entry.Co_lowspin = True
            if not calc.converged:
                calc.write()
                return calc

    if 'Co' in entry.comp:
        calc = check_spin(entry)
        assert ( not calc is None )
        entry.structures['relaxed'] = calc.output
    else:
        entry.structures['relaxed'] = calc.output
    return calc

def static(entry, **kwargs):
    # include a block to check if the compound has cobalt
    # redo the static run if it does
    # relaxation - Co_lowspin <= 0.004
    if entry.calculations.get('static', Calculation()).converged:
        return entry.calculations['static']

    calc = relaxation(entry, **kwargs)
    if hasattr(calc, 'Co_lowspin'):
        use_lowspin = ( calc.Co_lowspin is True )
    else:
        use_lowspin = False

    if not calc.converged:
        return calc

    input = calc.output

    if use_lowspin:
        chgcar_path = entry.path+'/Co_lowspin'
    else:
        chgcar_path = entry.path+'/relaxation'

    calc = Calculation.setup(input, entry=entry,
                                    configuration='static', 
                                    path=entry.path+'/static', 
                                    chgcar=chgcar_path,
                                    **kwargs)

    if use_lowspin:
        for atom in calc.input:
            if atom.element.symbol == 'Co':
                atom.magmom = 0.01

    entry.calculations['static'] = calc
    if calc.converged:
        f = calc.get_formation()
        f.save()
        ps = PhaseSpace(calc.input.comp.keys())
        ps.compute_stabilities(save=True)
    else:
        calc.write()
    return calc

def wavefunction(entry, **kwargs):
    if entry.calculations.get('wavefunction', Calculation()).converged:
        return entry.calculations['wavefunction']

    calc = static(entry, **kwargs)
    if not calc.converged:
        return calc

    input = calc.input
    calc = Calculation.setup(input, entry=entry,
                                    configuration='static',
                                    path=entry.path+'/hybrids/wavefunction',
                                    chgcar=entry.path+'/static',
                                    settings={'lwave':True},
                                    **kwargs)
    entry.calculations['wavefunction'] = calc
    if not calc.converged:
        calc.write()
    return calc

def hybrid(entry, **kwargs):
    # first, get a wavecar
    wave = wavefunction(entry, **kwargs)
    if not wave.converged:
        return wave

    calcs = []
    default = ['b3lyp', 'hse06', 'pbe0', 'vdw']
    for hybrid in kwargs.get('forms', default):
        calc = Calculation.setup(input, entry=entry,
                                    configuration=hybrid,
                                    path=entry.path+'/hybrids/'+hybrid,
                                    wavecar=wave,
                                    settings={'lwave':True},
                                    **kwargs)
        calcs.append(calc)
    return calcs
