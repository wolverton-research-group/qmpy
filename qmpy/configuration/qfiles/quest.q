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

module load mpi/intel-mpi-5.1.3.258 
module swap intel/2016.0 intel/2013.2

NPROCS={ntasks}

#running on {host}

{header}

{mpi} {binary} {pipes}

{footer}
