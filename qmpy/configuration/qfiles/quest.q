#!/bin/bash
#SBATCH -N {nodes}
#SBATCH -n {ntasks}
#SBATCH -t {walltime}
#SBATCH -J {name}
#SBATCH -A {key}
#SBATCH -p {queuetype}
#SBATCH -o jobout.txt

ulimit -s unlimited
export OMP_NUM_THREADS=1

module purge

module load mpi/openmpi-1.6.5-intel2013.2

NPROCS={ntasks}
#running on {host}

{header}

{mpi} {binary} {pipes}

{footer}
