#!/usr/bin/env python3
"""
Benchmark Stress: Drift and burst resilience testing.

Compares PyMatching (MWPM), Union-Find (LCD proxy), and BP+OSD (ASR-MP)
under hostile conditions: sinusoidal drift, correlated bursts, and leakage.

Usage:
    python benchmark_stress.py --distance 5 --drift 0.3 --burst 0.05 --shots 10000
"""

import argparse
import os
import sys

# Add src to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import sinter

from asr_mp.decoder import TesseractBPOSD
from asr_mp.noise_models import generate_sweep_tasks, generate_undeniable_tasks
from asr_mp.union_find_decoder import UnionFindSinterDecoder


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run stress-test QEC decoder benchmarks",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-d",
        "--distances",
        nargs="+",
        type=int,
        default=[5, 7, 9],
        help="Code distances to benchmark",
    )
    parser.add_argument(
        "-p",
        "--error-rate",
        type=float,
        default=0.003,
        help="Base physical error rate",
    )
    parser.add_argument(
        "--drift",
        type=float,
        default=0.3,
        help="Drift strength (0.3 = ±30%%)",
    )
    parser.add_argument(
        "--burst",
        type=float,
        default=0.05,
        help="Burst probability",
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
        default="stress_benchmark.csv",
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
    parser.add_argument(
        "--mode",
        type=str,
        default="undeniable",
        choices=["undeniable", "sweep"],
        help="Benchmark mode: 'undeniable' (fixed drift/burst across d) or 'sweep' (vary drift)",
    )
    return parser.parse_args()


def main() -> None:
    """Run the stress benchmark."""
    args = parse_args()

    print("=" * 60)
    print("ASR-MP Stress-Test Benchmark")
    print("=" * 60)
    print(f"Mode: {args.mode}")
    print(f"Distances: {args.distances}")
    print(f"Base error rate: {args.error_rate}")
    print(f"Drift strength: {args.drift} (±{args.drift*100:.0f}%)")
    print(f"Burst probability: {args.burst}")
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

    # Generate tasks based on mode
    print("\nGenerating tasks...")
    if args.mode == "undeniable":
        tasks = generate_undeniable_tasks(
            distances=args.distances,
            base_p=args.error_rate,
            drift_strength=args.drift,
            burst_prob=args.burst,
        )
    else:  # sweep mode
        tasks = []
        for d in args.distances:
            tasks.extend(generate_sweep_tasks(d, base_p=args.error_rate))

    print(f"Created {len(tasks)} tasks")

    # Build custom decoders dict
    custom_decoders = {}
    if "tesseract" in args.decoders:
        custom_decoders["tesseract"] = TesseractBPOSD()
    if "union_find" in args.decoders:
        custom_decoders["union_find"] = UnionFindSinterDecoder()

    # Run collection
    print("\nStarting stress-test benchmark...")
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
    print("\n" + "=" * 70)
    print("Stress-Test Results Summary")
    print("=" * 70)
    print(f"{'Decoder':<15} {'d':<5} {'Stress':<20} {'Shots':<10} {'Errors':<10} {'P_L':<15}")
    print("-" * 70)

    for s in sorted(samples, key=lambda x: (x.decoder, x.json_metadata["d"])):
        d = s.json_metadata["d"]
        stress = s.json_metadata.get("stress", "Unknown")
        p_l = s.errors / s.shots if s.shots > 0 else 0
        print(f"{s.decoder:<15} {d:<5} {stress:<20} {s.shots:<10} {s.errors:<10} {p_l:<15.6e}")

    print("=" * 70)
    print(f"Results saved to: {args.output}")

    # Print decoder comparison summary
    print("\n" + "=" * 70)
    print("Decoder Comparison (by distance)")
    print("=" * 70)

    # Group by distance
    by_distance = {}
    for s in samples:
        d = s.json_metadata["d"]
        if d not in by_distance:
            by_distance[d] = {}
        by_distance[d][s.decoder] = s.errors / s.shots if s.shots > 0 else 0

    for d in sorted(by_distance.keys()):
        print(f"\nDistance d={d}:")
        decoders_at_d = by_distance[d]
        baseline = decoders_at_d.get("pymatching", 1.0)
        for decoder, p_l in sorted(decoders_at_d.items()):
            improvement = baseline / p_l if p_l > 0 else float("inf")
            print(f"  {decoder:<15}: P_L = {p_l:.6e} ({improvement:.2f}x vs MWPM)")


if __name__ == "__main__":
    main()
