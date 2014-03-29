#!/usr/bin/python

# sound_waves.py v1.1 12-3-2011 Jeff Doak jeff.w.doak@gmail.com

import sys
import scipy as sp
from scipy import linalg
from scipy.integrate import dblquad
import read_file

BOLTZCONST = 1.381e-23  # J/K
PLANCKCONST = 6.626e-34  # J*s
AVONUM = 6.022e23  # things/mol

def dir_cosines(dir,coords=sp.identity(3)):
    """Returns a vector containing the direction cosines between vector dir, and
    the coordinate system coords. Default coordinate system is an orthonormal
    cartesian coordinate system."""
    cosines = sp.dot(coords,dir)/linalg.norm(dir)
    return cosines

def make_gamma(dc,C):
    """
    Returns a matrix containing the modified set of elastic constants, C,
    transformed by the direction cosines, dc.
    """
    Gamma = sp.zeros((3,3))
    Gamma[0,0] = dc[0]**2*C[0,0]+dc[1]**2*C[5,5]+dc[2]**2*C[4,4]
    Gamma[0,0] += 2*dc[1]*dc[2]*C[4,5]+2*dc[2]*dc[0]*C[0,4]
    Gamma[0,0] += 2*dc[0]*dc[1]*C[0,5]

    Gamma[1,1] = dc[0]**2*C[5,5]+dc[1]**2*C[1,1]+dc[2]**2*C[3,3]
    Gamma[1,1] += 2*dc[1]*dc[2]*C[1,3]+2*dc[2]*dc[0]*C[3,5]
    Gamma[1,1] += 2*dc[0]*dc[1]*C[1,5]

    Gamma[2,2] = dc[0]**2*C[4,4]+dc[1]**2*C[3,3]+dc[2]**2*C[2,2]
    Gamma[2,2] += 2*dc[1]*dc[2]*C[2,3]+2*dc[2]*dc[0]*C[2,4]
    Gamma[2,2] += 2*dc[0]*dc[1]*C[3,4]

    Gamma[0,1] = dc[0]**2*C[0,5]+dc[1]**2*C[1,5]+dc[2]**2*C[3,4]
    Gamma[0,1] += dc[1]*dc[2]*(C[3,5]+C[1,4])+dc[2]*dc[0]*(C[0,3]+C[4,5])
    Gamma[0,1] += dc[0]*dc[1]*(C[0,1]+C[5,5])

    Gamma[0,2] = dc[0]**2*C[0,4]+dc[1]**2*C[3,5]+dc[2]**2*C[2,4]
    Gamma[0,2] += dc[1]*dc[2]*(C[3,4]+C[2,5])+dc[2]*dc[0]*(C[0,2]+C[4,4])
    Gamma[0,2] += dc[0]*dc[1]*(C[0,3]+C[4,5])

    Gamma[1,2] = dc[0]**2*C[4,5]+dc[1]**2*C[1,3]+dc[2]**2*C[2,3]
    Gamma[1,2] += dc[1]*dc[2]*(C[3,3]+C[1,2])+dc[2]*dc[0]*(C[2,5]+C[3,4])
    Gamma[1,2] += dc[0]*dc[1]*(C[1,4]+C[3,5])

    Gamma[1,0] = Gamma[0,1]
    Gamma[2,0] = Gamma[0,2]
    Gamma[2,1] = Gamma[1,2]
    return Gamma

def spherical_integral(C,rho):
    """
    Calculate the integral of a function over a unit sphere.
    """
    # phi - azimuthal angle (angle in xy-plane)
    # theta - polar angle (angle between z and xy-plane)
    #       (  y  , x )
    def func(theta,phi,C,rho):  # Test function. Can I get 4*pi^2????
        x = sp.cos(phi)*sp.sin(theta)
        y = sp.sin(phi)*sp.sin(theta)
        z = sp.cos(theta)
        #dir = sp.array((x,y,z))
        #dc = dir_cosines(dir)
        dc = sp.array((x,y,z))  # Turns out these are direction cosines!
        Gamma = make_gamma(dc,C)
        rho_c_square = linalg.eigvals(Gamma).real  # GPa
        rho_c_square = rho_c_square*1e9  # Pa
        sound_vel = sp.sqrt(rho_c_square/rho)  # m/s
        integrand = 1/(sound_vel[0]**3) + 1/(sound_vel[1]**3) + 1/(sound_vel[2]**3)
        return integrand*sp.sin(theta)
    #        (  y  , x      )
    #def sfunc(theta,phi,args=()):
    #    return func(theta,phi,args)*sp.sin(theta)

    integral,error = dblquad(func,0,2*sp.pi,lambda g: 0,lambda h:
            sp.pi,args=(C,rho))
    return integral


#direction = sp.array((1.0,1.0,1.0))
#dc = dir_cosines(direction)
#C = read_file.read_file(sys.argv[1])
#C.pop(0)
#C = sp.array(C,float)
#Gamma = make_gamma(dc,C)
#density = 7500 #kg/m**3
#density = float(read_file.read_file(sys.argv[2])[0][0])
#rho_c_square = linalg.eigvals(Gamma) #GPa
#rho_c_square = rho_c_square*1e9 #Pa
#sound_vel = sp.sqrt(rho_c_square/density).real
#avg_vel = sp.average(sound_vel)
#print Gamma
#print direction
#print C
#print rho_c_square
#print rho_c_square.real
#print sound_vel," in m/s"
#print avg_vel
#print spherical_integral(C,density)

def main(argv):
    C = read_file.read_file(argv[0])
    C.pop(0)
    C = sp.array(C,float)
    density,natoms,molmass = read_file.read_file(argv[1])[0]
    density = float(density)  # kg/m**3
    natoms = int(natoms)
    molmass = float(molmass)  # kg/mol
    integral = spherical_integral(C,density)  # (s/m)**3
    mean_vel = (integral/12./sp.pi)**(-1/3.)
    debeye_temp = PLANCKCONST/BOLTZCONST*(3.*natoms*AVONUM*
                      density/4./sp.pi/molmass)**(1/3.)*mean_vel
    print debeye_temp,mean_vel



if __name__ == "__main__":
    main(sys.argv[1:])
