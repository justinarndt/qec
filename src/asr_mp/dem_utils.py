"""
DEM Utilities: Detector Error Model to Matrix Conversion

Provides utilities for converting Stim's DetectorErrorModel into sparse
matrices suitable for belief propagation decoding.
"""

from typing import Tuple

import numpy as np
import scipy.sparse
import stim


def dem_to_matrices(
    dem: stim.DetectorErrorModel,
) -> Tuple[scipy.sparse.csc_matrix, scipy.sparse.csc_matrix, np.ndarray]:
    """
    Convert a DetectorErrorModel to parity check and logical matrices.

    This function parses a Stim DEM and extracts:
    - H: The parity check matrix (detectors × errors)
    - L: The logical observable matrix (observables × errors)
    - priors: The prior error probabilities for each error mechanism

    Args:
        dem: A Stim DetectorErrorModel, typically obtained from
             circuit.detector_error_model(decompose_errors=True)

    Returns:
        H: Sparse parity check matrix (num_detectors × num_errors)
        L: Sparse logical matrix (num_observables × num_errors)
        priors: Array of prior probabilities for each error

    Example:
        >>> circuit = stim.Circuit.generated("surface_code:rotated_memory_z", distance=3, rounds=3)
        >>> dem = circuit.detector_error_model(decompose_errors=True)
        >>> H, L, priors = dem_to_matrices(dem)
        >>> print(f"H shape: {H.shape}, L shape: {L.shape}")
    """
    row_inds_H: list[int] = []
    col_inds_H: list[int] = []
    row_inds_L: list[int] = []
    col_inds_L: list[int] = []
    priors: list[float] = []

    col_idx = 0
    for instruction in dem.flattened():
        if instruction.type == "error":
            p = instruction.args_copy()[0]
            targets = instruction.targets_copy()
            priors.append(p)
            for t in targets:
                if t.is_relative_detector_id():
                    row_inds_H.append(t.val)
                    col_inds_H.append(col_idx)
                elif t.is_logical_observable_id():
                    row_inds_L.append(t.val)
                    col_inds_L.append(col_idx)
            col_idx += 1

    num_errors = col_idx

    H = scipy.sparse.csc_matrix(
        (np.ones(len(row_inds_H), dtype=np.uint8), (row_inds_H, col_inds_H)),
        shape=(dem.num_detectors, num_errors),
        dtype=np.uint8,
    )

    L = scipy.sparse.csc_matrix(
        (np.ones(len(row_inds_L), dtype=np.uint8), (row_inds_L, col_inds_L)),
        shape=(dem.num_observables, num_errors),
        dtype=np.uint8,
    )

    return H, L, np.array(priors)


def get_channel_llrs(priors: np.ndarray, clip_min: float = 1e-10) -> np.ndarray:
    """
    Convert prior probabilities to Log-Likelihood Ratios (LLRs).

    LLR = log((1-p)/p) where p is the error probability.
    Positive LLR indicates the qubit is more likely error-free.

    Args:
        priors: Array of error probabilities
        clip_min: Minimum probability to avoid log(0)

    Returns:
        Array of LLR values
    """
    p_clipped = np.clip(priors, clip_min, 1 - clip_min)
    return np.log((1 - p_clipped) / p_clipped)
