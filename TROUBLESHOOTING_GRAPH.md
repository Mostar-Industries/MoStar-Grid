# Knowledge Graph Not Showing - Troubleshooting

## Issue
The "Knowledge Fabric Visualization" section appears empty on the dashboard.

## Root Cause
The KnowledgeGraph component is now fetching from Neo4j, but there are a few potential issues:

1. **No relationships in current data** - The graph needs both nodes AND relationships to visualize properly
2. **Component might be in loading state**
3. **Neo4j query might need adjustment**

## Quick Fixes

### Option 1: Check Browser Console

Open browser DevTools (F12) and check the Console tab for errors.

### Option 2: Verify Data Has Relationships

The current Neo4j data has nodes but may not have relationships between them. Run this query to check:

```bash
# Check for relationships
$body = @{ 
    cypher = 'MATCH ()-[r]->() RETURN count(r) as relationship_count'
    parameters = @{} 
} | ConvertTo-Json

Invoke-RestMethod -Uri 'http://localhost:7000/api/neo4j/query' `
    -Method Post `
    -ContentType 'application/json' `
    -Body $body
```

### Option 3: Create Sample Relationships

If there are no relationships, create some:

```powershell
# Run this to create relationships between governance systems
$body = @{
    cypher = @"
MATCH (a), (b)
WHERE a.name = 'Oba Kingship' AND b.name = 'Ashanti Confederacy'
CREATE (a)-[:INFLUENCED_BY {strength: 0.7}]->(b)

MATCH (c), (d)
WHERE c.name = 'Gadaa System' AND d.name = 'Indaba'
CREATE (c)-[:SIMILAR_TO {similarity: 0.8}]->(d)

MATCH (e), (f)
WHERE e.name = 'Kgotla' AND f.name = 'Palaver System'
CREATE (e)-[:IMPLEMENTS]->(f)

RETURN 'Relationships created' as result
"@
    parameters = @{}
} | ConvertTo-Json

Invoke-RestMethod -Uri 'http://localhost:7000/api/neo4j/query' `
    -Method Post `
    -ContentType 'application/json' `
    -Body $body
```

### Option 4: Check Component State

The component should show:
- 🟢 Green dot if connected
- 🔴 Red dot if disconnected
- Controls for refresh and query input

If you don't see these controls, the component might not be rendering properly.

### Option 5: Manual Refresh

Once on the page:
1. Look for the "Refresh Graph" button
2. Click it to manually fetch data
3. Or enter a query like: `MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 20`

### Option 6: Check Network Tab

In browser DevTools, check the Network tab:
1. Look for requests to `/api/neo4j/query`
2. Check if they're returning data
3. Look for any 404 or 500 errors

## Expected Behavior

When working correctly, you should see:

1. **Controls at top:**
   - Connection indicator (green/red dot)
   - "Refresh Graph" button
   - Query input field
   - Node/relationship count

2. **Graph visualization:**
   - Colored nodes (based on type)
   - Lines connecting nodes (relationships)
   - Node labels
   - Interactive (hover effects)

## Debug Query

Try this query in the component's query input:

```cypher
MATCH (n)
OPTIONAL MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 20
```

## If Still Not Working

1. **Check frontend console logs:**
   ```
   Open DevTools (F12) → Console tab
   Look for errors mentioning "neo4j" or "graph"
   ```

2. **Verify backend is accessible:**
   ```powershell
   curl http://localhost:7000/api/neo4j/status
   ```

3. **Check if component is mounted:**
   ```
   In DevTools Console, type:
   document.querySelector('.knowledge-graph-container')
   ```
   Should return an element, not null

4. **Try the mock data version:**
   Edit `DashboardPage.tsx` line 109:
   ```tsx
   // Change from:
   <KnowledgeGraph autoFetch={true} maxNodes={50} />
   
   // To:
   <KnowledgeGraph data={mockGraphData} />
   ```

## Common Issues

### Issue: "Neo4j Disconnected"
**Solution:** Check `frontend/.env.local` has `VITE_NEO4J_*` variables

### Issue: "Failed to fetch graph data"
**Solution:** Verify backend is running and Neo4j is connected

### Issue: Empty graph with no error
**Solution:** Data might have nodes but no relationships. Create some relationships.

### Issue: Component not rendering at all
**Solution:** Check browser console for import errors

## Next Steps

1. Open http://localhost:3000
2. Navigate to Dashboard
3. Scroll to "Knowledge Fabric Visualization"
4. Check for controls and connection indicator
5. Click "Refresh Graph" or "Load Graph Data"
6. Check browser console for any errors

## Files to Check

- `frontend/components/KnowledgeGraph.tsx` - Main component
- `frontend/components/DashboardPage.tsx` - Where it's used
- `frontend/services/neo4jService.ts` - Data fetching
- `frontend/.env.local` - Neo4j credentials

---

**If you see the controls but no graph, the data needs relationships!**  
**If you don't see controls at all, check browser console for errors.**
