"""Estimate pi by sampling random points in a unit square."""

import argparse
import math
import random


def positive_int(value):
    """Require a positive integer for the number of random samples."""
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("must be a positive integer") from None
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def estimate_pi(samples, seed):
    """Use the fraction inside a quarter circle to estimate pi."""
    if samples <= 0:
        raise ValueError("samples must be positive")

    rng = random.Random(seed)
    inside = 0
    for _ in range(samples):
        x = rng.random()
        y = rng.random()
        if x * x + y * y <= 1:
            inside += 1

    # The quarter circle has area pi / 4; the square has area 1.
    return 4 * inside / samples


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=positive_int, default=1_000_000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    pi = estimate_pi(args.samples, args.seed)
    error = abs(pi - math.pi)
    print(
        f"seed={args.seed} samples={args.samples} "
        f"pi={pi:.6f} abs_error={error:.6f}",
        flush=True,
    )


if __name__ == "__main__":
    main()
