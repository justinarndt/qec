"""
ASR-MP: Adaptive Soft-Reliability Message Passing Decoder

A high-precision quantum error correction decoder designed for drift-resilient
fault tolerance. Implements Belief Propagation with Ordered Statistics Decoding
(BP+OSD) for rotated surface codes.

Key Features:
    - 2x reduction in logical error rates vs MWPM at d=3
    - Drift resilience under ±30% control parameter variation
    - O(N) parallelizable for FPGA synthesis
"""

__version__ = "1.0.0-alpha"
__author__ = "Justin Arndt"
__email__ = "justin@example.com"

from .decoder import ASRMPDecoder, TesseractBPOSD
from .dem_utils import dem_to_matrices
from .noise_models import (
    generate_leakage_circuit,
    generate_leakage_tasks,
    generate_stress_circuit,
    generate_undeniable_tasks,
)
from .union_find_decoder import UnionFindDecoder

__all__ = [
    "ASRMPDecoder",
    "TesseractBPOSD",
    "UnionFindDecoder",
    "generate_stress_circuit",
    "generate_undeniable_tasks",
    "generate_leakage_circuit",
    "generate_leakage_tasks",
    "dem_to_matrices",
    "__version__",
]
