"""
synthetic.py
MostlyAI integration for synthetic data generation with African lifecycle logic.
"""

import os
from typing import Dict, Optional
import httpx
from fastapi import HTTPException

MOSTLY_API_KEY = os.getenv("MOSTLY_API_KEY")
MOSTLY_BASE_URL = os.getenv("MOSTLY_BASE_URL", "https://app.mostly.ai/api")
MOSTLY_GENERATOR_ID = os.getenv("MOSTLY_GENERATOR_ID")


async def get_generator_info() -> Dict:
    """
    Fetch generator metadata from MostlyAI.
    Returns generator configuration and status.
    """
    if not MOSTLY_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="MOSTLY_API_KEY not configured"
        )
    
    if not MOSTLY_GENERATOR_ID:
        raise HTTPException(
            status_code=503,
            detail="MOSTLY_GENERATOR_ID not configured"
        )
    
    url = f"{MOSTLY_BASE_URL}/generators/{MOSTLY_GENERATOR_ID}"
    headers = {
        "Authorization": f"Bearer {MOSTLY_API_KEY}",
        "Content-Type": "application/json",
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=502,
            detail=f"MostlyAI API error: {str(e)}"
        )


async def generate_synthetic_probe(size: Dict[str, int]) -> Dict:
    """
    Generate synthetic data with lifecycle-aware sizing using MostlyAI SDK.
    
    Args:
        size: Dict with keys like 'infancy', 'childhood', 'science'
              representing lifecycle stage counts.
    
    Returns:
        Probe data with samples.
    """
    if not MOSTLY_API_KEY or not MOSTLY_GENERATOR_ID:
        raise HTTPException(
            status_code=503,
            detail="MostlyAI not configured (missing API_KEY or GENERATOR_ID)"
        )
    
    try:
        # Use the official SDK
        from mostlyai.sdk import MostlyAI
        mostly = MostlyAI(api_key=MOSTLY_API_KEY, base_url=MOSTLY_BASE_URL)
        
        # Get generator
        generator = mostly.generators.get(MOSTLY_GENERATOR_ID)
        
        # Probe uses SDK's probe method with total size
        total_size = sum(size.values())
        probe_data = mostly.probe(generator, size=total_size)
        
        return {
            "ok": True,
            "generator_id": MOSTLY_GENERATOR_ID,
            "generator_name": generator.name if hasattr(generator, 'name') else "Unknown",
            "size_requested": total_size,
            "lifecycle_distribution": size,
            "sample_count": len(probe_data) if isinstance(probe_data, list) else total_size,
            "message": f"Generated {total_size} probe samples"
        }
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="MostlyAI SDK not installed. Run: pip install -U mostlyai"
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"MostlyAI probe error: {str(e)}"
        )


# Lifecycle stage mapping (African context) - DEPRECATED: use get_allowed_tables()
LIFECYCLE_STAGES = {
    "infancy": {"min_age": 0, "max_age": 2, "focus": "early_bonding"},
    "childhood": {"min_age": 3, "max_age": 12, "focus": "cultural_learning"},
    "adolescence": {"min_age": 13, "max_age": 19, "focus": "identity_formation"},
    "young_adult": {"min_age": 20, "max_age": 35, "focus": "community_building"},
    "midlife": {"min_age": 36, "max_age": 55, "focus": "wisdom_transfer"},
    "elder": {"min_age": 56, "max_age": 120, "focus": "ancestral_guidance"},
    "science": {"focus": "knowledge_domain"},  # Added for compatibility
}


async def get_allowed_tables() -> set:
    """
    Dynamically fetch allowed tables from MostlyAI generator.
    Returns set of table names that the generator supports.
    """
    try:
        generator_info = await get_generator_info()
        # Extract table names from generator metadata
        tables = generator_info.get("tables", [])
        if isinstance(tables, list):
            return {t.get("name") for t in tables if isinstance(t, dict) and t.get("name")}
        return set()
    except Exception as e:
        print(f"[WARN] Could not fetch generator tables, using fallback: {e}")
        # Fallback to known lifecycle stages + common knowledge domains
        return {"infancy", "childhood", "adolescence", "adulthood", "science", "culture", "ethics", "knowledge_graph", "real_life"}


def validate_lifecycle_size(size: Dict[str, int]) -> bool:
    """
    Validate that lifecycle size dict contains valid stages.
    DEPRECATED: This uses hardcoded stages. Use validate_lifecycle_size_dynamic() instead.
    """
    for stage in size.keys():
        if stage not in LIFECYCLE_STAGES:
            return False
    return True


async def validate_lifecycle_size_dynamic(size: Dict[str, int]) -> tuple[bool, Optional[list]]:
    """
    Dynamically validate that size dict contains valid tables from the generator.
    Returns (is_valid, invalid_tables_list)
    """
    allowed = await get_allowed_tables()
    invalid = [k for k in size.keys() if k not in allowed]
    return (len(invalid) == 0, invalid if invalid else None)
