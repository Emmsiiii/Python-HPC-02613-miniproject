#!/bin/bash
#BSUB -q hpc
#BSUB -n 4
#BSUB -W 00:30
#BSUB -R "select[model==XeonGold6226R]"
#BSUB -R "rusage[mem=16GB]"
#BSUB -o par_dy2.out
#BSUB -e par_dy2.err 
#BSUB -N
#BSUB -R "span[hosts=1]"
#BSUB -J par_dy2

time python simulate_parallelized_dynamic.py 100 2 5