#!/usr/bin/env python3
"""
Generate Publication Plots: Create all figures for the Riverlane report.

Reads benchmark CSV files and generates publication-quality plots.

Usage:
    python generate_plots.py --input stress_benchmark.csv --output ../assets/
"""

import argparse
import os
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np

# Try to import sinter for reading CSV
try:
    import sinter
    SINTER_AVAILABLE = True
except ImportError:
    SINTER_AVAILABLE = False


# Plot styling
plt.style.use('seaborn-v0_8-whitegrid')
COLORS = {
    "pymatching": "#666666",
    "union_find": "#1f77b4",
    "tesseract": "#ff7f0e",
}
MARKERS = {
    "pymatching": "o",
    "union_find": "s",
    "tesseract": "^",
}
LABELS = {
    "pymatching": "MWPM (Baseline)",
    "union_find": "Union-Find (LCD Proxy)",
    "tesseract": "BP+OSD (ASR-MP)",
}


def load_samples(csv_path: str) -> List:
    """Load sinter samples from CSV file."""
    if not SINTER_AVAILABLE:
        raise ImportError("sinter is required to load benchmark results")
    return list(sinter.read_stats_from_csv_files(csv_path))


def plot_pl_vs_distance(
    samples: List,
    output_path: str,
    title: str = "Logical Error Rate vs Code Distance",
    fixed_p: Optional[float] = None,
    stress_filter: Optional[str] = None,
) -> None:
    """
    Plot P_L vs code distance for each decoder.

    Args:
        samples: List of sinter sample results
        output_path: Path to save the plot
        title: Plot title
        fixed_p: Filter to specific error rate
        stress_filter: Filter to specific stress condition
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    data: Dict[str, Dict[str, List]] = {}

    for s in samples:
        decoder = s.decoder
        d = s.json_metadata.get("d")
        p = s.json_metadata.get("p")
        stress = s.json_metadata.get("stress", "Standard")

        # Apply filters
        if fixed_p is not None and abs(p - fixed_p) > 1e-6:
            continue
        if stress_filter is not None and stress_filter not in stress:
            continue

        p_l = s.errors / s.shots if s.shots > 0 else 1e-6

        if decoder not in data:
            data[decoder] = {"d": [], "p_l": []}
        data[decoder]["d"].append(d)
        data[decoder]["p_l"].append(p_l)

    for decoder in sorted(data.keys()):
        vals = data[decoder]
        sorted_pairs = sorted(zip(vals["d"], vals["p_l"]))
        ds = [p[0] for p in sorted_pairs]
        pls = [p[1] for p in sorted_pairs]

        ax.plot(
            ds, pls,
            marker=MARKERS.get(decoder, "o"),
            color=COLORS.get(decoder, "black"),
            label=LABELS.get(decoder, decoder),
            linewidth=2,
            markersize=10,
        )

    ax.set_xlabel("Code Distance (d)", fontsize=12)
    ax.set_ylabel("Logical Error Rate ($P_L$)", fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.set_yscale("log")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def plot_drift_resilience(
    samples: List,
    output_path: str,
    fixed_d: int = 5,
) -> None:
    """
    Plot P_L vs drift amplitude.

    Args:
        samples: List of sinter sample results
        output_path: Path to save the plot
        fixed_d: Code distance to analyze
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    data: Dict[str, Dict[str, List]] = {}

    for s in samples:
        decoder = s.decoder
        d = s.json_metadata.get("d")
        drift = s.json_metadata.get("drift_strength", 0)

        if d != fixed_d:
            continue

        p_l = s.errors / s.shots if s.shots > 0 else 1e-6

        if decoder not in data:
            data[decoder] = {"drift": [], "p_l": []}
        data[decoder]["drift"].append(drift * 100)  # Convert to %
        data[decoder]["p_l"].append(p_l)

    for decoder in sorted(data.keys()):
        vals = data[decoder]
        sorted_pairs = sorted(zip(vals["drift"], vals["p_l"]))
        drifts = [p[0] for p in sorted_pairs]
        pls = [p[1] for p in sorted_pairs]

        ax.plot(
            drifts, pls,
            marker=MARKERS.get(decoder, "o"),
            color=COLORS.get(decoder, "black"),
            label=LABELS.get(decoder, decoder),
            linewidth=2,
            markersize=10,
        )

    ax.set_xlabel("Drift Amplitude (%)", fontsize=12)
    ax.set_ylabel("Logical Error Rate ($P_L$)", fontsize=12)
    ax.set_title(f"Drift Resilience (d={fixed_d})", fontsize=14)
    ax.set_yscale("log")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def plot_latency_comparison(
    latency_data: Dict[str, Dict[str, float]],
    output_path: str,
    fpga_target: float = 1.0,
) -> None:
    """
    Plot latency comparison bar chart.

    Args:
        latency_data: Dict of {decoder: {"mean": μs, "std": μs}}
        output_path: Path to save the plot
        fpga_target: FPGA target latency in μs
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    decoders = list(latency_data.keys())
    means = [latency_data[d]["mean"] for d in decoders]
    stds = [latency_data[d].get("std", 0) for d in decoders]
    colors = [COLORS.get(d.lower().replace(" ", "_").replace("+", ""), "#666666") for d in decoders]

    bars = ax.bar(decoders, means, yerr=stds, capsize=5, color=colors, alpha=0.8)

    ax.axhline(y=fpga_target, color="red", linestyle="--", linewidth=2,
               label=f"FPGA Target ({fpga_target} μs)")

    ax.set_ylabel("Latency (μs)", fontsize=12)
    ax.set_title("Decoder Latency Comparison", fontsize=14)
    ax.legend(fontsize=10)
    ax.set_yscale("log")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def plot_improvement_factor(
    samples: List,
    output_path: str,
    baseline_decoder: str = "pymatching",
) -> None:
    """
    Plot improvement factor vs MWPM baseline.

    Args:
        samples: List of sinter sample results
        output_path: Path to save the plot
        baseline_decoder: Decoder to use as baseline
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    # Group by (d, stress condition)
    groups: Dict[tuple, Dict[str, float]] = {}
    for s in samples:
        key = (s.json_metadata.get("d"), s.json_metadata.get("stress", "Standard"))
        p_l = s.errors / s.shots if s.shots > 0 else 1
        if key not in groups:
            groups[key] = {}
        groups[key][s.decoder] = p_l

    # Calculate improvements
    improvements: Dict[str, List[tuple]] = {}
    for key, decoders in groups.items():
        baseline = decoders.get(baseline_decoder, 1)
        for decoder, p_l in decoders.items():
            if decoder == baseline_decoder:
                continue
            improvement = baseline / p_l if p_l > 0 else 1
            if decoder not in improvements:
                improvements[decoder] = []
            improvements[decoder].append((key[0], improvement))

    for decoder, data in sorted(improvements.items()):
        sorted_data = sorted(data)
        ds = [d[0] for d in sorted_data]
        imps = [d[1] for d in sorted_data]

        ax.plot(
            ds, imps,
            marker=MARKERS.get(decoder, "o"),
            color=COLORS.get(decoder, "black"),
            label=f"{LABELS.get(decoder, decoder)} vs MWPM",
            linewidth=2,
            markersize=10,
        )

    ax.axhline(y=1.0, color="gray", linestyle="--", alpha=0.5)
    ax.set_xlabel("Code Distance (d)", fontsize=12)
    ax.set_ylabel("Improvement Factor", fontsize=12)
    ax.set_title("Decoder Improvement vs MWPM Baseline", fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate publication plots")
    parser.add_argument("-i", "--input", type=str, required=True,
                        help="Input CSV file from sinter benchmark")
    parser.add_argument("-o", "--output", type=str, default="../assets",
                        help="Output directory for plots")
    parser.add_argument("--all", action="store_true",
                        help="Generate all plot types")
    return parser.parse_args()


def main():
    args = parse_args()

    # Ensure output directory exists
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load samples
    print(f"Loading samples from {args.input}...")
    samples = load_samples(args.input)
    print(f"Loaded {len(samples)} samples")

    # Generate plots
    print("\nGenerating plots...")

    plot_pl_vs_distance(
        samples,
        str(output_dir / "pl_vs_distance.png"),
        title="Logical Error Rate vs Code Distance",
    )

    plot_drift_resilience(
        samples,
        str(output_dir / "drift_resilience.png"),
    )

    plot_improvement_factor(
        samples,
        str(output_dir / "improvement_factor.png"),
    )

    print("\nAll plots generated!")


if __name__ == "__main__":
    main()
