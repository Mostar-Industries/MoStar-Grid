/**
 * Neo4j Graph Database Service for Frontend
 * Provides graph visualization and query capabilities
 */

interface Neo4jConfig {
  uri: string;
  user: string;
  password: string;
  database: string;
}

interface GraphNode {
  id: string;
  label: string;
  properties: Record<string, any>;
}

interface GraphRelationship {
  id: string;
  type: string;
  source: string;
  target: string;
  properties: Record<string, any>;
}

interface GraphData {
  nodes: GraphNode[];
  relationships: GraphRelationship[];
}

class Neo4jService {
  private config: Neo4jConfig;
  private apiUrl: string;

  constructor() {
    this.config = {
      uri: import.meta.env.VITE_NEO4J_URI || '',
      user: import.meta.env.VITE_NEO4J_USER || 'neo4j',
      password: import.meta.env.VITE_NEO4J_PASSWORD || '',
      database: import.meta.env.VITE_NEO4J_DATABASE || 'neo4j',
    };
    
    // Use backend proxy for Neo4j queries to avoid CORS issues
    this.apiUrl = '/api/neo4j';
  }

  isConfigured(): boolean {
    return !!(this.config.uri && this.config.password);
  }

  /**
   * Execute a Cypher query via backend proxy
   */
  async query(cypher: string, parameters: Record<string, any> = {}): Promise<any> {
    if (!this.isConfigured()) {
      throw new Error('Neo4j not configured. Check environment variables.');
    }

    try {
      const response = await fetch(this.apiUrl + '/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          cypher,
          parameters,
          database: this.config.database,
        }),
      });

      if (!response.ok) {
        throw new Error(`Neo4j query failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Neo4j query error:', error);
      throw error;
    }
  }

  /**
   * Get graph data for visualization
   */
  async getGraphData(limit: number = 100): Promise<GraphData> {
    const cypher = `
      MATCH (n)
      OPTIONAL MATCH (n)-[r]->(m)
      RETURN n, r, m
      LIMIT $limit
    `;

    const result = await this.query(cypher, { limit });
    return this.transformToGraphData(result);
  }

  /**
   * Search nodes by label and properties
   */
  async searchNodes(label: string, filters: Record<string, any> = {}): Promise<GraphNode[]> {
    const whereClause = Object.keys(filters).length > 0
      ? 'WHERE ' + Object.keys(filters).map(k => `n.${k} = $${k}`).join(' AND ')
      : '';

    const cypher = `
      MATCH (n:${label})
      ${whereClause}
      RETURN n
      LIMIT 100
    `;

    const result = await this.query(cypher, filters);
    return this.transformToNodes(result);
  }

  /**
   * Create a node
   */
  async createNode(label: string, properties: Record<string, any>): Promise<GraphNode> {
    const cypher = `
      CREATE (n:${label} $props)
      RETURN n
    `;

    const result = await this.query(cypher, { props: properties });
    return this.transformToNodes(result)[0];
  }

  /**
   * Create a relationship between two nodes
   */
  async createRelationship(
    fromId: string,
    toId: string,
    type: string,
    properties: Record<string, any> = {}
  ): Promise<GraphRelationship> {
    const cypher = `
      MATCH (a), (b)
      WHERE id(a) = $fromId AND id(b) = $toId
      CREATE (a)-[r:${type} $props]->(b)
      RETURN r
    `;

    const result = await this.query(cypher, { fromId, toId, props: properties });
    return this.transformToRelationships(result)[0];
  }

  /**
   * Get neighbors of a node
   */
  async getNeighbors(nodeId: string, depth: number = 1): Promise<GraphData> {
    const cypher = `
      MATCH path = (n)-[*1..${depth}]-(m)
      WHERE id(n) = $nodeId
      RETURN path
      LIMIT 100
    `;

    const result = await this.query(cypher, { nodeId });
    return this.transformToGraphData(result);
  }

  /**
   * Transform Neo4j result to graph data
   */
  private transformToGraphData(result: any): GraphData {
    const nodes: GraphNode[] = [];
    const relationships: GraphRelationship[] = [];
    const nodeIds = new Set<string>();
    const nodeIdMap = new Map<string, string>(); // Map node name to generated ID

    // Process result records
    if (result.records) {
      result.records.forEach((record: any, recordIndex: number) => {
        // Handle 'n' node (source)
        if (record.n && typeof record.n === 'object') {
          const nodeName = record.n.name || `node_${recordIndex}_n`;
          if (!nodeIdMap.has(nodeName)) {
            const nodeId = `n_${nodeIds.size}`;
            nodeIdMap.set(nodeName, nodeId);
            nodeIds.add(nodeId);
            nodes.push({
              id: nodeId,
              label: record.n.type || record.n.region || 'Node',
              properties: record.n,
            });
          }
        }

        // Handle 'm' node (target)
        if (record.m && typeof record.m === 'object' && Object.keys(record.m).length > 0) {
          const nodeName = record.m.name || `node_${recordIndex}_m`;
          if (!nodeIdMap.has(nodeName)) {
            const nodeId = `n_${nodeIds.size}`;
            nodeIdMap.set(nodeName, nodeId);
            nodeIds.add(nodeId);
            nodes.push({
              id: nodeId,
              label: record.m.type || record.m.region || record.m.purpose || 'Node',
              properties: record.m,
            });
          }
        }

        // Handle 'r' relationship (array format: [source, type, target])
        if (record.r && Array.isArray(record.r) && record.r.length >= 2) {
          const relationshipType = record.r[1]; // Middle element is the relationship type
          const sourceName = record.n?.name;
          const targetName = record.m?.name;

          if (sourceName && targetName && nodeIdMap.has(sourceName) && nodeIdMap.has(targetName)) {
            relationships.push({
              id: `r_${relationships.length}`,
              type: relationshipType || 'RELATED_TO',
              source: nodeIdMap.get(sourceName)!,
              target: nodeIdMap.get(targetName)!,
              properties: {},
            });
          }
        }
      });
    }

    return { nodes, relationships };
  }

  /**
   * Transform Neo4j result to nodes array
   */
  private transformToNodes(result: any): GraphNode[] {
    const nodes: GraphNode[] = [];

    if (result.records) {
      result.records.forEach((record: any) => {
        const node = record.n || record[0];
        if (node) {
          nodes.push({
            id: node.identity?.toString() || node.id?.toString(),
            label: node.labels?.[0] || 'Node',
            properties: node.properties || {},
          });
        }
      });
    }

    return nodes;
  }

  /**
   * Transform Neo4j result to relationships array
   */
  private transformToRelationships(result: any): GraphRelationship[] {
    const relationships: GraphRelationship[] = [];

    if (result.records) {
      result.records.forEach((record: any) => {
        const rel = record.r || record[0];
        if (rel) {
          relationships.push({
            id: rel.identity?.toString() || rel.id?.toString(),
            type: rel.type,
            source: rel.start?.toString() || rel.startNodeId?.toString(),
            target: rel.end?.toString() || rel.endNodeId?.toString(),
            properties: rel.properties || {},
          });
        }
      });
    }

    return relationships;
  }

  /**
   * Test connection
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.query('RETURN 1 as test');
      return true;
    } catch (error) {
      console.error('Neo4j connection test failed:', error);
      return false;
    }
  }
}

// Export singleton instance
export const neo4jService = new Neo4jService();

// Export types
export type { Neo4jConfig, GraphNode, GraphRelationship, GraphData };
