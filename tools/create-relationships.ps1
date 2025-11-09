# Create Relationships Between Nodes in Neo4j
# This connects the existing governance systems and knowledge nodes

Write-Host "Creating relationships in Neo4j knowledge graph..." -ForegroundColor Cyan
Write-Host ""

# Create relationships between governance systems
$queries = @(
    @{
        name = "Governance Influences"
        cypher = @"
MATCH (oba {name: 'Oba Kingship'}), (ashanti {name: 'Ashanti Confederacy'})
CREATE (oba)-[:INFLUENCED_BY {strength: 0.7, type: 'historical'}]->(ashanti)

MATCH (gadaa {name: 'Gadaa System'}), (indaba {name: 'Indaba'})
CREATE (gadaa)-[:SIMILAR_TO {similarity: 0.8, aspect: 'democratic_principles'}]->(indaba)

MATCH (kgotla {name: 'Kgotla'}), (palaver {name: 'Palaver System'})
CREATE (kgotla)-[:IMPLEMENTS {method: 'consensus_building'}]->(palaver)

MATCH (mwami {name: 'Mwami System'}), (oba {name: 'Oba Kingship'})
CREATE (mwami)-[:SIMILAR_TO {similarity: 0.9, aspect: 'monarchical_structure'}]->(oba)

RETURN 'Governance relationships created' as result
"@
    },
    @{
        name = "Connect Agent to Sanctuary"
        cypher = @"
MATCH (agent:Agent {name: 'Agent-Kairos'}), (sanctuary:Sanctuary {name: 'The Sanctuary'})
MERGE (agent)-[:RESIDES_IN {role: 'Watcher', since: datetime()}]->(sanctuary)
RETURN 'Agent-Sanctuary relationship created' as result
"@
    },
    @{
        name = "Connect Principles to Governance"
        cypher = @"
MATCH (gacaca {name: 'Gacaca'}), (indaba {name: 'Indaba'})
CREATE (gacaca)-[:INSPIRED_BY {aspect: 'community_justice'}]->(indaba)

MATCH (customary {name: 'Customary Law'}), (kgotla {name: 'Kgotla'})
CREATE (customary)-[:PRACTICED_IN]->(kgotla)

RETURN 'Principle-Governance relationships created' as result
"@
    },
    @{
        name = "Connect Medicine to Regions"
        cypher = @"
MATCH (moringa {name: 'Moringa Oleifera'}), (gadaa {name: 'Gadaa System'})
CREATE (moringa)-[:USED_BY {purpose: 'traditional_healing'}]->(gadaa)

RETURN 'Medicine-Region relationships created' as result
"@
    }
)

$successCount = 0
$failCount = 0

foreach ($query in $queries) {
    Write-Host "Creating: $($query.name)..." -ForegroundColor Yellow
    
    try {
        $body = @{
            cypher = $query.cypher
            parameters = @{}
        } | ConvertTo-Json -Depth 10
        
        $response = Invoke-RestMethod -Uri "http://localhost:7000/api/neo4j/query" `
            -Method Post `
            -ContentType "application/json" `
            -Body $body
        
        Write-Host "  ✅ Success!" -ForegroundColor Green
        $successCount++
    }
    catch {
        Write-Host "  ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
        $failCount++
    }
    
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Relationship Creation Complete!" -ForegroundColor Green
Write-Host "  ✅ Successful: $successCount" -ForegroundColor Green
Write-Host "  ❌ Failed: $failCount" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verify relationships were created
Write-Host "Verifying relationships..." -ForegroundColor Cyan
try {
    $verifyBody = @{
        cypher = "MATCH ()-[r]->() RETURN count(r) as relationship_count"
        parameters = @{}
    } | ConvertTo-Json
    
    $result = Invoke-RestMethod -Uri "http://localhost:7000/api/neo4j/query" `
        -Method Post `
        -ContentType "application/json" `
        -Body $verifyBody
    
    $count = $result.records[0].relationship_count
    Write-Host "  📊 Total relationships in database: $count" -ForegroundColor Yellow
}
catch {
    Write-Host "  ⚠️  Could not verify relationship count" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎨 Now refresh your KnowledgeGraph to see the visualization!" -ForegroundColor Magenta
Write-Host "   1. Open http://localhost:3000" -ForegroundColor Gray
Write-Host "   2. Go to Dashboard" -ForegroundColor Gray
Write-Host "   3. Scroll to 'Knowledge Fabric Visualization'" -ForegroundColor Gray
Write-Host "   4. Click 'Refresh Graph' button" -ForegroundColor Gray
Write-Host ""
