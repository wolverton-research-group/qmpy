#!/bin/bash -l
#SBATCH --partition=shared
#SBATCH --nodes=1
#SBATCH --time={walltime}
#SBATCH --job-name={name}
#SBATCH --account={key}
#SBATCH --ntasks-per-node=12
#SBATCH --output=job.oe

#qmpy = {nodes}:{ppn}
ulimit -s unlimited
export OMP_NUM_THREADS=1
NPROCS=12

#running on {host}

{header}

{mpi} {binary} {pipes}

{footer}

