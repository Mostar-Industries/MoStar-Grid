import pytest
from core_engine.orchestrator import route_query, LOGISTICS_KEYWORDS
from core_engine.pdx_bridge import pdx_bridge

@pytest.mark.anyio
async def test_pdx_dispatch_trigger():
    # Force Body layer (dcx2) and include a logistics keyword
    prompt = "Dispatch medical supplies to Lagos immediately."
    metadata = {"force_layer": "dcx2"}
    
    # We expect this to trigger PDX dispatch because of 'dispatch' and 'medical'
    # Note: route_query calls call_ollama which we might want to mock if it's slow/unreliable
    # For now, let's see if we can check the logic flow.
    
    res = await route_query(prompt, metadata=metadata)
    
    # Check if PDX was triggered
    assert "pdx_dispatch" in res
    assert res["pdx_dispatch"]["status"] == "dispatched"
    assert "pdx_id" in res["pdx_dispatch"]
    assert res["pdx_dispatch"]["action"] == "AUTO_DISPATCH"

@pytest.mark.anyio
async def test_no_pdx_without_keywords():
    # Body layer but no logistics keywords
    prompt = "Tell me a joke."
    metadata = {"force_layer": "dcx2"}
    
    res = await route_query(prompt, metadata=metadata)
    
    # Check if PDX was NOT triggered
    assert "pdx_dispatch" not in res

def test_logistics_keywords():
    assert "medical" in LOGISTICS_KEYWORDS
    assert "dispatch" in LOGISTICS_KEYWORDS
    assert "cargo" in LOGISTICS_KEYWORDS
