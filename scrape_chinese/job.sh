#!/bin/bash

#SBATCH --partition=main
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=3:00:00

module purge
module load gcc/11.3.0
module load python/3.9.12

python parse.py