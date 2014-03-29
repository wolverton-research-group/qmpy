#!/usr/bin/python

# debye_model.py v0.0 12-3-2011 Jeff Doak jeff.w.doak@gmail.com

import sys
import scipy as sp
from scipy.integrate import quad
import read_file

BOLTZCONST = 8.617e-2  # meV/K/atom

def debye_func(x):
    """
    Calculate the debye function D(x) = 3*x**(-2)*Integral(z**3/exp(z-1)dz,2,x)
    """
    def func(z):
        f = z**3./(sp.exp(z)-1)
        return f

    integral,error = quad(func,0,x)
    D = integral*3.*x**(-3.)
    return D

def debye_E_zp(thetaD,natoms):
    """
    Returns the zero-point energy of the Debeye model in meV/atom.
    """
    E_zp = 9*natoms*BOLTZCONST*thetaD/8.
    return E_zp

def debye_E_vib(T,thetaD,natoms):
    """
    Returns the vibrational energy of the Debeye model (including zero-point
    energy) at a given temperature, T, in meV/atom.
    """
    E_vib = 9*thetaD/8. + 3*T*debye_func(thetaD/T)
    E_vib = natoms*BOLTZCONST*E_vib
    return E_vib

def debye_S_vib(T,thetaD,natoms):
    """
    Returns the vibrational entropy of the Debeye model at a given temperature,
    T, in meV/atom/K.
    """
    S_vib = 4*debye_func(thetaD/T)-3*sp.log(1-sp.exp(-thetaD/T))
    S_vib = natoms*BOLTZCONST*S_vib
    return S_vib

def debye_C_V(T,thetaD,natoms):
    """
    Returns the heat capacity at constant volume, C_V, of the Debeye model at a
    given temperature, T, in meV/atom/K.
    """
    C_V = 4*debye_func(thetaD/T)-3*(thetaD/T)/(sp.exp(thetaD/T)-1.)
    C_V = 3*natoms*BOLTZCONST*C_V
    return C_V

if __name__ == "__main__":
    thetaD,natoms = read_file.read_file(sys.argv[1])[0]
    thetaD = float(thetaD)
    natoms = int(natoms)
    temp = sp.linspace(0,2000,201)
    temp[0] = 1.0
    #reduced_temp = thetaD/temp
    E_zp = 9*natoms*BOLTZCONST*thetaD/8.
    #E_zp = 9*BOLTZCONST*thetaD/8.
    E_vib = sp.array([])
    S_vib = sp.array([])
    C_V = sp.array([])
    for T in temp:
        D = debye_func(thetaD/T)
        E_vib = sp.append(E_vib,natoms*BOLTZCONST*(E_zp + 3*T*D))
        #E_vib = sp.append(E_vib,BOLTZCONST*(E_zp + 3*T*D))
        S_vib = sp.append(S_vib,natoms*BOLTZCONST*(4*D - 
        #S_vib = sp.append(S_vib,BOLTZCONST*(4*D - 
                    3*sp.log(1-sp.exp(-thetaD/T))))
        C_V = sp.append(C_V,3*natoms*BOLTZCONST*(4*D - 
        #C_V = sp.append(C_V,3*BOLTZCONST*(4*D - 
                  3*(thetaD/T)/(sp.exp(thetaD/T)-1.)))
    F_vib = E_vib - T*S_vib
    #print E_vib
    #print S_vib
    #print F_vib
    print 3*BOLTZCONST
    print "T_(K) E_vib_(meV/atom) S_vib_(meV/atom/K) F_vib_(meV/atom) C_V_(meV/atom/K)"
    for i in range(len(temp)):
        print temp[i],E_vib[i],S_vib[i],F_vib[i],C_V[i]

