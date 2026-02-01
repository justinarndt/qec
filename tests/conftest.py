"""
Pytest configuration and fixtures for ASR-MP tests.
"""

import pytest
import numpy as np
import stim

# Optional imports - tests will skip if not available
try:
    from asr_mp.decoder import ASRMPDecoder, TesseractBPOSD
    from asr_mp.dem_utils import dem_to_matrices
    from asr_mp.noise_models import generate_stress_circuit, generate_standard_circuit
    ASR_MP_AVAILABLE = True
except ImportError:
    ASR_MP_AVAILABLE = False

try:
    from asr_mp.union_find_decoder import UnionFindDecoder
    UNION_FIND_AVAILABLE = True
except ImportError:
    UNION_FIND_AVAILABLE = False


# Skip markers
requires_asr_mp = pytest.mark.skipif(
    not ASR_MP_AVAILABLE,
    reason="asr_mp package not available"
)

requires_union_find = pytest.mark.skipif(
    not UNION_FIND_AVAILABLE,
    reason="fusion-blossom not available"
)


@pytest.fixture
def small_circuit() -> stim.Circuit:
    """Generate a small d=3 surface code circuit for quick tests."""
    return stim.Circuit.generated(
        "surface_code:rotated_memory_z",
        distance=3,
        rounds=3,
        after_clifford_depolarization=0.001,
        before_round_data_depolarization=0.001,
        before_measure_flip_probability=0.001,
        after_reset_flip_probability=0.001,
    )


@pytest.fixture
def small_dem(small_circuit: stim.Circuit) -> stim.DetectorErrorModel:
    """Generate DEM from small circuit."""
    return small_circuit.detector_error_model(decompose_errors=True)


@pytest.fixture
def stress_circuit() -> stim.Circuit:
    """Generate a stress-test circuit with drift and burst."""
    if not ASR_MP_AVAILABLE:
        pytest.skip("asr_mp not available")
    return generate_stress_circuit(d=3, base_p=0.003, drift_strength=0.3, burst_prob=0.05)


@pytest.fixture
def stress_dem(stress_circuit: stim.Circuit) -> stim.DetectorErrorModel:
    """Generate DEM from stress circuit."""
    return stress_circuit.detector_error_model(decompose_errors=True)


@pytest.fixture
def sample_syndrome(small_dem: stim.DetectorErrorModel) -> np.ndarray:
    """Generate a sample syndrome for testing."""
    # Create a simple syndrome with a few triggered detectors
    syndrome = np.zeros(small_dem.num_detectors, dtype=np.uint8)
    # Trigger every 5th detector for a pattern
    syndrome[::5] = 1
    return syndrome


@pytest.fixture
def zero_syndrome(small_dem: stim.DetectorErrorModel) -> np.ndarray:
    """Generate an all-zero syndrome (no errors)."""
    return np.zeros(small_dem.num_detectors, dtype=np.uint8)


@pytest.fixture
def asr_mp_decoder(small_dem: stim.DetectorErrorModel):
    """Create an ASR-MP decoder instance."""
    if not ASR_MP_AVAILABLE:
        pytest.skip("asr_mp not available")
    return ASRMPDecoder(small_dem, osd_order=0)  # Fast OSD for tests


@pytest.fixture
def union_find_decoder(small_dem: stim.DetectorErrorModel):
    """Create a Union-Find decoder instance."""
    if not UNION_FIND_AVAILABLE:
        pytest.skip("fusion-blossom not available")
    return UnionFindDecoder(small_dem)
