#!/bin/bash
#BSUB -J Task9
#BSUB -q c02613
#BSUB -n 1
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=8GB]"
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -W 00:30
#BSUB -o Task9_%J.out
#BSUB -e Task9_%J.err

# Initilize conda environment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

time python Task9.py 10
time python Task9.py 20