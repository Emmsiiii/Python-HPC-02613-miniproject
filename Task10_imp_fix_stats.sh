#!/bin/bash
#BSUB -J Task10_imp_stats
#BSUB -q c02613
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=8GB]"
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -W 00:30
#BSUB -o Task10_imp_stats_%J.out
#BSUB -e Task10_imp_stats_%J.err

# Initilize conda environment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

nsys stats task10_prof.nsys-rep