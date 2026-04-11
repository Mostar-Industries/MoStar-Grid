// Additional moments formatted to match existing mo_star_moment() structure

mo_star_moment(
    initiator="User",
    receiver="TsaTse Fly",
    description="Kickoff: MoStar Grid mind graph design - Established scope to model MoStar moments; requested full memory; constraints noted (no cross-session memory).",
    trigger_type="milestone",
    resonance_score=4.8,
    context_notes=[
        "Date: 2026-01-04",
        "Kind: milestone",
        "Title: MoStar Grid mind graph design",
        "Narrative: Established scope to model MoStar moments; requested full memory; constraints noted (no cross-session memory)",
        "Confidence: High",
        "Impact: 3",
        "Tags: setup|neo4j|design",
        "Actors: user|TsaTse Fly",
        "Projects: MoStar Grid",
        "Metadata: source=session",
        "Moment ID: MM_372cf7516e"
    ],
    approved=True,
),

mo_star_moment(
    initiator="User",
    receiver="TsaTse Fly",
    description="Delivered bootstrap pack (Python registry + Neo4j Cypher) - Provided Mostar_Moment.py and neo4j schema/import pack via canvas.",
    trigger_type="build",
    resonance_score=4.9,
    context_notes=[
        "Date: 2026-01-04",
        "Kind: build",
        "Title: Delivered bootstrap pack",
        "Narrative: Provided Mostar_Moment.py and neo4j schema/import pack via canvas",
        "Confidence: High",
        "Impact: 4",
        "Tags: build|python|cypher",
        "Actors: user|TsaTse Fly",
        "Projects: MoStar Grid",
        "Metadata: delivery=canvas",
        "Moment ID: MM_cc0de9e904"
    ],
    approved=True,
),

mo_star_moment(
    initiator="User",
    receiver="MoStar Grid",
    description="Imported DCP corpus (PDFs) - Ingested 7 DCP PDFs into workspace for potential linkage to health-sovereignty tracks.",
    trigger_type="ingest",
    resonance_score=4.2,
    context_notes=[
        "Date: 2026-01-04",
        "Kind: ingest",
        "Title: Imported DCP corpus (PDFs)",
        "Narrative: Ingested 7 DCP PDFs into workspace for potential linkage to health-sovereignty tracks",
        "Confidence: Medium",
        "Impact: 2",
        "Tags: assets|health|DCP",
        "Actors: user",
        "Projects: MoStar Grid",
        "Files: dcp-cholera.pdf|dcp-ebola.pdf|dcp-lassafever.pdf|dcp-marburg.pdf|dcp-sars.pdf|dcp-yellowfever.pdf|mpox-dcp-v3.2.pdf",
        "Metadata: zip=DCP.zip",
        "Moment ID: MM_712c62f754"
    ],
    approved=True,
),

// Relationship moments (converted to separate moments for relationship tracking)
mo_star_moment(
    initiator="MM_372cf7516e",
    receiver="MM_cc0de9e904",
    description="PRECEDES relationship: Design kickoff precedes bootstrap delivery - why=deliver_bootstrap",
    trigger_type="relationship",
    resonance_score=4.5,
    context_notes=[
        "Relationship: PRECEDES",
        "Source: MM_372cf7516e (design kickoff)",
        "Target: MM_cc0de9e904 (bootstrap delivery)",
        "Reason: deliver_bootstrap",
        "Type: temporal_sequence"
    ],
    approved=True,
),

mo_star_moment(
    initiator="MM_cc0de9e904",
    receiver="MM_712c62f754",
    description="RELATES_TO relationship: Bootstrap delivery relates to DCP import - note=assets_available",
    trigger_type="relationship",
    resonance_score=4.3,
    context_notes=[
        "Relationship: RELATES_TO",
        "Source: MM_cc0de9e904 (bootstrap delivery)",
        "Target: MM_712c62f754 (DCP import)",
        "Note: assets_available",
        "Type: logical_connection"
    ],
    approved=True,
),
