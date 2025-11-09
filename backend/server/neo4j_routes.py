"""
Neo4j API Routes for Frontend
Provides secure proxy for Neo4j graph queries
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging

from server.neo4j_client import get_neo4j_client

logger = logging.getLogger("grid.neo4j_routes")

router = APIRouter(prefix="/api/neo4j", tags=["neo4j"])


class Neo4jQueryRequest(BaseModel):
    cypher: str
    parameters: Optional[Dict[str, Any]] = None
    database: Optional[str] = "neo4j"


class Neo4jQueryResponse(BaseModel):
    records: List[Dict[str, Any]]
    summary: Optional[Dict[str, Any]] = None


@router.post("/query", response_model=Neo4jQueryResponse)
async def execute_query(request: Neo4jQueryRequest):
    """
    Execute a Cypher query against Neo4j
    """
    neo4j = get_neo4j_client()
    
    if not neo4j.is_connected:
        raise HTTPException(
            status_code=503,
            detail="Neo4j database not connected"
        )
    
    try:
        # Execute query
        results = neo4j.execute_query(request.cypher, request.parameters)
        
        return Neo4jQueryResponse(
            records=results,
            summary={"count": len(results)}
        )
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Query execution failed: {str(e)}"
        )


@router.get("/status")
async def neo4j_status():
    """
    Get Neo4j connection status
    """
    neo4j = get_neo4j_client()
    
    return {
        "connected": neo4j.is_connected,
        "type": "graph_database",
        "driver": "neo4j-python"
    }


@router.get("/schema")
async def get_schema():
    """
    Get database schema information
    """
    neo4j = get_neo4j_client()
    
    if not neo4j.is_connected:
        raise HTTPException(
            status_code=503,
            detail="Neo4j database not connected"
        )
    
    try:
        # Get node labels
        labels_query = "CALL db.labels()"
        labels_result = neo4j.execute_query(labels_query)
        labels = [record.get('label') for record in labels_result]
        
        # Get relationship types
        rel_types_query = "CALL db.relationshipTypes()"
        rel_types_result = neo4j.execute_query(rel_types_query)
        relationship_types = [record.get('relationshipType') for record in rel_types_result]
        
        return {
            "labels": labels,
            "relationship_types": relationship_types
        }
    except Exception as e:
        logger.error(f"Schema retrieval failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Schema retrieval failed: {str(e)}"
        )


@router.get("/stats")
async def get_stats():
    """
    Get database statistics
    """
    neo4j = get_neo4j_client()
    
    if not neo4j.is_connected:
        raise HTTPException(
            status_code=503,
            detail="Neo4j database not connected"
        )
    
    try:
        # Get node count
        node_count_query = "MATCH (n) RETURN count(n) as count"
        node_result = neo4j.execute_query(node_count_query)
        node_count = node_result[0].get('count', 0) if node_result else 0
        
        # Get relationship count
        rel_count_query = "MATCH ()-[r]->() RETURN count(r) as count"
        rel_result = neo4j.execute_query(rel_count_query)
        rel_count = rel_result[0].get('count', 0) if rel_result else 0
        
        return {
            "nodes": node_count,
            "relationships": rel_count
        }
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Stats retrieval failed: {str(e)}"
        )
