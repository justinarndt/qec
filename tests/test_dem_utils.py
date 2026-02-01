"""
Unit tests for DEM utilities.
"""

import numpy as np
import scipy.sparse
from conftest import requires_asr_mp


@requires_asr_mp
class TestDemToMatrices:
    """Tests for dem_to_matrices function."""

    def test_returns_tuple(self, small_dem):
        """Test that function returns correct tuple."""
        from asr_mp.dem_utils import dem_to_matrices

        result = dem_to_matrices(small_dem)

        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_h_matrix_shape(self, small_dem):
        """Test H matrix has correct shape."""
        from asr_mp.dem_utils import dem_to_matrices

        H, L, priors = dem_to_matrices(small_dem)

        assert H.shape[0] == small_dem.num_detectors
        assert H.shape[1] == len(priors)

    def test_l_matrix_shape(self, small_dem):
        """Test L matrix has correct shape."""
        from asr_mp.dem_utils import dem_to_matrices

        H, L, priors = dem_to_matrices(small_dem)

        assert L.shape[0] == small_dem.num_observables
        assert L.shape[1] == len(priors)

    def test_matrices_are_sparse(self, small_dem):
        """Test that matrices are sparse."""
        from asr_mp.dem_utils import dem_to_matrices

        H, L, priors = dem_to_matrices(small_dem)

        assert scipy.sparse.issparse(H)
        assert scipy.sparse.issparse(L)

    def test_priors_are_probabilities(self, small_dem):
        """Test that priors are valid probabilities."""
        from asr_mp.dem_utils import dem_to_matrices

        H, L, priors = dem_to_matrices(small_dem)

        assert all(0 <= p <= 1 for p in priors)

    def test_h_matrix_is_binary(self, small_dem):
        """Test that H matrix contains only 0s and 1s."""
        from asr_mp.dem_utils import dem_to_matrices

        H, L, priors = dem_to_matrices(small_dem)

        H_dense = H.toarray()
        assert set(np.unique(H_dense)).issubset({0, 1})

    def test_l_matrix_is_binary(self, small_dem):
        """Test that L matrix contains only 0s and 1s."""
        from asr_mp.dem_utils import dem_to_matrices

        H, L, priors = dem_to_matrices(small_dem)

        L_dense = L.toarray()
        assert set(np.unique(L_dense)).issubset({0, 1})

    def test_h_matrix_dtype(self, small_dem):
        """Test H matrix dtype."""
        from asr_mp.dem_utils import dem_to_matrices

        H, L, priors = dem_to_matrices(small_dem)

        assert H.dtype == np.uint8

    def test_consistent_with_dem(self, small_dem):
        """Test that matrix dimensions are consistent with DEM."""
        from asr_mp.dem_utils import dem_to_matrices

        H, L, priors = dem_to_matrices(small_dem)

        # Number of errors should be positive
        assert len(priors) > 0
        # H and L should have same number of columns
        assert H.shape[1] == L.shape[1]


@requires_asr_mp
class TestGetChannelLlrs:
    """Tests for get_channel_llrs function."""

    def test_returns_array(self):
        """Test that function returns array."""
        from asr_mp.dem_utils import get_channel_llrs

        priors = np.array([0.1, 0.2, 0.3])
        llrs = get_channel_llrs(priors)

        assert isinstance(llrs, np.ndarray)
        assert len(llrs) == len(priors)

    def test_low_probability_gives_high_llr(self):
        """Test that low error probability gives high (positive) LLR."""
        from asr_mp.dem_utils import get_channel_llrs

        priors = np.array([0.001])
        llrs = get_channel_llrs(priors)

        # Low p means high certainty of no error → positive LLR
        assert llrs[0] > 0

    def test_high_probability_gives_low_llr(self):
        """Test that high error probability gives low (negative) LLR."""
        from asr_mp.dem_utils import get_channel_llrs

        priors = np.array([0.9])
        llrs = get_channel_llrs(priors)

        # High p means likely error → negative LLR
        assert llrs[0] < 0

    def test_half_probability_gives_zero_llr(self):
        """Test that p=0.5 gives LLR ≈ 0."""
        from asr_mp.dem_utils import get_channel_llrs

        priors = np.array([0.5])
        llrs = get_channel_llrs(priors)

        assert np.isclose(llrs[0], 0, atol=1e-10)

    def test_clipping_prevents_inf(self):
        """Test that clipping prevents infinite LLRs."""
        from asr_mp.dem_utils import get_channel_llrs

        priors = np.array([0.0, 1.0])
        llrs = get_channel_llrs(priors)

        assert np.all(np.isfinite(llrs))

    def test_monotonic(self):
        """Test that LLR decreases as probability increases."""
        from asr_mp.dem_utils import get_channel_llrs

        priors = np.array([0.01, 0.1, 0.3, 0.5, 0.7, 0.9])
        llrs = get_channel_llrs(priors)

        # LLR should be monotonically decreasing
        for i in range(len(llrs) - 1):
            assert llrs[i] > llrs[i + 1]
