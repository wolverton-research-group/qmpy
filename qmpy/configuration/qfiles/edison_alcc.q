#!/bin/bash -l
#SBATCH --partition=regular
#SBATCH --nodes={nodes}
#SBATCH --time={walltime}
#SBATCH --job-name={name}
#SBATCH --account={key}
#SBATCH --ntasks-per-node=24
#SBATCH --output=job.oe

#qmpy = {nodes}:{ppn}
ulimit -s unlimited
export OMP_NUM_THREADS=1
module load vasp/5.4.1

##rm -f STOPCAR
##conf=`grep "SBATCH --job-name" $0 |head -n 1 |awk -F= '{{print $NF}}' |awk -F_ '{{print $NF}}'`
##if [[ $conf == 'hse06' ]]
##    then
##    SLEEPTIME=$(grep "SBATCH --time" $0 |head -n 1 |awk -F= '{{print $NF}}' |awk -F: '{{print -600+3600*$1+60*$2+$3}}')
##    (sleep $SLEEPTIME ; touch STOPCAR ; echo "LABORT = .TRUE." >> STOPCAR) &
##fi

#running on {host}

{header}

{mpi} {binary} {pipes}

{footer}

