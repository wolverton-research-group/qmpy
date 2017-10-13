#!/bin/bash -l
#SBATCH -p regular
#SBATCH -N {nodes}
#SBATCH -t {walltime}
#SBATCH -A {key}
#SBATCH -o job.oe
#SBATCH -J {name}
#SBATCH -C knl,quad,cache

#OpenMP settings:
export OMP_NUM_THREADS={threads}
export OMP_PLACES=threads
export OMP_PROC_BIND=true

#Cori Parameters:
cpu_per_core={cpu_per_core}
cpu_per_task={cpu_per_task}
nodes={nodes}
mpi_task=`echo $nodes*{ppn}*$cpu_per_core/$cpu_per_task | bc`

ulimit -s unlimited
module load vasp/20170629-knl


#running on {host}
{header}

{mpi} {binary} {pipes}

{footer}

