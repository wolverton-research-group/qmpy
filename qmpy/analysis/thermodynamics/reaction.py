# gclp.space

import numpy as np
import numpy.linalg
import json
import itertools
from collections import defaultdict
from utils import *
import logging

from scipy.spatial import ConvexHull

import qmpy
import phase

logger = logging.getLogger(__name__)

class Reaction(object):
    __doc__ = """
    methods
    attributes
    """
    
    def __init__(self, products=None, reactants=None, delta_var=None,
            variable=None, electrons=1.0):
        ### write blanks
        self._products = products
        self._reactants = reactants
        if isinstance(variable, basestring):
            self._variable = parse_comp(variable)
        elif isinstance(variable, phase.Phase):
            self._variable = variable.unit_comp
        else:
            self._variable = variable
        self._delta_var = delta_var
        self._delta_h = None
        self.electrons = electrons
        self._base = None

    def __repr__(self):
        return '<Reaction %s + %s --> %s : %s>' % (self.reactant_string,
                self.var_string, self.product_string,
                self.voltage)

    #### attributes
    @property
    def p_comp(self):
        if self.p_natoms == 0:
            return {}
        comp = defaultdict(float)
        for p, amt in self._products.items():
            for elt, amt2 in p.comp.items():
                comp[elt] += amt*amt2
        return comp

    @property
    def p_var_comp(self):
        if self.p_natoms == 0:
            return 1.0
        vamt = sum( p.fraction(self._variable)['var']*amt for p, amt in
                self._products.items())*sum(self.variable.values())
        return vamt/self.p_natoms

    @property
    def p_var_amt(self):
        if self.p_natoms == 0:
            return 1.0
        vamt = sum( p.amt(self._variable)['var']*amt for p, amt in
                self._products.items())*sum(self.variable.values())
        return vamt/self.p_natoms

    @property
    def p_natoms(self):
        return sum( sum(p.unit_comp.values())*amt for p, amt in 
                self._products.items())

    @property
    def r_comp(self):
        if self.r_natoms == 0:
            return {}
        comp = defaultdict(float)
        for r, amt in self._reactants.items():
            for elt, amt2 in r.comp.items():
                comp[elt] += amt*amt2
        return comp

    @property
    def r_var_comp(self):
        if self.r_natoms == 0:
            return 1.0
        vamt = sum( p.fraction(self._variable)['var']*amt for p, amt in
                self._reactants.items())*sum(self.variable.values())
        return vamt/self.r_natoms

    @property
    def r_var_amt(self):
        if self.r_natoms == 0:
            return 1.0
        vamt = sum( r.amt(self._variable)['var']*amt for r, amt in
                self._reactants.items())*sum(self.variable.values())
        return vamt/self.r_natoms

    @property
    def r_bgap(self):
        if not self._reactants:
            return 0.0
        else:
            gaps = [ p.band_gap for p in self._reactants if p.band_gap is not None]
            if not gaps:
                return 0.0
            else:
                return min(gaps)

    @property
    def p_bgap(self):
        if not self._reactants:
            return 0.0
        else:
            gaps = [ p.band_gap for p in self._products if p.band_gap is not None]
            if not gaps:
                return 0.0
            else:
                return min(gaps)

    @property
    def r_natoms(self):
        return sum( sum(p.unit_comp.values())*amt for p, amt in 
                self._reactants.items())

    @property
    def base(self):
        if self._base is None:
            amts = [ amt/sum(phase.nom_comp.values()) for phase, amt in
                                        self._products.items() ]
            amts += [ amt/sum(phase.nom_comp.values()) for phase, amt in
                                        self._reactants.items() ]
            self._base = min(amts)
        return self._base

    @property
    def product_string(self):
        return ' + '.join( '%s %s' % 
                (amt/sum(phase.nom_comp.values())/self.base, phase.name) 
                for phase, amt in self._products.items() )

    @property
    def reactant_string(self):
        return ' + '.join( '%s %s' %
                (amt/sum(phase.nom_comp.values())/self.base, phase.name) 
                for phase, amt in self._reactants.items() )

    @property
    def product_latex(self):
        return ' + '.join( '%s %s' %
                (amt/sum(phase.nom_comp.values())/self.base, phase.latex) 
                for phase, amt in self._products.items() )

    @property
    def reactant_latex(self):
        return ' + '.join( '%s %s' %
                (amt/sum(phase.nom_comp.values())/self.base, phase.latex) 
                for phase, amt in self._reactants.items() )

    @property
    def var_string(self):
        elts = [ '%g %s' % (self.delta_var/self.base*v, k)
                            for k, v in self.variable.items() ]
        return ' + '.join(elts)

    @property
    def var_latex(self):
        return '%s %s' % (self.delta_var, comp_to_latex(self.variable,
            special='reduce'))

    @property
    def react_mass(self):
        if not self._reactants:
            return 0
        return sum( amt*phase.mass for phase, amt in 
                self._reactants.items() ) / sum(self._reactants.values())

    @property
    def prod_mass(self):
        if not self._products:
            return 0
        return sum( amt*phase.mass for phase, amt in 
                self._products.items() ) / sum(self._products.values())

    @property
    def react_vol(self):
        if not self._reactants:
            return 0
        return sum( amt*phase.volume for phase, amt in 
                self._reactants.items() ) / sum(self._reactants.values())

    @property
    def prod_vol(self):
        if not self._products:
            return 0
        return sum( amt*phase.volume for phase, amt in 
                self._products.items() ) / sum(self._products.values())

    @property
    def delta_h(self):
        if self._delta_h is None:
            self.get_delta_h()
        return self._delta_h

    @property
    def delta_var(self):
        if self._delta_var is None:
            self._delta_var = self.p_var_comp - self.r_var_comp
            if self._delta_var == 0:
                self._delta_var = 1 
        return self._delta_var

    @property
    def variable(self):
        if self._variable is None:
            self.get_variable()
        return self._variable

    #### methods

    def get_delta_h(self):
        re = 0.0
        for k, v in self._reactants.items():
            re += v*k.energy
        pe = 0.0
        for k, v in self._products.items():
            pe += v*k.energy
        self._delta_h = re - pe

    @property
    def voltage(self):
        return self.delta_h/self.delta_var/self.electrons
