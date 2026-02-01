"""
Union-Find Decoder: LCD Proxy using fusion-blossom

Provides a Union-Find based decoder as a baseline/proxy for Riverlane's
Local Clustering Decoder (LCD). Uses the fusion-blossom library.
"""

import time
from typing import Optional

import numpy as np
import sinter
import stim

try:
    from fusion_blossom import SolverSerial, SolverInitializer
    FUSION_BLOSSOM_AVAILABLE = True
except ImportError:
    FUSION_BLOSSOM_AVAILABLE = False


class UnionFindDecoder:
    """
    Union-Find decoder using fusion-blossom as LCD proxy.

    This decoder serves as a baseline comparison for the ASR-MP decoder,
    representing the class of fast, hardware-friendly decoders like
    Riverlane's Local Clustering Decoder.

    Attributes:
        dem: The detector error model
        latencies: List of per-shot decode times (for profiling)

    Example:
        >>> dem = circuit.detector_error_model(decompose_errors=True)
        >>> decoder = UnionFindDecoder(dem)
        >>> correction = decoder.decode(syndrome)
    """

    def __init__(self, dem: stim.DetectorErrorModel):
        """
        Initialize the Union-Find decoder.

        Args:
            dem: Stim DetectorErrorModel

        Raises:
            ImportError: If fusion-blossom is not installed
        """
        if not FUSION_BLOSSOM_AVAILABLE:
            raise ImportError(
                "fusion-blossom is required for UnionFindDecoder. "
                "Install with: pip install fusion-blossom"
            )

        self.dem = dem
        self.latencies: list[float] = []

        # Initialize the fusion-blossom solver from the DEM
        self._initializer = SolverInitializer.from_detector_error_model(dem)
        self._solver: Optional[SolverSerial] = None

    def _get_solver(self) -> SolverSerial:
        """Get or create a solver instance."""
        if self._solver is None:
            self._solver = SolverSerial(self._initializer)
        return self._solver

    def decode(self, syndrome: np.ndarray) -> np.ndarray:
        """
        Decode a single syndrome using Union-Find.

        Args:
            syndrome: Binary syndrome array (num_detectors,)

        Returns:
            Logical correction array (num_observables,)
        """
        t0 = time.perf_counter()

        solver = self._get_solver()
        solver.clear()

        # Inject syndrome defects
        defect_indices = np.where(syndrome)[0].tolist()
        for idx in defect_indices:
            solver.add_defect(idx)

        # Solve and extract correction
        solver.solve()
        correction = np.zeros(self.dem.num_observables, dtype=np.uint8)

        # Get the logical observable corrections from the solution
        for obs_idx in range(self.dem.num_observables):
            if solver.get_observable(obs_idx):
                correction[obs_idx] = 1

        self.latencies.append(time.perf_counter() - t0)
        return correction

    def get_average_latency(self) -> float:
        """Get average decode latency in seconds."""
        if not self.latencies:
            return 0.0
        return sum(self.latencies) / len(self.latencies)

    def reset_latencies(self) -> None:
        """Clear latency tracking data."""
        self.latencies.clear()


class UnionFindCompiledDecoder(sinter.CompiledDecoder):
    """
    Sinter-compatible compiled decoder wrapper for Union-Find.
    """

    def __init__(self, dem: stim.DetectorErrorModel):
        """
        Initialize the compiled decoder.

        Args:
            dem: Stim DetectorErrorModel
        """
        self.dem = dem
        self.decoder = UnionFindDecoder(dem)

    def decode_shots_bit_packed(
        self,
        *,
        bit_packed_detection_event_data: np.ndarray,
        **kwargs,
    ) -> np.ndarray:
        """
        Decode multiple shots from bit-packed syndrome data.

        Args:
            bit_packed_detection_event_data: Bit-packed syndrome array

        Returns:
            Bit-packed logical predictions
        """
        num_shots = bit_packed_detection_event_data.shape[0]
        shots = np.unpackbits(
            bit_packed_detection_event_data,
            axis=1,
            count=self.dem.num_detectors,
            bitorder="little",
        )
        num_obs = self.dem.num_observables
        predictions = np.zeros((num_shots, num_obs), dtype=np.uint8)

        for i in range(num_shots):
            syndrome = shots[i]
            predictions[i] = self.decoder.decode(syndrome)

        return np.packbits(predictions, axis=1, bitorder="little")

    @property
    def latencies(self) -> list[float]:
        """Access decoder latencies for profiling."""
        return self.decoder.latencies


class UnionFindSinterDecoder(sinter.Decoder):
    """
    Sinter Decoder factory for Union-Find (LCD proxy).

    Register this with sinter to use the Union-Find decoder in benchmarks:

        samples = sinter.collect(
            tasks=tasks,
            decoders=['pymatching', 'union_find'],
            custom_decoders={'union_find': UnionFindSinterDecoder()},
            ...
        )
    """

    def compile_decoder_for_dem(
        self,
        *,
        dem: stim.DetectorErrorModel,
        **kwargs,
    ) -> sinter.CompiledDecoder:
        """
        Compile a decoder for the given DEM.

        Args:
            dem: Stim DetectorErrorModel

        Returns:
            Compiled decoder instance
        """
        return UnionFindCompiledDecoder(dem)

    def decode_via_files(self, *args, **kwargs):
        """Not implemented - use compile_decoder_for_dem instead."""
        raise NotImplementedError("Use compile_decoder_for_dem for this decoder")
