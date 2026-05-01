#!/bin/bash
#BSUB -J Task4
#BSUB -q hpc
#BSUB -W 5
#BSUB -n 1
#BSUB -R "select[model==XeonGold6142] rusage[mem=512MB]"
#BSUB -W 00:30
#BSUB -o Task4_%J.out
#BSUB -e Task4_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

kernprof -l Task4.py