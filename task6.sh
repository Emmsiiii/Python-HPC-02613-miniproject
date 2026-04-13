#!/bin/bash
#BSUB -q hpc
#BSUB -n 4
#BSUB -W 00:30
#BSUB -R "select[model==XeonGold6226R]"
#BSUB -R "rusage[mem=16GB]"
#BSUB -J dynamic5
#BSUB -o dynamic5.out
#BSUB -e dynamic5.err 
#BSUB -N
#BSUB -R "span[hosts=1]"


# Initilize conda environment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

time python task6.py 100 4

# Change the 3 command line argument to different number of workers, same as in question 5 to compare the time (For example 1,2,4,8,16) or maybe do a for loop.
# Do we also need to change the number of nodes (#BSUB -n 4) to match the number of workers?