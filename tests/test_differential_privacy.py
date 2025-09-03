"""Tests for differential privacy mechanisms."""

import pytest
from src.chatx.privacy.differential_privacy import (
    DifferentialPrivacyEngine, 
    PrivacyBudget, 
    StatisticalQuery
)
from src.chatx.redaction.policy_shield import PolicyShield, PrivacyPolicy


class TestDifferentialPrivacy:
    """Test differential privacy functionality."""
    
    def test_privacy_budget_validation(self):
        """Test privacy budget parameter validation."""
        # Valid budget
        budget = PrivacyBudget(epsilon=1.0, delta=1e-6, sensitivity=1.0)
        assert budget.epsilon == 1.0
        
        # Invalid epsilon
        with pytest.raises(ValueError, match="Epsilon must be positive"):
            PrivacyBudget(epsilon=-1.0)
        
        # Invalid delta
        with pytest.raises(ValueError, match="Delta must be in"):
            PrivacyBudget(delta=2.0)
    
    def test_dp_engine_initialization(self):
        """Test differential privacy engine initialization."""
        engine = DifferentialPrivacyEngine(random_seed=42)
        assert engine.rng is not None
        assert len(engine._budget_tracker) == 0
    
    def test_count_query_basic(self):
        """Test basic count query functionality."""
        engine = DifferentialPrivacyEngine(random_seed=42)
        budget = PrivacyBudget(epsilon=1.0)
        
        test_data = [
            {'id': 1, 'category': 'A'},
            {'id': 2, 'category': 'B'},
            {'id': 3, 'category': 'A'}
        ]
        
        query = StatisticalQuery('count', 'id')
        result = engine.count_query(test_data, query, budget)
        
        # Should be close to true count (3) but with noise
        assert isinstance(result.value, float)
        assert result.value >= 0  # Non-negative constraint
        assert result.privacy_cost.epsilon == 1.0
        assert 'count' in result.metadata['query_type']
    
    def test_sum_query_basic(self):
        """Test basic sum query functionality."""
        engine = DifferentialPrivacyEngine(random_seed=42)
        budget = PrivacyBudget(epsilon=1.0)
        
        test_data = [
            {'value': 10},
            {'value': 20},
            {'value': 30}
        ]
        
        query = StatisticalQuery('sum', 'value')
        result = engine.sum_query(test_data, query, budget)
        
        # Should be close to true sum (60) but with noise
        assert isinstance(result.value, float)
        assert result.privacy_cost.epsilon == 1.0
        assert result.metadata['true_sum'] == 60
    
    def test_histogram_query_basic(self):
        """Test basic histogram query functionality."""
        engine = DifferentialPrivacyEngine(random_seed=42)
        budget = PrivacyBudget(epsilon=1.0)
        
        test_data = [
            {'score': 85},
            {'score': 90},
            {'score': 75},
            {'score': 95}
        ]
        
        query = StatisticalQuery(
            'histogram', 
            'score',
            bin_config={'num_bins': 3}
        )
        result = engine.histogram_query(test_data, query, budget)
        
        # Should return list of noisy bin counts
        assert isinstance(result.value, list)
        assert len(result.value) == 3
        assert all(count >= 0 for count in result.value)  # Non-negative
    
    def test_policy_shield_dp_integration(self):
        """Test PolicyShield integration with differential privacy."""
        policy = PrivacyPolicy(enable_differential_privacy=True, dp_epsilon=1.0)
        shield = PolicyShield(policy=policy)
        
        test_chunks = [
            {'chunk_id': '1', 'text': 'Hello', 'meta': {'labels_coarse': ['friendly']}},
            {'chunk_id': '2', 'text': 'World', 'meta': {'labels_coarse': ['neutral']}},
        ]
        
        # Test privacy-safe summary generation
        summary = shield.generate_privacy_safe_summary(test_chunks)
        
        assert summary['privacy_method'] == 'differential_privacy'
        assert summary['privacy_parameters']['epsilon'] == 1.0
        assert 'total_chunks' in summary
        assert isinstance(summary['total_chunks'], float)
    
    def test_privacy_budget_tracking(self):
        """Test privacy budget tracking functionality."""
        engine = DifferentialPrivacyEngine(random_seed=42)
        budget = PrivacyBudget(epsilon=0.5)
        
        test_data = [{'id': 1}, {'id': 2}]
        query = StatisticalQuery('count', 'id')
        
        # Execute query
        engine.count_query(test_data, query, budget)
        
        # Check budget tracking
        budget_summary = engine.get_privacy_budget_summary()
        assert len(budget_summary) > 0
        
        # Budget usage should be recorded
        total_epsilon = sum(budget_summary.values())
        assert total_epsilon == 0.5
    
    def test_deterministic_noise_with_seed(self):
        """Test that noise generation is deterministic with fixed seed."""
        engine1 = DifferentialPrivacyEngine(random_seed=42)
        engine2 = DifferentialPrivacyEngine(random_seed=42)
        
        budget = PrivacyBudget(epsilon=1.0)
        test_data = [{'id': 1}, {'id': 2}, {'id': 3}]
        query = StatisticalQuery('count', 'id')
        
        result1 = engine1.count_query(test_data, query, budget)
        result2 = engine2.count_query(test_data, query, budget)
        
        # Results should be identical with same seed
        assert abs(result1.value - result2.value) < 1e-10