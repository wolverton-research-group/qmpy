#!/bin/bash
#MSUB -l nodes={nodes}:ppn={ppn}
#MSUB -l walltime={walltime}
#MSUB -N {name}
#MSUB -A {key}
#MSUB -q normal
#MSUB -o jobout.txt
#MSUB -e joberr.txt

module load intel/2011.3
module load mpi/openmpi-1.6.3-intel2011.3
# module load intel/2011.3
ulimit -s unlimited

cd $PBS_O_WORKDIR
NPROCS=`wc -l < $PBS_NODEFILE`
#running on {host}

{header}

{mpi} {binary} {pipes}

{footer}
