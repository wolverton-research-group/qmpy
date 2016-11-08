#!/usr/bin/env python
# miedema.py v1.6 12-13-2012 Jeff Doak jeff.w.doak@gmail.com
# adapted by S. Kirklin 1/7/14
import numpy as np
import sys
import yaml
import logging

import qmpy
from qmpy.utils import *

logger = logging.getLogger(__name__)

__all__ = ['Miedema']
# data rows: 
# Element_name Phi Rho Vol Z Valence TM? RtoP Htrans
params = yaml.load(open(qmpy.INSTALL_PATH+'/data/miedema.yml').read())

class Miedema(object):

    def __init__(self, composition):
        """
        Takes a variety of composition representations and returns the miedema
        model energy, if possible.

        Examples::

            >>> get_miedema_energy({"Fe":0.5, "Ni":0.5})
            -0.03
            >>> get_miedema_energy({'Fe':2, 'Ni':2})
            -0.03
            >>> get_miedema_energy('FeNi')
            -0.03
            >>> composition = Composition.get('FeNi')
            >>> get_miedema_energy(composition)
            -0.03

        Returns:
            Energy per atom. (eV/atom)
            
        """
        self.energy = None
        # validate composition
        if isinstance(composition, basestring):
            composition = parse_comp(composition)
        elif isinstance(composition, qmpy.Composition):
            composition = dict(composition.comp)
        elif isinstance(composition, dict):
            pass
        else:
            raise TypeError('Unrecognized composition:', composition)

        if len(composition) != 2:
            return None

        if not all( params[k] for k in composition ):
            self.energy = None
            return

        composition = unit_comp(composition)
        self.elt_a, self.elt_b = composition.keys()
        self.x = composition[self.elt_b]
        self.A = params[self.elt_a]
        self.B = params[self.elt_b]
        self.energy = self.H_form_ord()

    @property
    def P(self):
        """
        Chooses a value of P based on the transition metal status of the elements
        A and B. 
        
        There are 3 values of P for the cases where:
            both A and B are TM
            only one of A and B is a TM
            neither are TMs.
        """
        possibleP = [14.2,12.35,10.7]
        if (self.A[5] + self.B[5]) == 2:
            # Both elementA and elementB are Transition Metals.
            return possibleP[0]
        elif (self.A[5] + self.B[5]) == 1:
            # Only one of elementA and elementB are Transition Metals.
            return possibleP[1]
        else:
            # Neither elementA nor elementB are Transition Metals.
            return possibleP[2]

    @property
    def RtoP(self):
        """Calculate and return the value of RtoP based on the transition metal
        status of elements A and B, and the elemental values of RtoP for elements A
        and B."""
        # List of Transition Metals as given in Fig 2.28 of 
        # de Boer, et al., Cohesion in Metals (1988) (page 66).
        tmrange = []
        tmrange.extend(range(20,30))
        tmrange.extend(range(38,48))
        tmrange.extend(range(56,58))
        tmrange.extend(range(72,80))
        tmrange.extend([90,92,94])
        # List of Non-Transition Metals as given in Fig 2.28 of 
        # de Boer, et al., Cohesion in Metals (1988) (page 66).
        nontmrange = []
        nontmrange.extend(range(3,8))
        nontmrange.extend(range(11,16))
        nontmrange.extend([19])
        nontmrange.extend(range(30,34))
        nontmrange.extend([37])
        nontmrange.extend(range(48,52))
        nontmrange.extend([55])
        nontmrange.extend(range(80,84))
        # If one of A,B is in tmrange and the other is in nontmrange, set RtoP
        # to the product of elemental values, otherwise set RtoP to zero.
        if (self.A[3] in tmrange) and (self.B[3] in
                nontmrange):
            RtoP = self.A[6]*self.B[6]
        elif (self.A[3] in nontmrange) and (self.B[3] in
                tmrange):
            RtoP = self.A[6]*self.B[6]
        else:
            RtoP = 0.0
        return RtoP

    @property
    def a_A(self):
        return self.pick_a(self.elt_a)

    @property
    def a_B(self):
        return self.pick_a(self.elt_b)

    def pick_a(self, elt):
        """Choose a value of a based on the valence of element A."""
        possible_a = [0.14,0.1,0.07,0.04]
        if elt == self.elt_a:
            params = self.A
        else:
            params = self.B
        if params[4] == 1:
            return possible_a[0]
        elif params[4] == 2:
            return possible_a[1]
        elif params[4] == 3:
            return possible_a[2]
        #elif elementA in ["Ag","Au","Ir","Os","Pd","Pt","Rh","Ru"]:
        elif elt in ["Ag","Au","Cu"]:
            return possible_a[2]
        else:
            return possible_a[3]

    @property
    def gamma(self):
        """Calculate and return the value of Gamma_AB (= Gamma_BA) for the solvation
        of element A in element B."""
        QtoP = 9.4  # Constant from Miedema's Model.
        phi = [self.A[0], self.B[0]]
        rho = [self.A[1], self.B[1]]
        d_phi = phi[0] - phi[1]
        d_rho = rho[0] - rho[1]
        m_rho = (1/rho[0] + 1/rho[1])/2.
        gamma = self.P*(QtoP*d_rho**2 - d_phi**2 - self.RtoP)/m_rho
        return int(round(gamma))

    def H_form_ord(self):
        """Calculate the enthalpy of formation for an ordered compound of elements A
        and B with a composition xB of element B."""
        vol0_A = self.A[2]
        vol0_B = self.B[2]
        phi = [self.A[0], self.B[0]]
        htrans = [self.A[7], self.B[7]]
        # Determine volume scale parameter a.
        # Calculate surface concentrations using original volumes.
        c_S_A = (1-self.x)*vol0_A/((1-self.x)*vol0_A+self.x*vol0_B)
        c_S_B = self.x*vol0_B/((1-self.x)*vol0_A+self.x*vol0_B)
        # Calculate surface fractions for ordered compounds using original volumes.
        f_BA = c_S_B*(1+8*(c_S_A*c_S_B)**2)
        f_AB = c_S_A*(1+8*(c_S_A*c_S_B)**2)
        # Calculate new volumes using surface fractions (which use original
        # volumes).
        vol_A = vol0_A*(1+self.a_A*f_BA*(phi[0]-phi[1]))
        vol_B = vol0_B*(1+self.a_B*f_AB*(phi[1]-phi[0]))
        # Recalculate surface concentrations using new volumes.
        c_S_A = (1-self.x)*vol_A/((1-self.x)*vol_A+self.x*vol_B)
        c_S_B = self.x*vol_B/((1-self.x)*vol_A+self.x*vol_B)
        # Recalculate surface fractions for ordered compounds using new volumes.
        f_BA = c_S_B*(1+8*(c_S_A*c_S_B)**2)
        f_AB = c_S_A*(1+8*(c_S_A*c_S_B)**2)
        D_htrans = self.x*htrans[1]+(1-self.x)*htrans[0]
        H_ord = (self.gamma*(1-self.x)*self.x*vol_A*vol_B*(1+8*(c_S_A*c_S_B)**2)/
                ((1-self.x)*vol_A+self.x*vol_B) + D_htrans)
        return round(H_ord*0.01036427, 2)

    @staticmethod
    def get(composition):
        return Miedema(composition).energy

