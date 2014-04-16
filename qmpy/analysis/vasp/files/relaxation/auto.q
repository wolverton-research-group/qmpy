#!/bin/bash
#PBS -l nodes=1:ppn=1
#PBS -l walltime=01:00:00:00
#PBS -N 23891_relaxation
#PBS -o jobout.txt
#PBS -e joberr.txt

cd $PBS_O_WORKDIR
NPROCS=`wc -l < $PBS_NODEFILE`
#running on palestrina

gunzip -f CHGCAR.gz &> /dev/null
date +%s
ulimit -s unlimited

 /usr/local/bin/vasp_53_serial  > stdout.txt 2> stderr.txt

gzip -f CHGCAR OUTCAR PROCAR ELFCAR
rm -f WAVECAR CHG
date +%s
