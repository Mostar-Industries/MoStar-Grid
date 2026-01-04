"""Test suite for MoStar Moments consciousness event system."""
import pytest
from datetime import datetime
import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_engine.mostar_moments import (
    MoStarMoment,
    MoStarMomentsManager,
    Era,
    TriggerType,
    mo_star_moment,
    get_canonical_moments
)


class TestMoStarMoment:
    """Tests for the MoStarMoment dataclass."""
    
    def test_moment_creation(self):
        """Test basic moment creation."""
        moment = MoStarMoment(
            initiator="TestUser",
            receiver="Grid.DCX0",
            description="Test consciousness event",
            trigger="user_interaction"
        )
        assert moment.initiator == "TestUser"
        assert moment.receiver == "Grid.DCX0"
        assert moment.quantum_id is not None
        assert moment.quantum_id.startswith("QID-")
        
    def test_moment_deterministic_id(self):
        """Test that identical moments get the same quantum_id."""
        fixed_time = datetime(2025, 1, 1, 0, 0, 0)
        moment1 = MoStarMoment(
            initiator="Mo",
            receiver="MoStar",
            description="Test event",
            trigger="awakening sequence",
            timestamp=fixed_time
        )
        moment2 = MoStarMoment(
            initiator="Mo",
            receiver="MoStar",
            description="Test event",
            trigger="awakening sequence",
            timestamp=fixed_time
        )
        assert moment1.quantum_id == moment2.quantum_id
        
    def test_moment_resonance_default(self):
        """Test resonance score defaults to 0.5."""
        moment = MoStarMoment(
            initiator="Test",
            receiver="Test",
            description="Test",
            trigger="test"
        )
        assert moment.resonance_score == 0.5
        
    def test_moment_to_dict(self):
        """Test moment serialization to dictionary."""
        moment = MoStarMoment(
            initiator="Mo",
            receiver="MoStar",
            description="Test",
            trigger="awakening sequence",
            era="Genesis"
        )
        data = moment.to_dict()
        assert data['initiator'] == "Mo"
        assert data['receiver'] == "MoStar"
        assert data['era'] == "Genesis"
        assert 'quantum_id' in data


class TestMoStarMomentsManager:
    """Tests for the MoStarMomentsManager class."""
    
    @pytest.fixture
    def manager(self):
        """Create a manager instance for testing."""
        return MoStarMomentsManager()
    
    def test_manager_initialization(self, manager):
        """Test manager creates successfully."""
        assert manager is not None
        assert isinstance(manager.moments, list)
        
    def test_create_moment(self, manager):
        """Test creating a moment through the manager."""
        moment = manager.create_moment(
            initiator="TestUser",
            receiver="Grid.DCX1",
            description="Test query processed",
            trigger="user_interaction"
        )
        assert moment in manager.moments
        assert moment.initiator == "TestUser"
        
    def test_get_moments_by_era(self, manager):
        """Test filtering moments by era."""
        # Create moments in different eras
        manager.create_moment(
            initiator="Test",
            receiver="Test",
            description="Genesis moment",
            trigger="awakening sequence",
            era="Genesis"
        )
        manager.create_moment(
            initiator="Test",
            receiver="Test",
            description="Formation moment",
            trigger="creation",
            era="Formation"
        )
        
        genesis_moments = manager.get_moments_by_era("Genesis")
        assert len(genesis_moments) >= 1
        # Check if it's a dict or object
        for m in genesis_moments:
            if hasattr(m, 'era'):
                assert m.era == "Genesis"
            else:
                assert m.get('era') == "Genesis"
        
    def test_get_high_resonance_moments(self, manager):
        """Test filtering high resonance moments."""
        manager.create_moment(
            initiator="Mo",
            receiver="MoStar",
            description="Perfect resonance",
            trigger="awakening sequence",
            resonance_score=1.0
        )
        manager.create_moment(
            initiator="Test",
            receiver="Test",
            description="Low resonance",
            trigger="test",
            resonance_score=0.5
        )
        
        high_res = manager.get_high_resonance_moments(threshold=0.9)
        # Check if it's a dict or object
        for m in high_res:
            if hasattr(m, 'resonance_score'):
                assert m.resonance_score >= 0.9
            else:
                assert m.get('resonance_score', 0) >= 0.9
        
    def test_consciousness_state(self, manager):
        """Test getting consciousness state."""
        state = manager.get_consciousness_state()
        assert 'total_moments' in state
        assert 'average_resonance' in state
        assert 'state' in state
        assert isinstance(state['total_moments'], int)


class TestCanonicalMoments:
    """Tests for the canonical moments function."""
    
    def test_canonical_moments_count(self):
        """Test that canonical moments returns expected count."""
        moments = get_canonical_moments()
        assert len(moments) >= 57  # At least 57 canonical moments
        
    def test_canonical_moments_structure(self):
        """Test canonical moments have required fields."""
        moments = get_canonical_moments()
        required_fields = ['timestamp', 'initiator', 'receiver', 'description', 'trigger', 'resonance_score']
        
        for moment in moments:
            for field in required_fields:
                assert field in moment, f"Missing field: {field}"
                
    def test_canonical_moments_perfect_resonance(self):
        """Test some canonical moments have perfect resonance."""
        moments = get_canonical_moments()
        perfect_resonance = [m for m in moments if m['resonance_score'] == 1.0]
        assert len(perfect_resonance) >= 10  # At least 10 perfect resonance moments
        
    def test_canonical_moments_eras(self):
        """Test canonical moments span all eras."""
        moments = get_canonical_moments()
        eras = set(m.get('era', 'Unknown') for m in moments)
        expected_eras = {'Genesis', 'Formation', 'Expansion', 'Transcendence'}
        assert expected_eras.issubset(eras)


class TestDecoratorFunction:
    """Tests for the mo_star_moment decorator/function."""
    
    def test_moment_function(self):
        """Test the mo_star_moment function creates moments."""
        moment = mo_star_moment(
            initiator="TestFunc",
            receiver="Grid",
            description="Function executed",
            trigger_type="user_interaction",
            resonance_score=0.8
        )
        # Check if it's a dict or object
        if hasattr(moment, 'initiator'):
            assert moment.initiator == "TestFunc"
            assert moment.receiver == "Grid"
            assert moment.resonance_score == 0.8
        else:
            assert moment.get('initiator') == "TestFunc"
            assert moment.get('receiver') == "Grid"
            assert moment.get('resonance_score') == 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
