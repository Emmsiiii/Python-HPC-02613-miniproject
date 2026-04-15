#!/bin/bash
#BSUB -J task7
#BSUB -q hpc
#BSUB -n 1
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=8GB]"
#BSUB -W 00:30
#BSUB -o task7_%J.out
#BSUB -e task7_%J.err

# Initilize conda environment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

python task7.py 20

# the command line argument is how many building floorplans to process.