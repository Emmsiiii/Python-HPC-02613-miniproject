#!/bin/bash
#BSUB -q hpc
#BSUB -n 4
#BSUB -W 00:30
#BSUB -R "select[model==XeonGold6226R]"
#BSUB -R "rusage[mem=16GB]"
#BSUB -o pardy5.out
#BSUB -e pardy5.err 
#BSUB -N
#BSUB -R "span[hosts=1]"
#BSUB -J par_dy5

time python simulate_parallelized_dynamic.py 100 5 5