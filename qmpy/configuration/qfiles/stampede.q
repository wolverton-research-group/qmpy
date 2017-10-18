#!/bin/bash
#SBATCH -J {name}             # Job name
#SBATCH -o jobout.txt         # Name of stdout output file (%j expands to jobId)
#SBATCH -p normal             # Queue name
#SBATCH -N 1                  # Total number of nodes requested (16 cores/node)
#SBATCH -n 16                 # Total number of mpi tasks requested
#SBATCH -t 48:00:00           # Run time (hh:mm:ss) - 1.5 hours

module add intel/13.0.2.146   
module add mvapich2/1.9a2 

export I_MPI_PIN=0
export OMP_NUM_THREADS=1
ulimit -s unlimited
export VASP="/home1/03780/jh2336/Software/bin/vasp_dynamic_nosca"

ibrun $VASP &> STD.OUT

