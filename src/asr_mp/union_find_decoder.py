"""
Union-Find Decoder: LCD Proxy using fusion-blossom

Provides a Union-Find based decoder as a baseline/proxy for Riverlane's
Local Clustering Decoder (LCD). Uses the fusion-blossom library.
"""

import time

import numpy as np
import sinter
import stim

# Try to import fusion-blossom
FUSION_BLOSSOM_AVAILABLE = False
try:
    import fusion_blossom as fb

    FUSION_BLOSSOM_AVAILABLE = True
except ImportError:
    fb = None


class UnionFindDecoder:
    """
    Union-Find decoder using fusion-blossom as LCD proxy.

    This decoder serves as a baseline comparison for the ASR-MP decoder,
    representing the class of fast, hardware-friendly decoders like
    Riverlane's Local Clustering Decoder.
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
        self.num_detectors = dem.num_detectors
        self.num_observables = dem.num_observables

        # Build matching graph from DEM
        self._build_matching_graph()

    def _build_matching_graph(self):
        """Build the matching graph from the DEM."""
        # For now, use a simple implementation that returns zeros
        # TODO: Implement proper fusion-blossom graph construction
        self._solver = None

    def decode(self, syndrome: np.ndarray) -> np.ndarray:
        """
        Decode a single syndrome using Union-Find.

        Args:
            syndrome: Binary syndrome array (num_detectors,)

        Returns:
            Logical correction array (num_observables,)
        """
        t0 = time.perf_counter()

        # Simple fallback: return zeros
        # TODO: Implement proper fusion-blossom decoding
        correction = np.zeros(self.num_observables, dtype=np.uint8)

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
    """Sinter-compatible compiled decoder wrapper for Union-Find."""

    def __init__(self, dem: stim.DetectorErrorModel):
        self.dem = dem
        self.decoder = UnionFindDecoder(dem)

    def decode_shots_bit_packed(
        self,
        *,
        bit_packed_detection_event_data: np.ndarray,
        **kwargs,
    ) -> np.ndarray:
        """Decode multiple shots from bit-packed syndrome data."""
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
    """Sinter Decoder factory for Union-Find (LCD proxy)."""

    def compile_decoder_for_dem(
        self,
        *,
        dem: stim.DetectorErrorModel,
        **kwargs,
    ) -> sinter.CompiledDecoder:
        """Compile a decoder for the given DEM."""
        return UnionFindCompiledDecoder(dem)

    def decode_via_files(self, *args, **kwargs):
        """Not implemented - use compile_decoder_for_dem instead."""
        raise NotImplementedError("Use compile_decoder_for_dem for this decoder")
