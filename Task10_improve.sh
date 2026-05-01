#!/bin/bash
#BSUB -J Task10_imp
#BSUB -q c02613
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=8GB]"
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -W 00:30
#BSUB -o Task10_imp_%J.out
#BSUB -e Task10_imp_%J.err

# Initilize conda environment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

nsys profile -o task10_prof python Task10.py 1