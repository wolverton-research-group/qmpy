#!/bin/bash -l
#SBATCH --partition=regular
#SBATCH --nodes={nodes}
#SBATCH --time=02:00:00
#SBATCH --job-name={name}
#SBATCH --account={key}
#SBATCH --ntasks-per-node=24
#SBATCH --output=job.oe

#qmpy = {nodes}:{ppn}
ulimit -s unlimited
export OMP_NUM_THREADS=1
module load vasp/5.4.1

#running on {host}

{header}

{mpi} {binary} {pipes}

{footer}

