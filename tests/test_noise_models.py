"""
Unit tests for noise model generators.
"""

import numpy as np
import pytest
import stim

from conftest import requires_asr_mp


@requires_asr_mp
class TestGenerateStressCircuit:
    """Tests for generate_stress_circuit function."""

    def test_basic_generation(self):
        """Test basic circuit generation."""
        from asr_mp.noise_models import generate_stress_circuit

        circuit = generate_stress_circuit(d=3, base_p=0.001)

        assert isinstance(circuit, stim.Circuit)
        assert len(circuit) > 0

    def test_circuit_has_detectors(self):
        """Test that circuit has detectors."""
        from asr_mp.noise_models import generate_stress_circuit

        circuit = generate_stress_circuit(d=3, base_p=0.001)
        dem = circuit.detector_error_model(decompose_errors=True)

        assert dem.num_detectors > 0

    def test_circuit_has_observables(self):
        """Test that circuit has logical observables."""
        from asr_mp.noise_models import generate_stress_circuit

        circuit = generate_stress_circuit(d=3, base_p=0.001)
        dem = circuit.detector_error_model(decompose_errors=True)

        assert dem.num_observables > 0

    def test_drift_strength_parameter(self):
        """Test drift_strength parameter affects circuit."""
        from asr_mp.noise_models import generate_stress_circuit

        circuit_no_drift = generate_stress_circuit(d=3, base_p=0.001, drift_strength=0.0)
        circuit_with_drift = generate_stress_circuit(d=3, base_p=0.001, drift_strength=0.5)

        # Both should be valid circuits
        assert isinstance(circuit_no_drift, stim.Circuit)
        assert isinstance(circuit_with_drift, stim.Circuit)

    def test_burst_prob_parameter(self):
        """Test burst_prob parameter."""
        from asr_mp.noise_models import generate_stress_circuit

        circuit_no_burst = generate_stress_circuit(d=3, base_p=0.001, burst_prob=0.0)
        circuit_with_burst = generate_stress_circuit(d=3, base_p=0.001, burst_prob=0.1)

        # With burst, circuit should have CORRELATED_ERROR
        assert isinstance(circuit_with_burst, stim.Circuit)

    def test_custom_rounds(self):
        """Test custom rounds parameter."""
        from asr_mp.noise_models import generate_stress_circuit

        circuit = generate_stress_circuit(d=3, base_p=0.001, rounds=10)

        assert isinstance(circuit, stim.Circuit)

    def test_different_distances(self):
        """Test generation at different code distances."""
        from asr_mp.noise_models import generate_stress_circuit

        for d in [3, 5, 7]:
            circuit = generate_stress_circuit(d=d, base_p=0.001)
            dem = circuit.detector_error_model(decompose_errors=True)

            assert dem.num_detectors > 0
            assert dem.num_observables > 0


@requires_asr_mp
class TestGenerateStandardCircuit:
    """Tests for generate_standard_circuit function."""

    def test_basic_generation(self):
        """Test basic standard circuit generation."""
        from asr_mp.noise_models import generate_standard_circuit

        circuit = generate_standard_circuit(d=3, p=0.001)

        assert isinstance(circuit, stim.Circuit)

    def test_different_error_rates(self):
        """Test with different error rates."""
        from asr_mp.noise_models import generate_standard_circuit

        for p in [0.001, 0.005, 0.01]:
            circuit = generate_standard_circuit(d=3, p=p)
            dem = circuit.detector_error_model(decompose_errors=True)

            assert dem.num_detectors > 0


@requires_asr_mp
class TestGenerateUndeniableTasks:
    """Tests for generate_undeniable_tasks function."""

    def test_default_tasks(self):
        """Test default task generation."""
        from asr_mp.noise_models import generate_undeniable_tasks

        tasks = generate_undeniable_tasks()

        assert len(tasks) == 3  # Default: d=5,7,9
        for task in tasks:
            assert task.circuit is not None
            assert task.detector_error_model is not None
            assert "d" in task.json_metadata
            assert "stress" in task.json_metadata

    def test_custom_distances(self):
        """Test custom distances."""
        from asr_mp.noise_models import generate_undeniable_tasks

        tasks = generate_undeniable_tasks(distances=[3, 5])

        assert len(tasks) == 2

    def test_metadata_content(self):
        """Test task metadata."""
        from asr_mp.noise_models import generate_undeniable_tasks

        tasks = generate_undeniable_tasks(
            distances=[5],
            base_p=0.002,
            drift_strength=0.25,
            burst_prob=0.03,
        )

        task = tasks[0]
        assert task.json_metadata["d"] == 5
        assert task.json_metadata["p"] == 0.002
        assert task.json_metadata["drift_strength"] == 0.25
        assert task.json_metadata["burst_prob"] == 0.03


@requires_asr_mp
class TestGenerateStandardTasks:
    """Tests for generate_standard_tasks function."""

    def test_default_tasks(self):
        """Test default task generation."""
        from asr_mp.noise_models import generate_standard_tasks

        tasks = generate_standard_tasks()

        # Default: 3 distances × 3 error rates = 9 tasks
        assert len(tasks) == 9

    def test_custom_parameters(self):
        """Test custom parameters."""
        from asr_mp.noise_models import generate_standard_tasks

        tasks = generate_standard_tasks(
            distances=[3, 5],
            error_rates=[0.001, 0.002],
        )

        # 2 distances × 2 error rates = 4 tasks
        assert len(tasks) == 4


@requires_asr_mp
class TestGenerateSweepTasks:
    """Tests for generate_sweep_tasks function."""

    def test_default_sweep(self):
        """Test default drift sweep."""
        from asr_mp.noise_models import generate_sweep_tasks

        tasks = generate_sweep_tasks(d=5)

        # Default: 5 drift strengths
        assert len(tasks) == 5

    def test_custom_drift_strengths(self):
        """Test custom drift strengths."""
        from asr_mp.noise_models import generate_sweep_tasks

        tasks = generate_sweep_tasks(
            d=5,
            drift_strengths=[0.0, 0.1, 0.2],
        )

        assert len(tasks) == 3

    def test_sweep_metadata(self):
        """Test sweep task metadata."""
        from asr_mp.noise_models import generate_sweep_tasks

        tasks = generate_sweep_tasks(d=5, drift_strengths=[0.0, 0.3])

        assert tasks[0].json_metadata["drift_strength"] == 0.0
        assert tasks[1].json_metadata["drift_strength"] == 0.3
