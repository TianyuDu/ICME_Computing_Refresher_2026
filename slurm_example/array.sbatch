#!/bin/bash
#SBATCH --job-name=pi-array
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:02:00
#SBATCH --array=0-5
#SBATCH --output=logs/array-%A_%a.out
#SBATCH --error=logs/array-%A_%a.err

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
srun python3 -u array_pi.py --samples 1000000
