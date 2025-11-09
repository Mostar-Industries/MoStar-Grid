from fastapi import APIRouter, Request, HTTPException
import requests
import logging
from server.neo4j_client import get_neo4j_client

router = APIRouter(prefix="/api", tags=["chat"])
logger = logging.getLogger("grid.chat")

OLLAMA_URL = "http://localhost:11434/api/generate"  # Ollama or local LLaMA server

def get_context_for_prompt(prompt: str) -> str:
    """Fetch relevant context from Neo4j based on prompt keywords"""
    neo4j = get_neo4j_client()
    
    if not neo4j.is_connected:
        logger.warning("Neo4j not connected, returning empty context")
        return ""
    
    try:
        cypher = """
        MATCH (n)-[r]->(m)
        WHERE toLower(n.name) CONTAINS toLower($term) 
           OR toLower(m.name) CONTAINS toLower($term)
           OR toLower(type(r)) CONTAINS toLower($term)
        RETURN n.name AS from, 
               type(r) AS rel, 
               m.name AS to, 
               n.runbook_url AS from_url, 
               m.runbook_url AS to_url,
               n.region AS region,
               n.type AS type
        LIMIT 10
        """
        
        result = neo4j.execute_query(cypher, {"term": prompt.strip()})
        
        if not result:
            return "No specific context found in the knowledge graph."
        
        context_lines = []
        for r in result:
            line = f"{r.get('from', 'Unknown')} --[{r.get('rel', 'RELATES_TO')}]--> {r.get('to', 'Unknown')}"
            if r.get('region'):
                line += f" (Region: {r['region']})"
            if r.get('from_url'):
                line += f" | {r['from_url']}"
            context_lines.append(line)
        
        return "\n".join(context_lines)
    except Exception as e:
        logger.error(f"Error fetching context: {e}")
        return ""

@router.post("/chat")
async def chat(request: Request):
    """
    Chat endpoint that enriches prompts with Neo4j context and sends to local LLM
    """
    try:
        data = await request.json()
        prompt = data.get("prompt", "")
        
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        logger.info(f"Chat request: {prompt[:50]}...")
        
        # Fetch context from Neo4j
        context = get_context_for_prompt(prompt)
        
        # Build enriched prompt
        system_context = """You are MostarAI, an AI assistant specializing in African knowledge systems, 
governance structures, traditional medicine, and cultural practices. You have access to a knowledge graph 
containing information about African governance systems (like Oba Kingship, Gadaa, Ashanti Confederacy), 
traditional medicine (Moringa, Artemisia), spiritual practices (Ifá, Orisha), and principles (Ubuntu, Gacaca).

Answer questions based on the provided context from the knowledge graph. Be respectful, informative, and 
acknowledge the depth of African wisdom traditions."""

        if context:
            enriched_prompt = f"{system_context}\n\nKnowledge Graph Context:\n{context}\n\nUser Question: {prompt}\n\nAnswer:"
        else:
            enriched_prompt = f"{system_context}\n\nUser Question: {prompt}\n\nAnswer:"
        
        # Call Ollama using /api/chat endpoint (proper format with messages)
        payload = {
            "model": "mistral",  # or llama3, dolphin-mixtral, etc.
            "messages": [
                {"role": "user", "content": enriched_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        logger.info("Sending request to Ollama...")
        ollama_chat_url = "http://localhost:11434/api/chat"
        response = requests.post(ollama_chat_url, json=payload, timeout=60)
        
        if response.status_code != 200:
            logger.error(f"Ollama error: {response.status_code} - {response.text}")
            raise HTTPException(
                status_code=503, 
                detail="LLM service unavailable. Make sure Ollama is running: ollama run mistral"
            )
        
        result = response.json()
        logger.info("Got response from Ollama")
        
        # Extract message content from Ollama's chat response
        message_content = ""
        if "message" in result:
            message_content = result["message"].get("content", "")
        else:
            # Fallback for generate endpoint
            message_content = result.get("response", "")
        
        return {
            "response": message_content,
            "context_used": bool(context),
            "model": payload["model"]
        }
        
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Ollama")
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to Ollama. Start it with: ollama run mistral"
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
