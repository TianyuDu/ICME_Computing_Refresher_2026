"""Run one pi estimate using the seed assigned to this Slurm array task."""

import argparse
import math
import os
from pathlib import Path

from estimate_pi import estimate_pi, positive_int


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=positive_int, default=1_000_000)
    args = parser.parse_args()

    task_text = os.environ.get("SLURM_ARRAY_TASK_ID")
    if task_text is None:
        parser.error("SLURM_ARRAY_TASK_ID is not set; run this with a Slurm job array")
    try:
        task = int(task_text)
    except ValueError:
        parser.error("SLURM_ARRAY_TASK_ID must be an integer")

    seeds = Path(__file__).with_name("seeds.txt").read_text().splitlines()
    if not 0 <= task < len(seeds):
        parser.error(f"task index {task} is out of range for {len(seeds)} seeds")
    try:
        seed = int(seeds[task])
    except ValueError:
        parser.error(f"seed on line {task + 1} of seeds.txt must be an integer")

    pi = estimate_pi(args.samples, seed)
    error = abs(pi - math.pi)
    print(
        f"task={task} seed={seed} samples={args.samples} "
        f"pi={pi:.6f} abs_error={error:.6f}",
        flush=True,
    )


if __name__ == "__main__":
    main()
