#!/bin/sh
#SBATCH -C quad,cache
#SBATCH -p knlall
#SBATCH -t 48:00:00
#SBATCH -N {nodes}
#SBATCH --ntasks-per-node={ppn}
#SBATCH -J {name}

export OMP_NUM_THREADS=1
ulimit -s unlimited
export OMP_PROC_BIND=true
export OMP_PLACES=threads
export MKL_FAST_MEMORY_LIMIT=0

NPROCS={ppn}

#running on {host}

{header}

{mpi} {binary} {pipes}

{footer}
