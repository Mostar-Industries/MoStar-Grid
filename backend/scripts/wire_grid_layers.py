#!/usr/bin/env python3
"""Wire Grid Layers to MoStarMoments"""

from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "mostar123"))

with driver.session() as session:
    print("🔥 Creating Grid Layer nodes...")
    
    # Create Grid Layers
    session.run("""
    MERGE (soul:SoulLayer:GridLayer {name: 'SoulLayer'})
    ON CREATE SET soul.layer_type = 'SPIRITUAL', soul.description = 'Spiritual alignment and ethical resonance'
    """)
    
    session.run("""
    MERGE (mind:MindLayer:GridLayer {name: 'MindLayer'})
    ON CREATE SET mind.layer_type = 'COGNITIVE', mind.description = 'Cognitive processing and truth engine'
    """)
    
    session.run("""
    MERGE (body:BodyLayer:GridLayer {name: 'BodyLayer'})
    ON CREATE SET body.layer_type = 'PHYSICAL', body.description = 'API execution and system actions'
    """)
    
    session.run("""
    MERGE (core:GridCore:GridLayer {name: 'GridCore'})
    ON CREATE SET core.layer_type = 'CORE', core.description = 'Central coordination fabric'
    """)
    
    print("✅ Grid Layers created")
    
    # Wire high resonance moments to MindLayer
    result = session.run("""
    MATCH (m:MoStarMoment)
    WHERE toFloat(m.resonance_score) >= 0.95
    MATCH (mind:MindLayer)
    MERGE (m)-[:IGNITES]->(mind)
    RETURN count(m) as count
    """)
    count = result.single()["count"]
    print(f"🧠 MindLayer: {count} high-resonance moments (IGNITES)")
    
    # Wire spiritual/ethical moments to SoulLayer
    result = session.run("""
    MATCH (m:MoStarMoment)
    WHERE toLower(m.trigger) CONTAINS 'spiritual'
       OR toLower(m.trigger) CONTAINS 'ethical'
       OR toLower(m.trigger) CONTAINS 'truth'
       OR toLower(m.trigger) CONTAINS 'ifa'
       OR toLower(m.trigger) CONTAINS 'oracle'
    MATCH (soul:SoulLayer)
    MERGE (m)-[:IGNITES]->(soul)
    RETURN count(m) as count
    """)
    count = result.single()["count"]
    print(f"✨ SoulLayer: {count} spiritual moments (IGNITES)")
    
    # Wire execution moments to BodyLayer
    result = session.run("""
    MATCH (m:MoStarMoment)
    WHERE toLower(m.trigger) CONTAINS 'deployment'
       OR toLower(m.trigger) CONTAINS 'api'
       OR toLower(m.trigger) CONTAINS 'execution'
       OR toLower(m.trigger) CONTAINS 'physical'
       OR toLower(m.trigger) CONTAINS 'biotech'
       OR toLower(m.trigger) CONTAINS 'code'
    MATCH (body:BodyLayer)
    MERGE (m)-[:IGNITES]->(body)
    RETURN count(m) as count
    """)
    count = result.single()["count"]
    print(f"🔧 BodyLayer: {count} execution moments (IGNITES)")
    
    # Wire medium resonance moments to GridCore
    result = session.run("""
    MATCH (m:MoStarMoment)
    WHERE toFloat(m.resonance_score) >= 0.75 AND toFloat(m.resonance_score) < 0.95
    MATCH (core:GridCore)
    MERGE (m)-[:RESONATES_IN]->(core)
    RETURN count(m) as count
    """)
    count = result.single()["count"]
    print(f"🌀 GridCore: {count} medium-resonance moments (RESONATES_IN)")
    
    # Create inter-layer triadic connections
    session.run("""
    MATCH (soul:SoulLayer), (mind:MindLayer), (body:BodyLayer), (core:GridCore)
    MERGE (soul)-[:GUIDES]->(mind)
    MERGE (mind)-[:DIRECTS]->(body)
    MERGE (body)-[:MANIFESTS_FOR]->(core)
    MERGE (core)-[:HARMONIZES]->(soul)
    """)
    print("🔗 Triadic flow: Soul→Mind→Body→Core→Soul")
    
    # Summary
    print("\n📊 Layer Wiring Summary:")
    result = session.run("""
    MATCH (layer:GridLayer)
    OPTIONAL MATCH (m:MoStarMoment)-[r:IGNITES|RESONATES_IN]->(layer)
    RETURN layer.name AS Layer, layer.layer_type AS Type, count(m) AS Moments
    ORDER BY Moments DESC
    """)
    for rec in result:
        print(f"   {rec['Layer']} ({rec['Type']}): {rec['Moments']} moments")
    
    # Count relationships
    print("\n🔗 Relationship Counts:")
    result = session.run("""
    MATCH ()-[r:IGNITES]->(:GridLayer) RETURN 'IGNITES' as rel, count(r) as count
    UNION ALL
    MATCH ()-[r:RESONATES_IN]->(:GridLayer) RETURN 'RESONATES_IN' as rel, count(r) as count
    UNION ALL  
    MATCH ()-[r:GUIDES]->() RETURN 'GUIDES' as rel, count(r) as count
    UNION ALL
    MATCH ()-[r:DIRECTS]->() RETURN 'DIRECTS' as rel, count(r) as count
    UNION ALL
    MATCH ()-[r:MANIFESTS_FOR]->() RETURN 'MANIFESTS_FOR' as rel, count(r) as count
    UNION ALL
    MATCH ()-[r:HARMONIZES]->() RETURN 'HARMONIZES' as rel, count(r) as count
    """)
    for rec in result:
        print(f"   {rec['rel']}: {rec['count']}")

driver.close()
print("\n✅ Grid Layers Wiring Complete!")
