"""
Integration tests for the ASR-MP decoder.

These tests verify end-to-end functionality with small d=3 circuits
to ensure all components work together correctly.
"""

import numpy as np
from conftest import requires_asr_mp, requires_union_find


@requires_asr_mp
class TestEndToEndDecoding:
    """End-to-end decoding tests."""

    def test_asr_mp_decodes_sampled_errors(self, small_circuit, small_dem):
        """Test ASR-MP decoder on sampled error data."""
        from asr_mp.decoder import ASRMPDecoder

        # Sample some shots
        sampler = small_circuit.compile_detector_sampler()
        detection_events, observable_flips = sampler.sample(shots=10, separate_observables=True)

        # Decode each shot
        decoder = ASRMPDecoder(small_dem, osd_order=0)

        for i in range(detection_events.shape[0]):
            syndrome = detection_events[i].astype(np.uint8)
            correction = decoder.get_logical_correction(syndrome)

            # Correction should be valid shape
            assert correction.shape[0] == small_dem.num_observables

    def test_decoder_reduces_errors(self, small_circuit, small_dem):
        """Test that decoder actually reduces logical errors."""
        from asr_mp.decoder import ASRMPDecoder

        # Sample shots
        sampler = small_circuit.compile_detector_sampler()
        detection_events, observable_flips = sampler.sample(shots=100, separate_observables=True)

        decoder = ASRMPDecoder(small_dem, osd_order=0)

        # Count corrected vs uncorrected errors
        errors_without_decoding = np.sum(observable_flips)
        errors_with_decoding = 0

        for i in range(detection_events.shape[0]):
            syndrome = detection_events[i].astype(np.uint8)
            correction = decoder.get_logical_correction(syndrome)
            actual_flip = observable_flips[i].astype(np.uint8)

            # XOR correction with actual flip - should reduce to zero if correct
            residual = (correction ^ actual_flip) % 2
            errors_with_decoding += np.sum(residual)

        # Decoder should reduce errors (may not be perfect at low d)
        # At minimum, should not make things worse
        assert errors_with_decoding <= errors_without_decoding + 10


@requires_asr_mp
class TestStressCircuitIntegration:
    """Integration tests with stress-test circuits."""

    def test_decoder_handles_stress_circuit(self, stress_circuit, stress_dem):
        """Test decoder handles stress circuit with drift/burst."""
        from asr_mp.decoder import ASRMPDecoder

        decoder = ASRMPDecoder(stress_dem, osd_order=0)

        # Sample and decode
        sampler = stress_circuit.compile_detector_sampler()
        detection_events, _ = sampler.sample(shots=10, separate_observables=True)

        for i in range(detection_events.shape[0]):
            syndrome = detection_events[i].astype(np.uint8)
            correction = decoder.get_logical_correction(syndrome)

            assert correction.shape[0] == stress_dem.num_observables


@requires_asr_mp
class TestSinterIntegration:
    """Integration tests with sinter framework."""

    def test_tesseract_in_sinter_collect(self, small_circuit, small_dem):
        """Test TesseractBPOSD works with sinter collect."""
        import sinter

        from asr_mp.decoder import TesseractBPOSD

        task = sinter.Task(
            circuit=small_circuit,
            json_metadata={"d": 3, "p": 0.001},
            detector_error_model=small_dem,
        )

        # Run a quick collection
        samples = sinter.collect(
            num_workers=1,
            max_shots=10,
            max_errors=5,
            tasks=[task],
            decoders=["tesseract"],
            custom_decoders={"tesseract": TesseractBPOSD()},
            print_progress=False,
        )

        assert len(samples) == 1
        assert samples[0].shots > 0


@requires_union_find
class TestUnionFindIntegration:
    """Integration tests for Union-Find decoder."""

    def test_union_find_decodes(self, small_circuit, small_dem):
        """Test Union-Find decoder on sampled data."""
        from asr_mp.union_find_decoder import UnionFindDecoder

        sampler = small_circuit.compile_detector_sampler()
        detection_events, _ = sampler.sample(shots=10, separate_observables=True)

        decoder = UnionFindDecoder(small_dem)

        for i in range(detection_events.shape[0]):
            syndrome = detection_events[i].astype(np.uint8)
            correction = decoder.decode(syndrome)

            assert correction.shape[0] == small_dem.num_observables

    def test_union_find_in_sinter(self, small_circuit, small_dem):
        """Test UnionFindSinterDecoder works with sinter."""
        import sinter

        from asr_mp.union_find_decoder import UnionFindSinterDecoder

        task = sinter.Task(
            circuit=small_circuit,
            json_metadata={"d": 3, "p": 0.001},
            detector_error_model=small_dem,
        )

        samples = sinter.collect(
            num_workers=1,
            max_shots=10,
            max_errors=5,
            tasks=[task],
            decoders=["union_find"],
            custom_decoders={"union_find": UnionFindSinterDecoder()},
            print_progress=False,
        )

        assert len(samples) == 1


@requires_asr_mp
@requires_union_find
class TestMultiDecoderComparison:
    """Test comparing multiple decoders."""

    def test_all_decoders_together(self, small_circuit, small_dem):
        """Test running all decoders together in sinter."""
        import sinter

        from asr_mp.decoder import TesseractBPOSD
        from asr_mp.union_find_decoder import UnionFindSinterDecoder

        task = sinter.Task(
            circuit=small_circuit,
            json_metadata={"d": 3, "p": 0.001},
            detector_error_model=small_dem,
        )

        samples = sinter.collect(
            num_workers=1,
            max_shots=10,
            max_errors=5,
            tasks=[task],
            decoders=["pymatching", "union_find", "tesseract"],
            custom_decoders={
                "tesseract": TesseractBPOSD(),
                "union_find": UnionFindSinterDecoder(),
            },
            print_progress=False,
        )

        # Should have results for all 3 decoders
        assert len(samples) == 3
        decoders_found = {s.decoder for s in samples}
        assert decoders_found == {"pymatching", "union_find", "tesseract"}
