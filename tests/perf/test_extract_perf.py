"""Performance smoke tests for iMessage extraction."""

import pytest


class TestExtractionPerformance:
    """Test extraction performance meets targets."""
    
    @pytest.mark.perf
    def test_placeholder_for_pr6(self):
        """Placeholder test for PR-6 implementation."""
        # TODO: Implement in PR-6 (Validation + perf)
        # Test should cover:
        # - Generate N synthetic messages in test DB
        # - Measure end-to-end extraction throughput
        # - Target: ≥5k msgs/min/contact on dev laptop
        # - Non-blocking in CI (pytest marker)
        # - Print metrics for regression detection
        assert True  # Placeholder