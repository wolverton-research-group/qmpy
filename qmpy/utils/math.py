"""qmpy.utils.math

Some mathematical functions which are used periodically.

"""
import qmpy
import numpy as np
from numpy.linalg import norm
import logging

logger = logging.getLogger(__name__)

def _gcd(a,b):
    """
    Returns greatest common denominator of two numbers.
    
    Example:
    >>> _gcd(4, 6)
    2
    """
    while b:
        a,b=b,a%b
    return a

def gcd(numbers):
    """
    Returns greatest common denominator of an iterator of numbers.

    Example:
    >>> gcd(12, 20, 32)
    4
    """
    numbers = list(numbers)
    if len(numbers) == 1:
        return numbers[0]
    a=numbers.pop()
    b=numbers.pop()
    tmp_gcd = _gcd(a,b)
    while numbers:
        tmp_gcd = _gcd(tmp_gcd,numbers.pop())
    return tmp_gcd

def is_integer(number, tol=1e-5):
    number = float(number)
    return abs(round(number) - number) < tol
        
def roundclose(v, tol=1e-8):
    if is_integer(v, tol=tol):
        return int(round(v))
    else:
        return v

def isclose(v1, v2, tol=1e-6):
    """
    Test if v1 and v2 are with `tol` of one another`.
    Examples::
        >>> if isclose(0.5, 0.49999999):
                print 'True'
        True
    """
    return abs(v1 - v2) < tol

def lcm(a,b):
    """
    Returns least common multiple of two numbers.

    Example:
    >>> lcm(20,10)
    20
    """
    return a*b/gcd([a,b])

def ffloat(string):
    """
    In case of fortran digits overflowing and returing ********* this
    fuction will replace such values with 1e9
    """

    if 'nan' in string.lower():
        return 1e9
    try:
        new_float = float(string)
    except ValueError:
        if '*******' in string:
            new_float = 1e9
        else:
            return None
    return new_float

def angle(x, y, radians=False):
    """Return the angle between two lattice vectors

    Examples:
    >>> angle([1,0,0], [0,1,0])
    90.0
    """
    if radians:
        return np.arccos(np.dot(x,y)/(norm(x)*norm(y)))
    else:
        return np.arccos(np.dot(x,y)/(norm(x)*norm(y)))*180./np.pi

def basis_to_latparams(basis, radians=False):
    """Returns the lattice parameters [a, b, c, alpha, beta, gamma].
    
    Example:
        
    >>> basis_to_latparams([[3,0,0],[0,3,0],[0,0,5]])
    [3, 3, 5, 90, 90, 90]
    """

    va, vb, vc = basis
    a = np.linalg.norm(va)
    b = np.linalg.norm(vb)
    c = np.linalg.norm(vc)
    alpha = angle(vb, vc, radians=radians)
    beta = angle(vc, va, radians=radians)
    gamma = angle(va, vb, radians=radians)
    return [a, b, c, alpha, beta, gamma]

def latparams_to_basis(latparam, radians=False):
    """Convert a 3x3 basis matrix from the lattice parameters.

    Example:
    >>> latparams_to_basis([3, 3, 5, 90, 90, 90])
    [[3,0,0],[0,3,0],[0,0,5]]

    """
    basis = []
    a, b, c = latparam[0:3]
    alpha, beta, gamma = latparam[3:6]

    if not radians:
        alpha *= np.pi/180
        beta *= np.pi/180
        gamma *= np.pi/180

    basis.append([a, 0, 0])
    basis.append([b*np.cos(gamma), b*np.sin(gamma), 0 ])
    cx = np.cos(beta)
    cy = (np.cos(alpha) - np.cos(beta)*np.cos(gamma))/np.sin(gamma)
    cz = np.sqrt(1. - cx*cx - cy*cy)
    basis.append([c*cx, c*cy, c*cz])
    basis = np.array(basis)
    basis[abs(basis) < 1e-10] = 0
    return basis

def basis_to_metmat(lat_vecs):
    A,B,C = lat_vecs
    a = np.dot(A,A)
    b = np.dot(B,B)
    c = np.dot(C,C)
    d = np.dot(B,C)
    e = np.dot(A,C)
    f = np.dot(A,B)
    return np.array([[a, f, e],
                     [f, b, d],
                     [e, d, c]])

def basis_to_niggli(lat_vecs):
    A,B,C = lat_vecs
    a = np.dot(A,A)
    b = np.dot(B,B)
    c = np.dot(C,C)
    ksi = 2*np.dot(B,C)
    eta = 2*np.dot(A,C)
    zeta = 2*np.dot(A,B)
    return np.array([[a,b,c],[ksi,eta,zeta]])

def niggli_to_basis(S):
    met_mat = [[S[0,0], S[1,2]/2, S[0,2]/2],
               [S[1,2]/2, S[1,1], S[0,1]/2],
               [S[0,2]/2, S[0,1]/2, S[2,2]]]
    return metmat_to_basis(met_mat)

def niggli_to_latparams(S):
    met_mat = [[S[0,0], S[1,2]/2, S[0,2]/2],
               [S[1,2]/2, S[1,1], S[0,1]/2],
               [S[0,2]/2, S[0,1]/2, S[2,2]]]
    return metmat_to_latparams(met_mat)

def metmat_to_latparams(met_mat):
    a = np.sqrt(abs(G[0,0]))
    b = np.sqrt(abs(G[1,1]))
    c = np.sqrt(abs(G[2,2]))
    al = np.arccos(G[1,2]/abs(b*c))*180/np.pi
    be = np.arccos(G[0,2]/abs(a*c))*180/np.pi
    ga = np.arccos(G[0,1]/abs(a*b))*180/np.pi
    return (a,b,c,al,be,ga)

def metmat_to_basis(met_mat):
    lp = metmat_to_latparams(met_mat)
    return latparams_to_basis(lp)

def coord_to_point(coord):
    if len(coord) == 1:
        return [0]
    elif len(coord) == 2:
        return [coord_to_bin(coord)]
    elif len(coord) == 3:
        return coord_to_gtri(coord)
    elif len(coord) == 4:
        return coord_to_gtet(coord)

def coord_to_bin(coord):
    """Convert a binary composition to an x-coordinate value:
    returns ( A )
    
    """
    return coord[0]

def coord_to_gtri(coord):
    """Convert a ternary composition to an x,y-coordinate pair:
    ( A+B/2, B*3^(1/2)/2 )
    
    """
    return (coord[0] + coord[1]/2., 
            coord[1]*np.sqrt(3)/2)

def coord_to_gtet(coord):
    """Convert a quaternary composition to an x,y,z triplet:
    ( A/2+B+C/2, A*3^(1/2)/2 + C*3^(1/2)/6, C*(2/3)^(1/2) )
    
    """
    return (coord[0]/2 + coord[1] + coord[2]/2,
        coord[0]*np.sqrt(3)/2 + coord[2]*np.sqrt(3)/6.,
        coord[2]*np.sqrt(2./3))

def triple_prod(matrix):
    return np.dot(matrix[0], np.cross(matrix[1], matrix[2]))

def sign(x):
    if x > 0:
        return 1
    else:
        return -1

def entire(x):
    return np.floor(x)

def wrap(x, tol=1e-4):
    x -= np.floor(x)
    x[abs(x) < tol] = 0
    x[abs(abs(x) - 1) < tol] = 0
    return x
