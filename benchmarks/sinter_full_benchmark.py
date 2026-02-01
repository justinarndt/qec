#!/usr/bin/env python3
"""
Sinter Full Benchmark: Production-grade statistical benchmarking.

Extended benchmark configuration for CEO-ready results:
- Distances: d=5, 7, 9, 11, 13
- Rounds: 100-200 per task
- Shots: 1,000,000 or max_errors=1000
- All three decoders: PyMatching, Union-Find, BP+OSD

This script generates statistically significant results for the Riverlane report.

Usage:
    python sinter_full_benchmark.py --full        # Full production run
    python sinter_full_benchmark.py --quick       # Quick validation run
"""

import argparse
import os
import sys
import time
from typing import List

# Add src to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import sinter
import stim

from asr_mp.decoder import TesseractBPOSD
from asr_mp.noise_models import generate_stress_circuit
from asr_mp.union_find_decoder import UnionFindSinterDecoder


def generate_full_tasks(
    distances: List[int],
    error_rates: List[float],
    rounds_per_d: int = 100,
    drift_strength: float = 0.3,
    burst_prob: float = 0.05,
) -> List[sinter.Task]:
    """
    Generate comprehensive task list for full benchmark.

    Args:
        distances: List of code distances
        error_rates: List of physical error rates
        rounds_per_d: Multiplier for rounds (rounds = d * rounds_per_d / d = rounds_per_d)
        drift_strength: Drift amplitude
        burst_prob: Burst probability

    Returns:
        List of sinter tasks
    """
    tasks = []

    for d in distances:
        # Use 100-200 rounds as specified
        rounds = max(100, min(200, d * 20))

        for p in error_rates:
            # Standard noise task
            circuit_std = stim.Circuit.generated(
                "surface_code:rotated_memory_z",
                distance=d,
                rounds=rounds,
                after_clifford_depolarization=p,
                before_round_data_depolarization=p,
                before_measure_flip_probability=p,
                after_reset_flip_probability=p,
            )
            tasks.append(
                sinter.Task(
                    circuit=circuit_std,
                    json_metadata={
                        "d": d,
                        "p": p,
                        "rounds": rounds,
                        "stress": "Standard",
                    },
                    detector_error_model=circuit_std.detector_error_model(decompose_errors=True),
                )
            )

            # Stress-test task (drift + burst)
            circuit_stress = generate_stress_circuit(
                d=d,
                base_p=p,
                drift_strength=drift_strength,
                burst_prob=burst_prob,
                rounds=rounds,
            )
            tasks.append(
                sinter.Task(
                    circuit=circuit_stress,
                    json_metadata={
                        "d": d,
                        "p": p,
                        "rounds": rounds,
                        "stress": f"Drift={drift_strength}+Burst={burst_prob}",
                        "drift_strength": drift_strength,
                        "burst_prob": burst_prob,
                    },
                    detector_error_model=circuit_stress.detector_error_model(decompose_errors=True),
                )
            )

    return tasks


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run full production benchmark for Riverlane report",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full production benchmark (1M shots, d=5-13)",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick validation (1K shots, d=5-9)",
    )
    parser.add_argument(
        "-d", "--distances",
        nargs="+",
        type=int,
        default=None,
        help="Override distances (default: based on --full/--quick)",
    )
    parser.add_argument(
        "-p", "--error-rates",
        nargs="+",
        type=float,
        default=[0.001, 0.002, 0.003, 0.004, 0.005, 0.006],
        help="Physical error rates",
    )
    parser.add_argument(
        "-s", "--shots",
        type=int,
        default=None,
        help="Override max shots",
    )
    parser.add_argument(
        "-e", "--max-errors",
        type=int,
        default=1000,
        help="Maximum errors before stopping",
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=8,
        help="Number of parallel workers",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="full_benchmark.csv",
        help="Output CSV file path",
    )
    parser.add_argument(
        "--drift",
        type=float,
        default=0.3,
        help="Drift strength for stress tests",
    )
    parser.add_argument(
        "--burst",
        type=float,
        default=0.05,
        help="Burst probability for stress tests",
    )
    return parser.parse_args()


def main() -> None:
    """Run the full benchmark."""
    args = parse_args()

    # Set defaults based on mode
    if args.full:
        distances = args.distances or [5, 7, 9, 11, 13]
        max_shots = args.shots or 1_000_000
    elif args.quick:
        distances = args.distances or [5, 7, 9]
        max_shots = args.shots or 1_000
    else:
        distances = args.distances or [5, 7, 9]
        max_shots = args.shots or 10_000

    print("=" * 70)
    print("ASR-MP Full Production Benchmark")
    print("=" * 70)
    print(f"Mode: {'FULL (CEO-ready)' if args.full else 'QUICK (validation)' if args.quick else 'STANDARD'}")
    print(f"Distances: {distances}")
    print(f"Error rates: {args.error_rates}")
    print(f"Max shots: {max_shots:,}")
    print(f"Max errors: {args.max_errors}")
    print(f"Workers: {args.workers}")
    print(f"Drift strength: {args.drift}")
    print(f"Burst probability: {args.burst}")
    print(f"Output: {args.output}")
    print("=" * 70)

    # Generate tasks
    print("\nGenerating tasks...")
    tasks = generate_full_tasks(
        distances=distances,
        error_rates=args.error_rates,
        drift_strength=args.drift,
        burst_prob=args.burst,
    )
    print(f"Created {len(tasks)} tasks")
    print(f"  - {len(tasks)//2} standard noise tasks")
    print(f"  - {len(tasks)//2} stress-test tasks")

    # Build custom decoders
    custom_decoders = {
        "tesseract": TesseractBPOSD(),
        "union_find": UnionFindSinterDecoder(),
    }
    decoders = ["pymatching", "union_find", "tesseract"]

    # Estimated runtime
    est_tasks = len(tasks) * len(decoders)
    print(f"\nTotal decoder-task combinations: {est_tasks}")
    print("Starting benchmark...\n")

    start_time = time.time()

    # Run collection
    samples = sinter.collect(
        num_workers=args.workers,
        max_shots=max_shots,
        max_errors=args.max_errors,
        tasks=tasks,
        decoders=decoders,
        custom_decoders=custom_decoders,
        print_progress=True,
        save_resume_filepath=args.output,
    )

    elapsed = time.time() - start_time

    # Print comprehensive summary
    print("\n" + "=" * 80)
    print("FULL BENCHMARK RESULTS")
    print("=" * 80)
    print(f"Total time: {elapsed/60:.1f} minutes")
    print(f"Results saved to: {args.output}")

    # Summary table
    print("\n" + "-" * 80)
    print(f"{'Decoder':<12} {'d':<4} {'p':<8} {'Stress':<25} {'Shots':<12} {'Errors':<8} {'P_L':<12}")
    print("-" * 80)

    for s in sorted(samples, key=lambda x: (x.json_metadata["stress"], x.json_metadata["d"], x.json_metadata["p"], x.decoder)):
        d = s.json_metadata["d"]
        p = s.json_metadata["p"]
        stress = s.json_metadata.get("stress", "Unknown")[:24]
        p_l = s.errors / s.shots if s.shots > 0 else 0
        print(f"{s.decoder:<12} {d:<4} {p:<8.4f} {stress:<25} {s.shots:<12,} {s.errors:<8} {p_l:<12.4e}")

    # Decoder comparison by condition
    print("\n" + "=" * 80)
    print("DECODER COMPARISON SUMMARY")
    print("=" * 80)

    conditions = set((s.json_metadata["d"], s.json_metadata["stress"]) for s in samples)
    for d, stress in sorted(conditions):
        print(f"\nd={d}, {stress}:")
        relevant = [s for s in samples if s.json_metadata["d"] == d and s.json_metadata["stress"] == stress]

        baseline = None
        for s in relevant:
            if s.decoder == "pymatching":
                baseline = s.errors / s.shots if s.shots > 0 else 1.0
                break

        for s in sorted(relevant, key=lambda x: x.decoder):
            p_l = s.errors / s.shots if s.shots > 0 else 0
            if baseline and p_l > 0:
                improvement = baseline / p_l
                print(f"  {s.decoder:<15}: P_L = {p_l:.4e} ({improvement:.2f}x vs MWPM)")
            else:
                print(f"  {s.decoder:<15}: P_L = {p_l:.4e}")

    print("\n" + "=" * 80)
    print("Benchmark complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
