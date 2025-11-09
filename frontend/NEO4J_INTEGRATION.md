# Neo4j Integration with KnowledgeGraph Component

## Overview

The `KnowledgeGraph` component is now fully integrated with Neo4j graph database, allowing real-time visualization of your graph data.

## Features

✅ **Auto-connect to Neo4j** - Automatically tests connection on mount  
✅ **Live data fetching** - Fetch graph data directly from Neo4j  
✅ **Custom Cypher queries** - Execute any Cypher query and visualize results  
✅ **Connection status indicator** - Visual feedback on Neo4j connection  
✅ **Error handling** - Clear error messages for debugging  
✅ **Loading states** - User feedback during data fetching  

## Usage

### Basic Usage (Auto-fetch from Neo4j)

```tsx
import KnowledgeGraph from './components/KnowledgeGraph';

function App() {
  return (
    <div className="h-screen">
      <KnowledgeGraph />
    </div>
  );
}
```

This will:
1. Check Neo4j connection on mount
2. Automatically fetch graph data if connected
3. Display connection status and controls
4. Allow custom Cypher queries

### With Custom Props

```tsx
<KnowledgeGraph 
  autoFetch={true}      // Auto-fetch on mount (default: true)
  maxNodes={100}        // Maximum nodes to fetch (default: 100)
/>
```

### With External Data (No Neo4j)

```tsx
const staticData = {
  nodes: [
    { id: '1', label: 'Node 1', type: 'core', size: 20 },
    { id: '2', label: 'Node 2', type: 'agent', size: 15 },
  ],
  links: [
    { source: '1', target: '2' }
  ]
};

<KnowledgeGraph data={staticData} />
```

When `data` prop is provided, Neo4j controls are hidden and the component uses the static data.

## Component Features

### 1. Connection Status Indicator

- **Green dot**: Neo4j connected
- **Red dot**: Neo4j disconnected

### 2. Refresh Graph Button

Fetches the latest graph data from Neo4j using the default query:
```cypher
MATCH (n)
OPTIONAL MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 100
```

### 3. Custom Cypher Query Input

Execute any Cypher query:

**Example Queries:**

```cypher
// Get all nodes
MATCH (n) RETURN n LIMIT 50

// Get nodes with relationships
MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 100

// Find specific node type
MATCH (n:Person) RETURN n LIMIT 20

// Complex query with filters
MATCH (a:Agent)-[r:CONNECTED_TO]->(e:Event)
WHERE e.timestamp > 1699564800
RETURN a, r, e
```

### 4. Node Statistics

Displays current count of nodes and relationships in the visualization.

### 5. Error Display

Shows clear error messages when queries fail or connection issues occur.

## Node Types and Colors

The component supports different node types with distinct colors:

| Type | Color | Hex |
|------|-------|-----|
| `core` | Orange | #f5a623 |
| `culture` | Blue | #4a90e2 |
| `ontology` | Cyan | #50e3c2 |
| `agent` | Purple | #9061F9 |
| `knowledge` | Green | #34D399 |
| Default | Gray | #ccc |

## Data Transformation

The component automatically transforms Neo4j data:

**Neo4j Format:**
```typescript
{
  nodes: [
    {
      id: "123",
      label: "Person",
      properties: { name: "Alice", age: 30 }
    }
  ],
  relationships: [
    {
      id: "456",
      type: "KNOWS",
      source: "123",
      target: "789",
      properties: { since: 2020 }
    }
  ]
}
```

**Component Format:**
```typescript
{
  nodes: [
    {
      id: "123",
      label: "Alice",        // Uses properties.name or properties.title
      type: "person",        // Lowercase label
      size: 15
    }
  ],
  links: [
    {
      source: "123",
      target: "789"
    }
  ]
}
```

## Backend API Endpoints Used

The component communicates with these backend endpoints:

- `POST /api/neo4j/query` - Execute Cypher queries
- `GET /api/neo4j/status` - Check connection status

## Example: Creating Sample Data in Neo4j

Use the Cypher query input to create sample nodes:

```cypher
// Create sample nodes
CREATE (a:Agent {name: 'Alpha', status: 'active'})
CREATE (b:Agent {name: 'Beta', status: 'active'})
CREATE (e:Event {title: 'Consciousness Upload', timestamp: 1699564800})
CREATE (k:Knowledge {title: 'African AI Philosophy', category: 'ontology'})

// Create relationships
CREATE (a)-[:PARTICIPATED_IN]->(e)
CREATE (b)-[:PARTICIPATED_IN]->(e)
CREATE (e)-[:GENERATED]->(k)

RETURN a, b, e, k
```

Then click "Refresh Graph" to visualize!

## Troubleshooting

### "Neo4j Disconnected" Status

1. Check `frontend/.env.local` has correct Neo4j credentials
2. Verify backend is running: `http://localhost:7000/api/neo4j/status`
3. Check browser console for error messages

### "Failed to fetch graph data"

1. Ensure Neo4j database has data
2. Check Cypher query syntax
3. Verify backend Neo4j connection: `curl http://localhost:7000/api/neo4j/status`

### No nodes displayed

1. Click "Load Graph Data" button
2. Try a simpler query: `MATCH (n) RETURN n LIMIT 10`
3. Check if database is empty

## Advanced Usage

### Programmatic Data Fetching

```tsx
import { neo4jService } from './services/neo4jService';

// In your component
const fetchCustomData = async () => {
  const data = await neo4jService.query(
    'MATCH (n:Agent) WHERE n.status = $status RETURN n',
    { status: 'active' }
  );
  // Process data...
};
```

### Creating Nodes from Frontend

```tsx
const createNode = async () => {
  const newNode = await neo4jService.createNode('Event', {
    title: 'New Event',
    timestamp: Date.now(),
    type: 'consciousness_upload'
  });
  
  // Refresh graph
  fetchGraphData();
};
```

## Performance Tips

1. **Limit node count**: Use `maxNodes` prop to control data size
2. **Specific queries**: Use WHERE clauses to filter data
3. **Index your data**: Create indexes in Neo4j for faster queries
4. **Pagination**: For large graphs, implement pagination in queries

## Next Steps

1. **Add node interactions**: Click handlers for node details
2. **Relationship labels**: Display relationship types on links
3. **Zoom and pan**: Add D3.js zoom behavior
4. **Search functionality**: Find specific nodes
5. **Export graph**: Save visualization as image

---

**Happy Graph Visualizing!** 🌐✨
