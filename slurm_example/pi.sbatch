#!/bin/bash
#SBATCH --job-name=estimate-pi
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:02:00
#SBATCH --output=logs/pi-%j.out
#SBATCH --error=logs/pi-%j.err

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
hostname
srun python3 -u estimate_pi.py --samples 1000000 --seed 42
