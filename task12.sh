#!/bin/sh
#BSUB -q c02613
#BSUB -J task8_cuda[1-5]
#BSUB -n 4
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=8GB]"
#BSUB -W 00:15
#BSUB -o batch_output/TASK8_%J_%I.out
#BSUB -e batch_output/TASK8_%J_%I.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

CHUNK=1000

START=$(( ($LSB_JOBINDEX - 1) * CHUNK ))
END=$(( $LSB_JOBINDEX * CHUNK ))

if [ $END -gt 4571 ]; then
    END=4571
fi

python -u task8.py $START $END 20000 > results_${START}_${END}.csv