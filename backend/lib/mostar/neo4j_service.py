from backend.lib.neo4j_connector import run_cypher_query

def get_context_for_prompt(prompt):
    cypher = """
    MATCH (n)-[r]->(m)
    WHERE toLower(n.name) CONTAINS toLower($term) OR toLower(m.name) CONTAINS toLower($term)
    RETURN n.name AS from, type(r) AS rel, m.name AS to, n.runbook_url AS from_url, m.runbook_url AS to_url
    LIMIT 10
    """
    term = prompt.strip()
    result = run_cypher_query(cypher, {"term": term})
    
    context_lines = [
        f"{r['from']} ({r['from_url']}) --[{r['rel']}]--> {r['to']} ({r['to_url']})"
        for r in result
    ]
    return "\n".join(context_lines)
