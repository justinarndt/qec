"""
ASR-MP Decoder: Adaptive Soft-Reliability Message Passing

High-precision quantum error correction decoder implementing Belief Propagation
with Ordered Statistics Decoding (BP+OSD) for rotated surface codes.
"""

import time
import warnings
from typing import Optional

import numpy as np
import sinter
import stim

from .dem_utils import dem_to_matrices

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Import ldpc with version compatibility
try:
    from ldpc import BpOsdDecoder
except ImportError:
    from ldpc import bposd_decoder as BpOsdDecoder


class ASRMPDecoder:
    """
    Adaptive Soft-Reliability Message Passing Decoder.

    A high-precision decoder using Belief Propagation with OSD post-processing.
    Designed for drift-resilient fault tolerance in the Tera-Quop regime.

    Attributes:
        H: Parity check matrix (sparse)
        L: Logical observable matrix (sparse)
        priors: Prior error probabilities
        latencies: List of per-shot decode times (for profiling)

    Example:
        >>> dem = circuit.detector_error_model(decompose_errors=True)
        >>> decoder = ASRMPDecoder(dem)
        >>> correction = decoder.decode(syndrome)
    """

    def __init__(
        self,
        dem: stim.DetectorErrorModel,
        bp_method: str = "product_sum",
        max_iter: int = 50,
        osd_method: str = "osd_cs",
        osd_order: int = 35,
        error_rate: float = 0.001,
    ):
        """
        Initialize the ASR-MP decoder.

        Args:
            dem: Stim DetectorErrorModel
            bp_method: BP algorithm variant ("product_sum" for exact arithmetic)
            max_iter: Maximum BP iterations (balanced for speed/accuracy)
            osd_method: OSD variant ("osd_cs" for Combination Sweep)
            osd_order: OSD search depth (35 for deep search, 0 for fast)
            error_rate: Base error rate for channel initialization
        """
        self.dem = dem
        self.H, self.L, self.priors = dem_to_matrices(dem)
        self.latencies: list[float] = []

        # Configuration parameters
        self.bp_method = bp_method
        self.max_iter = max_iter
        self.osd_method = osd_method
        self.osd_order = osd_order

        # Initialize the BP+OSD decoder
        self.bpd = BpOsdDecoder(
            self.H,
            error_rate=error_rate,
            channel_probs=self.priors,
            bp_method=bp_method,
            max_iter=max_iter,
            osd_method=osd_method,
            osd_order=osd_order,
        )

    def decode(self, syndrome: np.ndarray) -> np.ndarray:
        """
        Decode a single syndrome.

        Args:
            syndrome: Binary syndrome array (num_detectors,)

        Returns:
            Estimated error array
        """
        t0 = time.perf_counter()
        estimated_error = self.bpd.decode(syndrome)
        self.latencies.append(time.perf_counter() - t0)
        return estimated_error

    def get_logical_correction(self, syndrome: np.ndarray) -> np.ndarray:
        """
        Get the logical observable correction for a syndrome.

        Args:
            syndrome: Binary syndrome array

        Returns:
            Logical correction array (num_observables,)
        """
        estimated_error = self.decode(syndrome)
        return (self.L @ estimated_error) % 2

    def get_average_latency(self) -> float:
        """Get average decode latency in seconds."""
        if not self.latencies:
            return 0.0
        return sum(self.latencies) / len(self.latencies)

    def reset_latencies(self) -> None:
        """Clear latency tracking data."""
        self.latencies.clear()


class TesseractCompiledDecoder(sinter.CompiledDecoder):
    """
    Sinter-compatible compiled decoder wrapper for ASR-MP.

    This class implements the sinter.CompiledDecoder interface for
    integration with sinter's Monte Carlo sampling framework.
    """

    def __init__(self, dem: stim.DetectorErrorModel):
        """
        Initialize the compiled decoder.

        Args:
            dem: Stim DetectorErrorModel
        """
        self.dem = dem
        self.decoder = ASRMPDecoder(dem)

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
                Shape: (num_shots, ceil(num_detectors/8))

        Returns:
            Bit-packed logical predictions
                Shape: (num_shots, ceil(num_observables/8))
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
            correction = self.decoder.get_logical_correction(syndrome)
            predictions[i] = np.asarray(correction, dtype=np.uint8).flatten()[:num_obs]

        return np.packbits(predictions, axis=1, bitorder="little")

    @property
    def latencies(self) -> list[float]:
        """Access decoder latencies for profiling."""
        return self.decoder.latencies


class TesseractBPOSD(sinter.Decoder):
    """
    Sinter Decoder factory for ASR-MP/Tesseract.

    Register this with sinter to use the ASR-MP decoder in benchmarks:

        samples = sinter.collect(
            tasks=tasks,
            decoders=['pymatching', 'tesseract'],
            custom_decoders={'tesseract': TesseractBPOSD()},
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
        return TesseractCompiledDecoder(dem)

    def decode_via_files(self, *args, **kwargs):
        """Not implemented - use compile_decoder_for_dem instead."""
        raise NotImplementedError("Use compile_decoder_for_dem for this decoder")
