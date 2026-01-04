import json
import os
from typing import List, Dict, Any
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Configuration
JSON_SOURCE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'exports', 'activation_subgraph.json')
STORE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'memory_store')
MODEL_NAME = "all-MiniLM-L6-v2"

def load_moments(json_path: str) -> List[Dict[str, Any]]:
    """Load MoStarMoments from the JSON export."""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Source file not found: {json_path}")
        
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    moments = [
        node for node in data.get("nodes", []) 
        if node.get("type") == "MoStarMoment"
    ]
    return moments

def create_documents(moments: List[Dict[str, Any]]) -> List[Document]:
    """Convert moments to LangChain Documents."""
    docs = []
    for m in moments:
        data = m.get("data", {})
        
        # Construct a rich semantic representation
        content = (
            f"Moment: {data.get('description', 'Unknown Event')}\n"
            f"Era: {data.get('era', 'Unknown')}\n"
            f"Resonance: {data.get('resonance', 0.0)}\n"
            f"Initiator: {data.get('initiator', 'Unknown')}\n"
            f"Receiver: {data.get('receiver', 'Unknown')}"
        )
        
        # Metadata for filtering and context
        metadata = {
            "id": m.get("id"),
            "timestamp": data.get("timestamp"),
            "era": data.get("era"),
            "resonance": data.get("resonance"),
            "type": "MoStarMoment"
        }
        
        docs.append(Document(page_content=content, metadata=metadata))
    return docs

def ingest_memory():
    """Main ingestion process."""
    print(f"📂 Loading moments from {JSON_SOURCE}...")
    moments = load_moments(JSON_SOURCE)
    print(f"   Found {len(moments)} moments.")
    
    print("📄 Converting to documents...")
    docs = create_documents(moments)
    
    print(f"🧠 Initializing embeddings ({MODEL_NAME})...")
    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    
    print("🏗️  Building FAISS index...")
    vectorstore = FAISS.from_documents(docs, embeddings)
    
    print(f"💾 Saving to {STORE_PATH}...")
    os.makedirs(STORE_PATH, exist_ok=True)
    vectorstore.save_local(STORE_PATH)
    
    print("✅ Memory ingestion complete.")

if __name__ == "__main__":
    ingest_memory()
