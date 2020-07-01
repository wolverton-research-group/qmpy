#!/bin/sh
#SBATCH -J {name}
#SBATCH -p RM
#SBATCH -N {nodes}
#SBATCH -t 48:00:00
#SBATCH -A mr4s8rp
#SBATCH --ntasks-per-node={ppn}

module load intel/19.3
export I_MPI_JOB_RESPECT_PROCESS_PLACEMENT=0

NPROCS={ppn}

#running on {host}

{header}

{mpi} {binary} {pipes}

{footer}
