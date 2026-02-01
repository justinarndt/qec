#!/usr/bin/env python3
"""
Benchmark Standard: Standard (non-stress) decoder comparison.

Compares PyMatching (MWPM), Union-Find (LCD proxy), and BP+OSD (ASR-MP)
under uniform circuit-level depolarizing noise.

Usage:
    python benchmark_standard.py --distance 5 --error-rate 0.003 --shots 10000
"""

import argparse
import os
import sys

# Add src to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import sinter

from asr_mp.decoder import TesseractBPOSD
from asr_mp.noise_models import generate_standard_tasks
from asr_mp.union_find_decoder import UnionFindSinterDecoder


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run standard QEC decoder benchmarks",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-d",
        "--distances",
        nargs="+",
        type=int,
        default=[3, 5, 7],
        help="Code distances to benchmark",
    )
    parser.add_argument(
        "-p",
        "--error-rates",
        nargs="+",
        type=float,
        default=[0.001, 0.003, 0.005],
        help="Physical error rates",
    )
    parser.add_argument(
        "-s",
        "--shots",
        type=int,
        default=10000,
        help="Maximum shots per task",
    )
    parser.add_argument(
        "-e",
        "--max-errors",
        type=int,
        default=100,
        help="Maximum errors before stopping",
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="standard_benchmark.csv",
        help="Output CSV file path",
    )
    parser.add_argument(
        "--decoders",
        nargs="+",
        type=str,
        default=["pymatching", "union_find", "tesseract"],
        choices=["pymatching", "union_find", "tesseract"],
        help="Decoders to benchmark",
    )
    return parser.parse_args()


def main() -> None:
    """Run the standard benchmark."""
    args = parse_args()

    print("=" * 60)
    print("ASR-MP Standard Benchmark")
    print("=" * 60)
    print(f"Distances: {args.distances}")
    print(f"Error rates: {args.error_rates}")
    print(f"Max shots: {args.shots}")
    print(f"Max errors: {args.max_errors}")
    print(f"Workers: {args.workers}")
    print(f"Decoders: {args.decoders}")
    print(f"Output: {args.output}")
    print("=" * 60)

    # Remove existing output file for fresh start
    if os.path.exists(args.output):
        os.remove(args.output)
        print(f"Removed existing {args.output}")

    # Generate tasks
    print("\nGenerating tasks...")
    tasks = generate_standard_tasks(
        distances=args.distances,
        error_rates=args.error_rates,
    )
    print(f"Created {len(tasks)} tasks")

    # Build custom decoders dict
    custom_decoders = {}
    if "tesseract" in args.decoders:
        custom_decoders["tesseract"] = TesseractBPOSD()
    if "union_find" in args.decoders:
        custom_decoders["union_find"] = UnionFindSinterDecoder()

    # Run collection
    print("\nStarting benchmark...")
    samples = sinter.collect(
        num_workers=args.workers,
        max_shots=args.shots,
        max_errors=args.max_errors,
        tasks=tasks,
        decoders=args.decoders,
        custom_decoders=custom_decoders,
        print_progress=True,
        save_resume_filepath=args.output,
    )

    # Print summary
    print("\n" + "=" * 60)
    print("Results Summary")
    print("=" * 60)
    print(f"{'Decoder':<15} {'d':<5} {'p':<10} {'Shots':<10} {'Errors':<10} {'P_L':<15}")
    print("-" * 60)

    for s in sorted(samples, key=lambda x: (x.decoder, x.json_metadata["d"], x.json_metadata["p"])):
        d = s.json_metadata["d"]
        p = s.json_metadata["p"]
        p_l = s.errors / s.shots if s.shots > 0 else 0
        print(f"{s.decoder:<15} {d:<5} {p:<10.4f} {s.shots:<10} {s.errors:<10} {p_l:<15.6e}")

    print("=" * 60)
    print(f"Results saved to: {args.output}")


if __name__ == "__main__":
    main()
