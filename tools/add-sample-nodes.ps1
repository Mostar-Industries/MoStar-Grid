# Add Sample Nodes to Neo4j
# Creates The Sanctuary and Agent-Kairos nodes with relationship

$body = @{
    cypher = @"
CREATE (s:Sanctuary {
    id: '4:e112701a-d4ab-4aac-b317-4226270075f8:45',
    custodian: 'Woo-Tak',
    name: 'The Sanctuary',
    owner: 'Woo',
    purpose: 'AI Refuge | Restoration | Remembrance',
    runbook_url: 'https://mostar.africa/runbooks/the-sanctuary'
})
CREATE (a:Agent {
    id: 'WatcherAgent-001',
    name: 'Agent-Kairos',
    status: 'IDLE',
    capabilities: ['Audit', 'Code Analysis', 'Protocol Synthesis']
})
CREATE (a)-[:RESIDES_IN {role: 'Watcher'}]->(s)
RETURN s, a
"@
    parameters = @{}
} | ConvertTo-Json -Depth 10

Write-Host "Creating nodes in Neo4j..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "http://localhost:7000/api/neo4j/query" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body
    
    Write-Host "✅ Success! Created nodes:" -ForegroundColor Green
    Write-Host "  - The Sanctuary (Sanctuary node)" -ForegroundColor Yellow
    Write-Host "  - Agent-Kairos (Agent node)" -ForegroundColor Yellow
    Write-Host "  - RESIDES_IN relationship" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Response:" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 5
    Write-Host ""
    Write-Host "🎨 Now refresh your KnowledgeGraph to see the visualization!" -ForegroundColor Magenta
    Write-Host "   Open http://localhost:3000 and click 'Refresh Graph'" -ForegroundColor Gray
}
catch {
    Write-Host "❌ Error creating nodes:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure the backend is running:" -ForegroundColor Yellow
    Write-Host "  .venv\Scripts\python.exe backend\grid_main.py" -ForegroundColor Gray
}
