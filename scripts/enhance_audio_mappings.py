from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

STOPWORDS = {
    "a",
    "an",
    "the",
    "of",
    "to",
    "and",
    "or",
    "for",
    "in",
    "on",
    "at",
    "by",
    "with",
    "from",
    "into",
    "as",
    "when",
    "what",
    "who",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "be",
    "become",
    "someone",
    "something",
    "kind",
    "used",
    "very",
    "var",
    "rev",
    "up",
    "down",
    "out",
    "over",
    "under",
    "off",
    "person",
    "people",
    "object",
    "objects",
    "this",
    "is",
    "it",
    "only",
}


def _normalize_text(value: str | None) -> str:
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", value)
    normalized = normalized.encode("ascii", "ignore").decode("ascii").lower()
    normalized = normalized.replace("&", " and ").replace("8217", "")
    normalized = normalized.replace("immitate", "imitate")
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return " ".join(normalized.split())


def _tokenize_significant(value: str | None) -> list[str]:
    return [
        token
        for token in _normalize_text(value).split()
        if len(token) > 2 and token not in STOPWORDS
    ]


def _speaker_code(value: str | None) -> str:
    normalized = (value or "").lower()
    if "mfon" in normalized:
        return "MU"
    if "itoro" in normalized:
        return "II"
    return ""


def _audio_speaker_code(filename: str) -> str:
    normalized = filename.lower()
    if (
        "mfon-udoinyang" in normalized
        or "_mu_" in normalized
        or normalized.startswith("ibibio16_mu")
        or normalized.startswith("ibibio17_mu")
        or normalized.startswith("ibibio18_mu")
    ):
        return "MU"
    if "itoro-ituen" in normalized or "itoro_ituen" in normalized:
        return "II"
    return ""


def _extract_audio_gloss(filename: str) -> str:
    normalized = _normalize_text(Path(filename).stem)
    normalized = re.sub(
        r"^ibibio mfon udoinyang \d{2}[a-z]{3}\d{4} \d{4} ",
        "",
        normalized,
    )
    normalized = re.sub(
        r"^ibibio itoro ituen \d{2}[a-z]{3}\d{4} \d{4} ",
        "",
        normalized,
    )
    normalized = re.sub(r"^ibibio16 mu \d+ ", "", normalized)
    normalized = re.sub(r"^ibibio17 mu \d+ ", "", normalized)
    normalized = re.sub(r"^ibibio18 mu \d+ ", "", normalized)
    normalized = re.sub(r"^ibibio 5 13 mu \d+ ", "", normalized)
    normalized = re.sub(r"^ls100019 ibibio mu ", "", normalized)
    normalized = re.sub(r"^ls100020 ibibio mu ", "", normalized)
    normalized = re.sub(r"\bvar\b.*$", "", normalized).strip()
    normalized = re.sub(r"\brev\b.*$", "", normalized).strip()
    normalized = re.sub(r"\b[a-d]\b$", "", normalized).strip()
    return normalized


def _ordered_subset(needle: list[str], haystack: list[str]) -> bool:
    position = 0
    for token in needle:
        try:
            next_index = haystack.index(token, position)
        except ValueError:
            return False
        position = next_index + 1
    return True


def _eligible_entries(
    entries: list[dict], audio_speaker: str
) -> list[tuple[int, dict]]:
    eligible = []
    for index, entry in enumerate(entries):
        if entry.get("audio_file"):
            continue
        entry_speaker = _speaker_code(entry.get("speaker"))
        if audio_speaker and entry_speaker and audio_speaker != entry_speaker:
            continue
        eligible.append((index, entry))
    return eligible


def _find_candidates(entries: list[dict], filename: str) -> list[tuple[int, int]]:
    audio_gloss = _extract_audio_gloss(filename)
    audio_tokens = _tokenize_significant(audio_gloss)
    if not audio_tokens:
        return []
    audio_speaker = _audio_speaker_code(filename)
    eligible = _eligible_entries(entries, audio_speaker)
    first_token_candidates = [
        entry_index
        for entry_index, entry in eligible
        if _tokenize_significant(entry.get("english"))
        and _tokenize_significant(entry.get("english"))[0] == audio_tokens[0]
    ]
    candidates: list[tuple[int, int]] = []
    for entry_index, entry in eligible:
        english_norm = _normalize_text(entry.get("english"))
        english_tokens = _tokenize_significant(entry.get("english"))
        if not english_tokens:
            continue
        if english_norm == audio_gloss:
            candidates.append((3, entry_index))
            continue
        if len(audio_tokens) >= 2 and _ordered_subset(audio_tokens, english_tokens):
            candidates.append((2, entry_index))
            continue
        if len(audio_tokens) == 1 and len(first_token_candidates) == 1:
            if english_tokens[0] == audio_tokens[0]:
                candidates.append((1, entry_index))
    return candidates


def enhance_dictionary(json_path: Path, audio_dir: Path, output_path: Path) -> dict:
    with json_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    entries = data["entries"]
    existing_audio_count = sum(1 for entry in entries if entry.get("audio_file"))
    assignments_by_entry: dict[int, list[tuple[int, str]]] = {}
    for audio_path in sorted(audio_dir.glob("*.mp3")):
        candidates = _find_candidates(entries, audio_path.name)
        if not candidates:
            continue
        best_level = max(level for level, _ in candidates)
        best_entry_indexes = [
            entry_index for level, entry_index in candidates if level == best_level
        ]
        if len(best_entry_indexes) != 1:
            continue
        entry_index = best_entry_indexes[0]
        assignments_by_entry.setdefault(entry_index, []).append(
            (best_level, audio_path.name)
        )
    added = 0
    for entry_index, matches in assignments_by_entry.items():
        matches.sort(key=lambda item: (-item[0], item[1]))
        chosen_filename = matches[0][1]
        if entries[entry_index].get("audio_file"):
            continue
        entries[entry_index]["audio_file"] = chosen_filename
        added += 1
    metadata = data.setdefault("metadata", {})
    metadata["entries_with_audio"] = sum(
        1 for entry in entries if entry.get("audio_file")
    )
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return {
        "existing_audio_count": existing_audio_count,
        "added_audio_count": added,
        "final_audio_count": metadata["entries_with_audio"],
        "output_path": str(output_path),
    }


def main() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    import_dir = backend_dir / "neo4j-mostar-industries" / "import"
    json_path = import_dir / "ibibio_dictionary_with_audio.json"
    audio_dir = import_dir / "Ibibio_audio"
    output_path = import_dir / "ibibio_dictionary_enhanced.json"
    if not json_path.exists():
        raise SystemExit(f"Dictionary not found: {json_path}")
    if not audio_dir.exists():
        raise SystemExit(f"Audio directory not found: {audio_dir}")
    summary = enhance_dictionary(json_path, audio_dir, output_path)
    print("🎧 IBIBIO AUDIO ENHANCEMENT")
    print(f"   existing_audio_count: {summary['existing_audio_count']}")
    print(f"   added_audio_count: {summary['added_audio_count']}")
    print(f"   final_audio_count: {summary['final_audio_count']}")
    print(f"   output_path: {summary['output_path']}")


if __name__ == "__main__":
    main()
