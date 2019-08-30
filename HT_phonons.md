# HT_phonons to do

## qmpy/analysis/vasp/phonon_calculation.py
### class PhononCalculation(models.Model) 
- one-to-one 
- one-to-many
- many-to-many 
- read forces for all supercell
- fit FCs using CSLD
- caluclate various properties from 2nd order and store them as properties
- interface with shengBTE to calculation conductivity
- render plots of phonon disperson, T-dependent phase diagram
- raw FCs available for download

## qmpy/computing/queue.py
### class Job(models.Model)
- create(): modify to handle mutiple supercell
- copy all supercells, generate batch scripts (SLURM) to run supercells, and copy back

## qmpy/computing/scripts.py
### class 
