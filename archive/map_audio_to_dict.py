"""
🔥 Map Ibibio audio files to dictionary entries
Usage: python map_audio_to_dict.py
"""

import json
import re
from pathlib import Path
from rapidfuzz import fuzz, process

# ================= CONFIGURATION =================
AUDIO_DIR = Path(r"C:\Users\idona\OneDrive - World Health Organization\Documents\Dev\MoStar-Grid\backend\neo4j-mostar-industries\import\Ibibio_audio")
DICT_JSON = Path(r"C:\Users\idona\OneDrive - World Health Organization\Documents\Dev\MoStar-Grid\backend\neo4j-mostar-industries\import\ibibio_dictionary.json")
OUTPUT_JSON = Path(r"C:\Users\idona\OneDrive - World Health Organization\Documents\Dev\MoStar-Grid\backend\neo4j-mostar-industries\import\ibibio_dictionary_with_audio.json")
MATCH_THRESHOLD = 70   # minimum fuzzy score (0-100)
# ==================================================

def extract_desc_from_filename(filename: str) -> str:
    """Extract the English description part from audio filename."""
    # Remove extension
    name = filename.stem.lower()
    
    # Remove prefixes like ibibio_5_13_MU_9_ , ibibio_Itoro-Ituen_01Jul2014-1145_
    # General pattern: anything up to last underscore before the description
    parts = name.split('_')
    # Find where the numeric/date part ends – usually after the speaker code
    # We'll take everything after the last part that contains only digits/hyphens
    desc_parts = []
    for i, part in enumerate(parts):
        # If this part looks like a date or code (e.g., "01Jul2014-1138"), skip it
        if re.match(r'^[\d\-]+$', part) or part in ['mu', 'itoro-ituen']:
            continue
        # Also skip the initial "ibibio" and numbers
        if part.isdigit() or part == 'ibibio':
            continue
        desc_parts.append(part)
    
    desc = ' '.join(desc_parts)
    # Remove trailing _a, _b, _c etc.
    desc = re.sub(r'_[a-z]$', '', desc)
    return desc

def determine_speaker(filename: str) -> str:
    """Return speaker name based on filename."""
    name = filename.stem.lower()
    if 'itoro-ituen' in name:
        return 'Itoro Ituen'
    elif 'mu' in name:
        return 'Mfon Udoinyang'
    else:
        return 'Unknown'

def load_dictionary(json_path: Path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def save_dictionary(data, json_path: Path):
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    print("🔥 Loading dictionary...")
    dict_data = load_dictionary(DICT_JSON)
    entries = dict_data['entries']
    
    # Build a list of English definitions for fuzzy matching
    choices = []
    for idx, entry in enumerate(entries):
        # Use the full English definition as the choice
        choices.append((entry['english'], idx))
    
    english_texts = [c[0] for c in choices]
    
    print(f"📁 Scanning audio files in {AUDIO_DIR}...")
    audio_files = list(AUDIO_DIR.glob("*.mp3"))
    print(f"Found {len(audio_files)} audio files.")
    
    matched = 0
    for af in audio_files:
        desc = extract_desc_from_filename(af)
        speaker = determine_speaker(af)
        
        if not desc:
            print(f"⚠️  Could not extract description from {af.name}")
            continue
        
        # Fuzzy match against all English definitions
        best_match = process.extractOne(desc, english_texts, scorer=fuzz.token_sort_ratio)
        if best_match is None:
            continue
        match_text, score, idx = best_match[0], best_match[1], choices[best_match[2]][1]
        
        if score >= MATCH_THRESHOLD:
            entry = entries[idx]
            # Optionally double-check speaker consistency
            if entry['speaker'] != speaker:
                print(f"⚠️  Speaker mismatch for {af.name}: dict says {entry['speaker']}, file suggests {speaker}. Using file speaker.")
                # Update the entry's speaker to match the file? Or keep dict? We'll keep dict as source of truth, but audio file speaker may be more accurate.
                # Here we assume the file is correct, so we update the entry's speaker.
                entry['speaker'] = speaker
            
            if entry['audio_file']:
                print(f"⚠️  Entry {entry['ibibio']} already has audio {entry['audio_file']}, replacing with {af.name}")
            entry['audio_file'] = af.name
            matched += 1
            print(f"✅ {af.name} → {entry['ibibio']} (score {score})")
        else:
            print(f"❌ No good match for {af.name} (best: '{match_text}' score {score})")
    
    print(f"\n🎯 Matched {matched} audio files to dictionary entries.")
    
    # Update metadata
    dict_data['metadata']['entries_with_audio'] = sum(1 for e in entries if e.get('audio_file'))
    dict_data['metadata']['speakers'] = list(set(e['speaker'] for e in entries if e.get('speaker')))
    
    save_dictionary(dict_data, OUTPUT_JSON)
    print(f"💾 Updated dictionary saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
