#!/bin/bash
#BSUB -J Task4_profiler
#BSUB -q hpc
#BSUB -W 5
#BSUB -n 1
#BSUB -R "rusage[mem=512MB]"
#BSUB -W 00:30
#BSUB -o Task4_profiler_%J.out
#BSUB -e Task4_profiler_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

python -m line_profiler Task4.py.lprof