#!/bin/bash
#PBS -l nodes={nodes}:ppn={ppn}
#PBS -l walltime={walltime}
#PBS -N {name}
#PBS -o jobout.txt
#PBS -e joberr.txt

cd $PBS_O_WORKDIR
NPROCS=`wc -l < $PBS_NODEFILE`
#running on {host}

{header}

{mpi} {binary} {pipes}

{footer}
