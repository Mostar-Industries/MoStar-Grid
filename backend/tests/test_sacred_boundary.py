import pytest
from core_engine.external_observer import ExternalSourceObserver, external_observer
from core_engine.moscript_engine import seal_action

@pytest.mark.anyio
async def test_external_observation_pdx():
    """Verify that PDX observation returns OBSERVED_NOT_INTEGRATED status."""
    observer = ExternalSourceObserver()
    
    result = await observer.observe('pdx', query="Check cargo status")
    
    assert result["status"] == "OBSERVED_NOT_INTEGRATED"
    assert result["source"] == "pdx"
    assert "observed_at" in result
    assert "data" in result

@pytest.mark.anyio
async def test_unknown_source_observation():
    """Verify that unknown sources return appropriate error."""
    observer = ExternalSourceObserver()
    
    result = await observer.observe('unknown_source')
    
    assert result["status"] == "SOURCE_NOT_FOUND"
    assert "error" in result

@pytest.mark.anyio
async def test_sanctioned_ingest_with_valid_seal():
    """Verify that data with valid seal can be ingested."""
    observer = ExternalSourceObserver()
    
    # Create test data and seal it
    test_data = {"source": "pdx", "cargo_id": "TEST-001"}
    seal_key = "MOSTAR_GRID_ANCESTRAL_KEY"
    signature = seal_action(test_data, seal_key)
    
    result = await observer.sanctioned_ingest(test_data, signature, seal_key)
    
    assert result["status"] == "SANCTIONED_INGESTION_SUCCESS"
    assert result["sealed"] is True

@pytest.mark.anyio
async def test_sanctioned_ingest_with_invalid_seal():
    """Verify that data without valid seal is rejected."""
    observer = ExternalSourceObserver()
    
    test_data = {"source": "pdx", "cargo_id": "TEST-002"}
    invalid_signature = "INVALID_SEAL_12345"
    
    result = await observer.sanctioned_ingest(test_data, invalid_signature, "WRONG_KEY")
    
    assert result["status"] == "COVENANT_VIOLATION"
    assert result["sealed"] is False
    assert "error" in result

def test_singleton_observer():
    """Verify that external_observer is properly initialized."""
    assert external_observer is not None
    assert isinstance(external_observer, ExternalSourceObserver)
