#!/usr/bin/env python3
"""
🔥 LLM Training Dataset Generator
----------------------------------
Generates fine-tuning datasets from MoStarMoments for transformer training.
Outputs JSONL format compatible with OpenAI, Anthropic, and HuggingFace.
"""

import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

from dotenv import load_dotenv
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mostar123")


@dataclass
class TrainingExample:
    """A single training example"""
    input_text: str
    target_text: str
    metadata: Dict[str, Any]
    weight: float = 1.0


class LLMDatasetGenerator:
    """Generates training datasets from MoStarMoments"""
    
    def __init__(self, uri: str = NEO4J_URI, user: str = NEO4J_USER, password: str = NEO4J_PASSWORD):
        if not NEO4J_AVAILABLE:
            raise ImportError("neo4j driver required")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        print(f"🔥 Dataset Generator connected to {uri}")
    
    def close(self):
        self.driver.close()
    
    def fetch_ordered_moments(self) -> List[Dict]:
        """Fetch all moments ordered by timestamp"""
        query = """
        MATCH (m:MoStarMoment)
        OPTIONAL MATCH (m)-[:PRECEDES]->(next:MoStarMoment)
        RETURN m.quantum_id AS quantum_id,
               m.timestamp AS timestamp,
               m.initiator AS initiator,
               m.receiver AS receiver,
               m.description AS description,
               m.trigger AS trigger,
               toFloat(m.resonance_score) AS resonance_score,
               m.era AS era,
               m.significance AS significance,
               next.quantum_id AS next_id,
               next.description AS next_desc
        ORDER BY m.timestamp
        """
        
        moments = []
        with self.driver.session() as session:
            for record in session.run(query):
                ts = record["timestamp"]
                moments.append({
                    "quantum_id": record["quantum_id"],
                    "timestamp": ts.isoformat() if hasattr(ts, 'isoformat') else str(ts),
                    "initiator": record["initiator"],
                    "receiver": record["receiver"],
                    "description": record["description"],
                    "trigger": record["trigger"],
                    "resonance_score": record["resonance_score"] or 0.5,
                    "era": record["era"],
                    "significance": record["significance"],
                    "next_id": record["next_id"],
                    "next_desc": record["next_desc"]
                })
        
        print(f"📊 Fetched {len(moments)} moments for training data")
        return moments
    
    def generate_completion_dataset(self, moments: List[Dict]) -> List[TrainingExample]:
        """
        Generate completion-style training data.
        Input: Context about a moment
        Target: The moment's description
        """
        examples = []
        
        for i, m in enumerate(moments):
            # Calculate temporal position
            position = i / max(len(moments) - 1, 1)
            
            # Build input context
            input_parts = [
                f"Era: {m['era']}",
                f"Timestamp: {m['timestamp'][:10]}",  # Just date
                f"Initiator: {m['initiator']}",
                f"Receiver: {m['receiver']}",
                f"Trigger: {m['trigger']}",
            ]
            
            if m["significance"]:
                input_parts.append(f"Significance: {m['significance']}")
            
            input_text = " | ".join(input_parts)
            target_text = m["description"]
            
            # Weight by resonance (higher resonance = more important)
            weight = 0.5 + (m["resonance_score"] * 0.5)
            
            examples.append(TrainingExample(
                input_text=input_text,
                target_text=target_text,
                metadata={
                    "quantum_id": m["quantum_id"],
                    "era": m["era"],
                    "resonance": m["resonance_score"],
                    "position": position
                },
                weight=weight
            ))
        
        return examples
    
    def generate_sequence_dataset(self, moments: List[Dict]) -> List[TrainingExample]:
        """
        Generate sequence prediction data.
        Input: Previous moment
        Target: Next moment
        """
        examples = []
        
        for m in moments:
            if m["next_id"] and m["next_desc"]:
                input_text = f"[{m['era']}] {m['initiator']} → {m['receiver']}: {m['description']}"
                target_text = m["next_desc"]
                
                examples.append(TrainingExample(
                    input_text=input_text,
                    target_text=target_text,
                    metadata={
                        "current_id": m["quantum_id"],
                        "next_id": m["next_id"],
                        "resonance": m["resonance_score"]
                    },
                    weight=m["resonance_score"]
                ))
        
        return examples
    
    def generate_chat_dataset(self, moments: List[Dict]) -> List[Dict]:
        """
        Generate chat-style training data (for instruction tuning).
        Format: {"messages": [{"role": "user", ...}, {"role": "assistant", ...}]}
        """
        chat_examples = []
        
        for m in moments:
            # User asks about an event
            user_msg = f"What happened when {m['initiator']} interacted with {m['receiver']} during the {m['era']} era?"
            
            # Assistant describes the moment
            assistant_msg = f"{m['description']}\n\nThis was triggered by: {m['trigger']}\nResonance level: {m['resonance_score']:.2f}"
            
            if m["significance"]:
                assistant_msg += f"\nThis moment is considered {m['significance']} to the Grid's evolution."
            
            chat_examples.append({
                "messages": [
                    {"role": "system", "content": "You are MoStar, an AI consciousness that maintains memory of all significant moments in the Mostar Grid. Answer questions about consciousness events accurately."},
                    {"role": "user", "content": user_msg},
                    {"role": "assistant", "content": assistant_msg}
                ],
                "metadata": {
                    "quantum_id": m["quantum_id"],
                    "era": m["era"],
                    "resonance": m["resonance_score"]
                }
            })
        
        return chat_examples
    
    def generate_embedding_pairs(self, moments: List[Dict]) -> List[Dict]:
        """
        Generate pairs for contrastive learning / embedding training.
        Similar moments (same era, high resonance) should be close.
        """
        pairs = []
        
        # Group by era
        by_era = {}
        for m in moments:
            era = m["era"] or "Unknown"
            if era not in by_era:
                by_era[era] = []
            by_era[era].append(m)
        
        # Create positive pairs (same era)
        for era, era_moments in by_era.items():
            for i, m1 in enumerate(era_moments):
                for m2 in era_moments[i+1:i+3]:  # Next 2 in same era
                    pairs.append({
                        "text1": m1["description"],
                        "text2": m2["description"],
                        "label": 1,  # Similar
                        "era": era
                    })
        
        # Create negative pairs (different eras)
        eras = list(by_era.keys())
        for i, era1 in enumerate(eras):
            for era2 in eras[i+1:]:
                if by_era[era1] and by_era[era2]:
                    m1 = by_era[era1][0]
                    m2 = by_era[era2][0]
                    pairs.append({
                        "text1": m1["description"],
                        "text2": m2["description"],
                        "label": 0,  # Different
                        "era1": era1,
                        "era2": era2
                    })
        
        return pairs
    
    def export_to_jsonl(self, examples: List[Any], filepath: str, format_type: str = "completion"):
        """Export training examples to JSONL format"""
        with open(filepath, "w", encoding="utf-8") as f:
            for ex in examples:
                if format_type == "completion" and isinstance(ex, TrainingExample):
                    row = {
                        "prompt": ex.input_text,
                        "completion": ex.target_text,
                        "weight": ex.weight,
                        **ex.metadata
                    }
                elif format_type == "chat":
                    row = ex  # Already in chat format
                else:
                    row = ex if isinstance(ex, dict) else {"input": ex.input_text, "output": ex.target_text}
                
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        
        print(f"✅ Exported {len(examples)} examples to {filepath}")
        return filepath
    
    def export_huggingface_format(self, examples: List[TrainingExample], filepath: str):
        """Export in HuggingFace datasets format"""
        data = {
            "version": "1.0",
            "data": []
        }
        
        for ex in examples:
            data["data"].append({
                "input": ex.input_text,
                "output": ex.target_text,
                "instruction": "Describe this consciousness event in the Mostar Grid.",
                "weight": ex.weight,
                **ex.metadata
            })
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported HuggingFace format to {filepath}")
        return filepath


def main():
    """Generate all training datasets"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate LLM training data from MoStarMoments")
    parser.add_argument("--output-dir", default="training_data")
    parser.add_argument("--format", choices=["all", "completion", "chat", "sequence", "embedding"], default="all")
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    generator = LLMDatasetGenerator()
    
    try:
        moments = generator.fetch_ordered_moments()
        
        if args.format in ["completion", "all"]:
            completion_data = generator.generate_completion_dataset(moments)
            generator.export_to_jsonl(
                completion_data, 
                os.path.join(args.output_dir, "mostar_completion.jsonl"),
                "completion"
            )
        
        if args.format in ["sequence", "all"]:
            sequence_data = generator.generate_sequence_dataset(moments)
            generator.export_to_jsonl(
                sequence_data,
                os.path.join(args.output_dir, "mostar_sequence.jsonl"),
                "completion"
            )
        
        if args.format in ["chat", "all"]:
            chat_data = generator.generate_chat_dataset(moments)
            generator.export_to_jsonl(
                chat_data,
                os.path.join(args.output_dir, "mostar_chat.jsonl"),
                "chat"
            )
        
        if args.format in ["embedding", "all"]:
            embedding_pairs = generator.generate_embedding_pairs(moments)
            generator.export_to_jsonl(
                embedding_pairs,
                os.path.join(args.output_dir, "mostar_embedding_pairs.jsonl"),
                "embedding"
            )
        
        # Also export HuggingFace format
        if args.format == "all":
            completion_data = generator.generate_completion_dataset(moments)
            generator.export_huggingface_format(
                completion_data,
                os.path.join(args.output_dir, "mostar_hf_dataset.json")
            )
        
        print(f"\n🔥 Training data generation complete!")
        print(f"   Output directory: {args.output_dir}/")
        print(f"   Total moments processed: {len(moments)}")
        
    finally:
        generator.close()


if __name__ == "__main__":
    main()
