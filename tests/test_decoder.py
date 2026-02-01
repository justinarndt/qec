"""
Unit tests for the ASR-MP decoder.
"""

import numpy as np
import pytest
import stim

from conftest import requires_asr_mp


@requires_asr_mp
class TestASRMPDecoder:
    """Tests for the ASRMPDecoder class."""

    def test_decoder_initialization(self, small_dem):
        """Test that decoder initializes correctly."""
        from asr_mp.decoder import ASRMPDecoder

        decoder = ASRMPDecoder(small_dem, osd_order=0)

        assert decoder.dem == small_dem
        assert decoder.H is not None
        assert decoder.L is not None
        assert decoder.priors is not None
        assert len(decoder.latencies) == 0

    def test_decode_zero_syndrome(self, asr_mp_decoder, zero_syndrome):
        """Test decoding with no errors (zero syndrome)."""
        correction = asr_mp_decoder.get_logical_correction(zero_syndrome)

        # Zero syndrome should give zero correction
        assert correction.shape[0] == asr_mp_decoder.dem.num_observables
        assert np.sum(correction) == 0

    def test_decode_returns_valid_shape(self, asr_mp_decoder, sample_syndrome):
        """Test that decode returns correct shape."""
        error = asr_mp_decoder.decode(sample_syndrome)

        # Error should match number of error mechanisms
        assert error.shape[0] == asr_mp_decoder.H.shape[1]

    def test_logical_correction_shape(self, asr_mp_decoder, sample_syndrome):
        """Test that logical correction has correct shape."""
        correction = asr_mp_decoder.get_logical_correction(sample_syndrome)

        assert correction.shape[0] == asr_mp_decoder.dem.num_observables

    def test_latency_tracking(self, asr_mp_decoder, sample_syndrome):
        """Test that latency is tracked."""
        asr_mp_decoder.reset_latencies()
        assert len(asr_mp_decoder.latencies) == 0

        asr_mp_decoder.decode(sample_syndrome)
        assert len(asr_mp_decoder.latencies) == 1
        assert asr_mp_decoder.latencies[0] > 0

        asr_mp_decoder.decode(sample_syndrome)
        assert len(asr_mp_decoder.latencies) == 2

    def test_average_latency(self, asr_mp_decoder, sample_syndrome):
        """Test average latency calculation."""
        asr_mp_decoder.reset_latencies()

        for _ in range(5):
            asr_mp_decoder.decode(sample_syndrome)

        avg = asr_mp_decoder.get_average_latency()
        assert avg > 0
        assert len(asr_mp_decoder.latencies) == 5

    def test_reset_latencies(self, asr_mp_decoder, sample_syndrome):
        """Test latency reset."""
        asr_mp_decoder.decode(sample_syndrome)
        assert len(asr_mp_decoder.latencies) > 0

        asr_mp_decoder.reset_latencies()
        assert len(asr_mp_decoder.latencies) == 0

    def test_configurable_parameters(self, small_dem):
        """Test decoder with different configurations."""
        from asr_mp.decoder import ASRMPDecoder

        # Fast config
        decoder_fast = ASRMPDecoder(
            small_dem,
            bp_method="product_sum",
            max_iter=10,
            osd_method="osd_0",
            osd_order=0,
        )
        assert decoder_fast.max_iter == 10
        assert decoder_fast.osd_order == 0

        # High precision config
        decoder_precise = ASRMPDecoder(
            small_dem,
            bp_method="product_sum",
            max_iter=50,
            osd_method="osd_cs",
            osd_order=10,
        )
        assert decoder_precise.max_iter == 50
        assert decoder_precise.osd_order == 10


@requires_asr_mp
class TestTesseractBPOSD:
    """Tests for the sinter-compatible TesseractBPOSD decoder."""

    def test_sinter_decoder_creation(self):
        """Test that sinter decoder can be created."""
        from asr_mp.decoder import TesseractBPOSD

        decoder = TesseractBPOSD()
        assert decoder is not None

    def test_compile_decoder_for_dem(self, small_dem):
        """Test compiling decoder for DEM."""
        from asr_mp.decoder import TesseractBPOSD, TesseractCompiledDecoder

        factory = TesseractBPOSD()
        compiled = factory.compile_decoder_for_dem(dem=small_dem)

        assert isinstance(compiled, TesseractCompiledDecoder)

    def test_decode_shots_bit_packed(self, small_dem):
        """Test bit-packed decoding."""
        from asr_mp.decoder import TesseractBPOSD

        factory = TesseractBPOSD()
        compiled = factory.compile_decoder_for_dem(dem=small_dem)

        # Create bit-packed syndrome data (1 shot, all zeros)
        num_det_bytes = (small_dem.num_detectors + 7) // 8
        bit_packed = np.zeros((1, num_det_bytes), dtype=np.uint8)

        result = compiled.decode_shots_bit_packed(
            bit_packed_detection_event_data=bit_packed
        )

        num_obs_bytes = (small_dem.num_observables + 7) // 8
        assert result.shape == (1, num_obs_bytes)

    def test_decode_multiple_shots(self, small_dem):
        """Test decoding multiple shots."""
        from asr_mp.decoder import TesseractBPOSD

        factory = TesseractBPOSD()
        compiled = factory.compile_decoder_for_dem(dem=small_dem)

        num_shots = 10
        num_det_bytes = (small_dem.num_detectors + 7) // 8
        bit_packed = np.zeros((num_shots, num_det_bytes), dtype=np.uint8)

        result = compiled.decode_shots_bit_packed(
            bit_packed_detection_event_data=bit_packed
        )

        num_obs_bytes = (small_dem.num_observables + 7) // 8
        assert result.shape == (num_shots, num_obs_bytes)
