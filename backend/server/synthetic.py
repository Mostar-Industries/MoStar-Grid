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
    Generate synthetic data with lifecycle-aware sizing.
    
    Args:
        size: Dict with keys like 'infancy', 'childhood', 'science'
              representing lifecycle stage counts.
    
    Returns:
        Generation job details and status.
    """
    if not MOSTLY_API_KEY or not MOSTLY_GENERATOR_ID:
        raise HTTPException(
            status_code=503,
            detail="MostlyAI not configured (missing API_KEY or GENERATOR_ID)"
        )
    
    # Transform lifecycle sizes into MostlyAI probe format
    total_size = sum(size.values())
    
    url = f"{MOSTLY_BASE_URL}/generators/{MOSTLY_GENERATOR_ID}/probe"
    headers = {
        "Authorization": f"Bearer {MOSTLY_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "size": total_size,
        "metadata": {
            "lifecycle_distribution": size,
            "african_logic": True,
            "covenant_threshold": 0.97,
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "ok": True,
                "job_id": result.get("id"),
                "status": result.get("status"),
                "size": total_size,
                "lifecycle_distribution": size,
                "generator_id": MOSTLY_GENERATOR_ID,
            }
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=502,
            detail=f"MostlyAI generation error: {str(e)}"
        )


# Lifecycle stage mapping (African context)
LIFECYCLE_STAGES = {
    "infancy": {"min_age": 0, "max_age": 2, "focus": "early_bonding"},
    "childhood": {"min_age": 3, "max_age": 12, "focus": "cultural_learning"},
    "adolescence": {"min_age": 13, "max_age": 19, "focus": "identity_formation"},
    "young_adult": {"min_age": 20, "max_age": 35, "focus": "community_building"},
    "midlife": {"min_age": 36, "max_age": 55, "focus": "wisdom_transfer"},
    "elder": {"min_age": 56, "max_age": 120, "focus": "ancestral_guidance"},
}


def validate_lifecycle_size(size: Dict[str, int]) -> bool:
    """Validate that lifecycle size dict contains valid stages."""
    for stage in size.keys():
        if stage not in LIFECYCLE_STAGES:
            return False
    return True
