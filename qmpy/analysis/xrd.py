#!/usr/env/bin python

import itertools
import numpy as np
from symmetry.routines import find_structure_symmetry
import logging

from qmpy.data import elements
from qmpy.utils import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Peak(object):
    """
    Attributes:
      angle (float): 
        Peak 2*theta angle in radians.
      hkl (list): 
        HKL indices of the peak.
      multiplicity (int): 
        Number of HKL indices which generate the peak.

    """
    def __init__(self, angle, multiplicity=None, intensity=None, hkl=None,
                              xrd=None, width=None, measured=False):
        self.angle = angle
        self.two_theta = angle*360/np.pi
        self.hkl = hkl
        self.multiplicity = multiplicity
        self.intensity = intensity
        self.xrd = xrd
        self.width = width
        self.measured = measured

        self.real = None
        self.imag = None

    def lp_factor(self):
        """
        Calculates the Lorentz-polarization factor.
        
        http://reference.iucr.org/dictionary/Lorentz%E2%80%93polarization_correction
        """
        num = (1+np.cos(2*self.angle)**2)
        den = np.cos(self.angle)*np.sin(self.angle)**2
        return num/den

    def calculate_intensity(self, bfactors=None, scale=None):
        intensity = self.structure_factor_squared(bfactors)
        self.intensity = intensity * scale
        self.intensity *= self.multiplicity
        self.intensity *= self.lp_factor()
        return self.intensity

    def thermal_factor(self, bfactor=1.0):
        """
        Calculates the Debye-Waller factor for a peak.

        http://en.wikipedia.org/wiki/Debye-Waller_factor
        """
        return np.exp(-bfactor*(np.sin(self.angle)/self.xrd.wavelength)**2)

    def atomic_scattering_factor(self, element):
        asfp = elements[element]['scattering_factors']
        s = np.sin(self.angle) / self.xrd.wavelength
        s2 = s*s
        if s > 2:
            msg = 'Atomic scattering factors are not optimized for'
            msg += ' s greater than 2'
            logger.warn(msg)

        factors = [ asfp['a'+str(i)]*np.exp(-asfp['b'+str(i)]*s2) 
                                              for i in range(1,5) ]
        return sum(factors) + asfp['c']

    def structure_factor_squared(self, bfactors=None):
        if bfactors is None:
            bfactors = [ 1.0 for o in self.xrd.structure.orbits ]

        real = 0.0
        imag = 0.0

        for bfactor, orbit in zip(bfactors, self.xrd.structure.orbits):
            tf = self.thermal_factor(bfactor)
            for site in orbit:
                for atom in site:
                    sf = self.atomic_scattering_factor(atom.element_id)
                    dot = 2*np.pi*np.dot(self.hkl[0], atom.coord)
                    pre = sf * tf * atom.occupancy
                    real += pre*np.cos(dot) 
                    imag += pre*np.sin(dot)

        self.real = real
        self.imag = imag
        return real*real + imag*imag

class XRD(object):
    """
    Container for an X-ray diffraction pattern.

    Attributes:
      peaks (List): 
        List of :mod:`~qmpy.Peak` instances.
      measured (bool): 
        True if the XRD is a measured pattern, otherwise False.
      min_2th (float): 
        Minimum 2theta angle allowed. Defaults to 60 degrees.
      max_2th (float): 
        Maximum 2theta angle allowed. Defaults to 10 degrees.
      wavelength (float): 
        X-ray wavelength. Defaults to 1.5418 Ang.
      resolution (float): 
        Minimum 2theta angle the XRD will distinguish between.

    """
    def __init__(self, structure=None, measured=False, wavelength=1.5418,
            min_2th=10, max_2th=60, resolution=1e-2):
        self.peaks = []
        self.structure = structure
        self.measured = measured
        self.wavelength = wavelength
        self.min_2th = min_2th
        self.max_2th = max_2th
        self.resolution = resolution

    def add_peak(self, peak):
        for p in self.peaks:
            if abs(peak.two_theta - p.two_theta) < self.resolution:
                p.multiplicity += peak.multiplicity
                p.hkl.append(peak.hkl)
                return
        peak.xrd = self
        self.peaks.append(peak)

    def d_thermal_factor(angle, bfactor):
        temp = (np.sin(angle) / self.wavelength)**2
        return -temp * np.exp(-bfactor*temp)

    def bragg_angle(self, hkl):
        ratio = np.linalg.norm(self.structure.inv.dot(hkl))/2
        ratio *= self.wavelength
        if (ratio >=-1 and ratio <= 1):
            return np.arcsin(ratio)
        elif angle < -1:
            return -np.pi/2
        else:
            return np.pi/2

    def get_intensities(self, bfactors=None, scale=None):
        """
        Loops over all peaks calculating intensity.

        Keyword Arguments:
          bfactors (list) : list of B factors for each atomic site. Care must
            taken to ensure that the order of B factors agrees with the order
            of atomic orbits.
          scale (float) : Scaling factor to multiply the intensities by. If
            scale evaluates to False, the intensities will be re-normalized at
            the end such that the highest peak is 1.
        """
        rescale = False
        if not scale:
            rescale = True
            scale = 1.0

        for peak in self.peaks:
            peak.calculate_intensity(bfactors=bfactors, scale=scale)

        if rescale:
            m = max([ p.intensity for p in self.peaks ])
            for p in self.peaks:
                p.intensity /= m

    def get_peaks(self):
        """
        """

        max_mag = 2*np.sin(self.max_2th*np.pi/90) / self.wavelength
        self.structure.symmetrize()
        rots = []
        for r in self.structure.rotations:
            if np.allclose(r, np.eye(3)):
                continue
            if not any([np.allclose(r, rr) for rr in rots]):
                rots.append(r)

        im, jm, km = map(lambda x: int(np.ceil(max_mag*x)), 
                 self.structure.lat_params[:3])

        for h,k,l in itertools.product(range(-im, im+1), 
                                       range(-jm, jm+1),
                                       range(-km, km+1)):
            if [h,k,l] == [0,0,0]:
                continue

            mult = 1
            hkl = np.array([h,k,l])
            equiv = [hkl]
            repeat = False
            for rot in rots:
                thkl = np.dot(rot, hkl)
                if thkl[0] < hkl[0] - 1e-4:
                    repeat = True
                elif abs(thkl[0]-hkl[0]) < 1e-4:
                    if thkl[1] < hkl[1] - 1e-4:
                        repeat = True
                    elif abs(thkl[1]-hkl[1]) < 1e-4:
                        if thkl[2] < hkl[2] - 1e-4:
                            repeat = True
                if repeat:
                    break

                if not any([ np.allclose(thkl, shkl) for shkl in equiv ]):
                    equiv.append(thkl)
                    mult += 1

            angle = self.bragg_angle(hkl)
            two_theta = angle*360/np.pi

            if two_theta > self.max_2th or two_theta < self.min_2th:
                continue

            peak = Peak(angle, multiplicity=mult, hkl=equiv)
            self.add_peak(peak)

    def plot(self):
        renderer = Renderer()

        for p in self.peaks:
            l = Line([[p.two_theta, 0], 
                      [p.two_theta, p.intensity]], color='grey')
            renderer.add(l)

        renderer.xaxis.label = "2&Theta;"
        renderer.yaxis.max = 1.0
        renderer.xaxis.min = self.min_2th
        renderer.xaxis.max = self.max_2th
        return renderer
