# HT_phonons to do

## qmpy/analysis/vasp/phonon_calculation.py
- [ ] class PhononCalculation(models.Model) 
  - one-to-one to `qmpy.materials.Entry`
  - one-to-many to `qmpy.materials.Structure`
  - many-to-many to `qmpy.analysis.vasp.calculation`
  - read forces for all supercell
  - fit FCs using CSLD
  - caluclate various properties from 2nd order and store them as properties
  - interface with shengBTE to calculation conductivity
  - render plots of phonon disperson, T-dependent phase diagram
    - Try `plotly.offline`
  - raw FCs available for download

## qmpy/computing/queue.py
- [ ] class Job(models.Model)
  - create(): modify to handle mutiple supercell
  - copy all supercells, generate batch scripts (SLURM) to run supercells, and copy back

## qmpy/computing/scripts.py
- [x] phonon_relaxation():
  - `Calculation(configuration=‘phonon_relaxation’)`
  - `configuration/vasp_settings/inputs/phonon_relaxation.yml` with the settings:
    - ADDGRID = .True.
    - EDIFF = -1E-3
  - update `configuration/vasp_incar_format/incar_tag_groups.yml`
