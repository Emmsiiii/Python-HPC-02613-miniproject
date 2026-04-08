#!/bin/bash
#BSUB -J timing
#BSUB -q hpc
#BSUB -n 1
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=8GB]"
#BSUB -W 00:30
#BSUB -o output_%J.out
#BSUB -e error_%J.err

# Initilize conda environment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

time python simulate.py 20