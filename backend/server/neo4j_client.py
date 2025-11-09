"""
Neo4j Graph Database Client for MoStar Grid
Manages connections to Neo4j for knowledge graph operations
"""
import os
import logging
from typing import Optional, Dict, Any, List
from neo4j import GraphDatabase, Driver

logger = logging.getLogger("grid.neo4j")


class Neo4jClient:
    """Neo4j database client with connection pooling"""
    
    def __init__(self):
        self.driver: Optional[Driver] = None
        self._connected = False
        
    def connect(self) -> bool:
        """
        Establish connection to Neo4j database
        Returns True if successful, False otherwise
        """
        try:
            uri = os.getenv("NEO4J_URI")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD")
            
            if not uri or not password or password == "<YOUR_NEO4J_PASSWORD>":
                logger.warning("⚠️  Neo4j credentials not configured")
                return False
            
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            
            # Verify connectivity
            self.driver.verify_connectivity()
            
            self._connected = True
            logger.info(f"✅ Connected to Neo4j at {uri}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Neo4j connection failed: {e}")
            self._connected = False
            return False
    
    def close(self):
        """Close the Neo4j driver connection"""
        if self.driver:
            self.driver.close()
            self._connected = False
            logger.info("✅ Neo4j connection closed")
    
    @property
    def is_connected(self) -> bool:
        """Check if Neo4j is connected"""
        return self._connected
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            
        Returns:
            List of result records as dictionaries
        """
        if not self.is_connected:
            raise RuntimeError("Neo4j not connected. Call connect() first.")
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def create_node(self, label: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a node in the graph
        
        Args:
            label: Node label (e.g., "Agent", "Event", "Location")
            properties: Node properties
            
        Returns:
            Created node properties
        """
        query = f"CREATE (n:{label} $props) RETURN n"
        result = self.execute_query(query, {"props": properties})
        return result[0]["n"] if result else {}
    
    def create_relationship(
        self, 
        from_id: str, 
        to_id: str, 
        rel_type: str, 
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create a relationship between two nodes
        
        Args:
            from_id: Source node ID
            to_id: Target node ID
            rel_type: Relationship type
            properties: Optional relationship properties
            
        Returns:
            True if successful
        """
        query = f"""
        MATCH (a), (b)
        WHERE id(a) = $from_id AND id(b) = $to_id
        CREATE (a)-[r:{rel_type} $props]->(b)
        RETURN r
        """
        result = self.execute_query(query, {
            "from_id": from_id,
            "to_id": to_id,
            "props": properties or {}
        })
        return len(result) > 0
    
    def find_nodes(self, label: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Find nodes by label and optional filters
        
        Args:
            label: Node label
            filters: Optional property filters
            
        Returns:
            List of matching nodes
        """
        if filters:
            where_clause = " AND ".join([f"n.{k} = ${k}" for k in filters.keys()])
            query = f"MATCH (n:{label}) WHERE {where_clause} RETURN n"
            result = self.execute_query(query, filters)
        else:
            query = f"MATCH (n:{label}) RETURN n"
            result = self.execute_query(query)
        
        return [record["n"] for record in result]


# Global Neo4j client instance
neo4j_client = Neo4jClient()


def get_neo4j_client() -> Neo4jClient:
    """Get the global Neo4j client instance"""
    return neo4j_client
