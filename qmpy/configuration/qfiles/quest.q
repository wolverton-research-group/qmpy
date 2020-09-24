#!/bin/bash
#SBATCH -N {nodes}
#SBATCH -n {ntasks}
#SBATCH -t {walltime}
#SBATCH -J {name}
#SBATCH -A {key}
#SBATCH -p {queuetype}
#SBATCH -o jobout.txt

ulimit -s unlimited
module load mpi/openmpi-1.6.5-intel2013.2
module load scalapack/2.0.2_gcc483  fftw/3.3.3-gcc

NPROCS={ntasks}

#running on {host}

{header}

{mpi} {binary} {pipes}

{footer}
