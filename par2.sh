#!/bin/bash
#BSUB -q hpc
#BSUB -n 4
#BSUB -W 00:30
#BSUB -R "select[model==XeonGold6226R]"
#BSUB -R "rusage[mem=16GB]"
#BSUB -o par2.out
#BSUB -e par2.err 
#BSUB -N
#BSUB -R "span[hosts=1]"
#BSUB -J par2

time python simulate_parallelized_static.py 100 2