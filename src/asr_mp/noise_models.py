"""
Noise Models: Stress-Test Circuit Generators

Provides noise model generators for benchmarking QEC decoders under
realistic, hostile conditions including drift, burst errors, and leakage.
"""

from typing import List, Optional

import numpy as np
import sinter
import stim


def generate_stress_circuit(
    d: int,
    base_p: float,
    drift_strength: float = 0.2,
    burst_prob: float = 0.0,
    rounds: Optional[int] = None,
) -> stim.Circuit:
    """
    Generate a rotated surface code circuit with stress-test noise.

    This function creates a circuit with time-varying noise to simulate
    realistic hardware conditions:
    - Sinusoidal drift in error rates (mimics T1 fluctuations)
    - Correlated burst errors (mimics cosmic ray events)

    Args:
        d: Code distance
        base_p: Base physical error rate
        drift_strength: Amplitude of sinusoidal drift (0.3 = ±30%)
        burst_prob: Probability of correlated burst injection
        rounds: Number of syndrome rounds (default: 3*d)

    Returns:
        Stim circuit with injected noise

    Example:
        >>> circuit = generate_stress_circuit(d=5, base_p=0.003, drift_strength=0.3)
        >>> dem = circuit.detector_error_model(decompose_errors=True)
    """
    if rounds is None:
        rounds = d * 3

    # Generate base circuit without noise
    circuit_raw = stim.Circuit.generated(
        "surface_code:rotated_memory_z",
        distance=d,
        rounds=rounds,
        after_clifford_depolarization=0,
        before_round_data_depolarization=0,
        before_measure_flip_probability=0,
        after_reset_flip_probability=0,
    )

    # Flatten to remove RepeatBlocks for surgery
    circuit = circuit_raw.flattened()

    # Circuit surgery: inject time-varying noise
    new_circuit = stim.Circuit()
    period = rounds / 2.0
    current_round = 0

    for instruction in circuit:
        if instruction.name == "TICK":
            current_round += 1
            new_circuit.append("TICK")
            continue

        # Calculate drift factor: sinusoidal variation
        drift_factor = 1.0 + drift_strength * np.sin(2 * np.pi * current_round / period)
        p_now = base_p * drift_factor
        targets = instruction.targets_copy()

        # Inject noise based on gate type
        if instruction.name in ["R", "M", "MR"]:
            new_circuit.append(instruction.name, targets)
            new_circuit.append("X_ERROR", targets, p_now)
        elif instruction.name in ["CX", "CZ", "H", "S", "X", "Z", "Y"]:
            new_circuit.append(instruction.name, targets)
            if instruction.name in ["CX", "CZ"]:
                new_circuit.append("DEPOLARIZE2", targets, p_now)
            else:
                new_circuit.append("DEPOLARIZE1", targets, p_now)
        else:
            new_circuit.append(instruction)

    # Burst injection: correlated errors on adjacent qubits
    if burst_prob > 0:
        middle_qubits = list(range(d * d // 2, d * d // 2 + d))
        targets = [stim.target_z(q) for q in middle_qubits]
        burst_circuit = stim.Circuit()
        burst_circuit.append("CORRELATED_ERROR", targets, burst_prob)
        new_circuit = burst_circuit + new_circuit

    return new_circuit


def generate_standard_circuit(
    d: int,
    p: float,
    rounds: Optional[int] = None,
) -> stim.Circuit:
    """
    Generate a standard rotated surface code circuit with uniform noise.

    Args:
        d: Code distance
        p: Physical error rate (uniform depolarizing)
        rounds: Number of syndrome rounds (default: 3*d)

    Returns:
        Stim circuit with standard circuit-level noise
    """
    if rounds is None:
        rounds = d * 3

    return stim.Circuit.generated(
        "surface_code:rotated_memory_z",
        distance=d,
        rounds=rounds,
        after_clifford_depolarization=p,
        before_round_data_depolarization=p,
        before_measure_flip_probability=p,
        after_reset_flip_probability=p,
    )


def generate_undeniable_tasks(
    distances: Optional[List[int]] = None,
    base_p: float = 0.003,
    drift_strength: float = 0.3,
    burst_prob: float = 0.05,
) -> List[sinter.Task]:
    """
    Generate sinter tasks for the "undeniable" stress-test benchmark.

    Creates tasks across multiple code distances with drift and burst noise
    to demonstrate decoder resilience under hostile conditions.

    Args:
        distances: List of code distances (default: [5, 7, 9])
        base_p: Base physical error rate
        drift_strength: Drift amplitude (0.3 = ±30%)
        burst_prob: Burst injection probability

    Returns:
        List of sinter.Task objects ready for collection

    Example:
        >>> tasks = generate_undeniable_tasks(distances=[5, 7, 9, 11, 13])
        >>> samples = sinter.collect(tasks=tasks, ...)
    """
    if distances is None:
        distances = [5, 7, 9]

    tasks = []
    for d in distances:
        circuit = generate_stress_circuit(
            d,
            base_p=base_p,
            drift_strength=drift_strength,
            burst_prob=burst_prob,
        )
        tasks.append(
            sinter.Task(
                circuit=circuit,
                json_metadata={
                    "d": d,
                    "p": base_p,
                    "stress": "Drift+Burst",
                    "drift_strength": drift_strength,
                    "burst_prob": burst_prob,
                },
                detector_error_model=circuit.detector_error_model(decompose_errors=True),
            )
        )
    return tasks


def generate_standard_tasks(
    distances: Optional[List[int]] = None,
    error_rates: Optional[List[float]] = None,
) -> List[sinter.Task]:
    """
    Generate sinter tasks for standard (non-stress) benchmarking.

    Args:
        distances: List of code distances (default: [3, 5, 7])
        error_rates: List of physical error rates (default: [0.001, 0.003, 0.005])

    Returns:
        List of sinter.Task objects
    """
    if distances is None:
        distances = [3, 5, 7]
    if error_rates is None:
        error_rates = [0.001, 0.003, 0.005]

    tasks = []
    for d in distances:
        for p in error_rates:
            circuit = generate_standard_circuit(d, p)
            tasks.append(
                sinter.Task(
                    circuit=circuit,
                    json_metadata={"d": d, "p": p, "stress": "None"},
                    detector_error_model=circuit.detector_error_model(decompose_errors=True),
                )
            )
    return tasks


def generate_sweep_tasks(
    d: int,
    drift_strengths: Optional[List[float]] = None,
    base_p: float = 0.003,
) -> List[sinter.Task]:
    """
    Generate tasks for drift amplitude sweep analysis.

    Useful for plotting P_L vs drift amplitude to demonstrate resilience.

    Args:
        d: Code distance
        drift_strengths: List of drift amplitudes (default: [0, 0.1, 0.2, 0.3, 0.4])
        base_p: Base physical error rate

    Returns:
        List of sinter.Task objects
    """
    if drift_strengths is None:
        drift_strengths = [0.0, 0.1, 0.2, 0.3, 0.4]

    tasks = []
    for drift in drift_strengths:
        circuit = generate_stress_circuit(d, base_p=base_p, drift_strength=drift)
        tasks.append(
            sinter.Task(
                circuit=circuit,
                json_metadata={
                    "d": d,
                    "p": base_p,
                    "stress": f"Drift={drift}",
                    "drift_strength": drift,
                },
                detector_error_model=circuit.detector_error_model(decompose_errors=True),
            )
        )
    return tasks
