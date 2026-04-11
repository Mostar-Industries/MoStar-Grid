from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

from neo4j import GraphDatabase

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class GridSemantic:
    def __init__(self, semantic_path: Path):
        self.semantic_path = semantic_path
        with open(semantic_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        self.fallback = payload.get("fallback", "Standing by.")
        self.intents = payload.get("intents", [])

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(re.findall(r"[a-z0-9']+", (value or "").lower()))

    def respond(
        self, utterance: str, mode: str = "strategic", tone: int = 3
    ) -> dict[str, Any]:
        normalized = self._normalize(utterance)
        best_intent: Optional[dict[str, Any]] = None
        best_score = 0
        for intent in self.intents:
            keywords = intent.get("keywords", [])
            score = sum(
                1 for keyword in keywords if self._normalize(keyword) in normalized
            )
            if score > best_score:
                best_intent = intent
                best_score = score
        if not best_intent:
            return {
                "intent_id": "fallback",
                "response": self.fallback,
                "mode": mode,
                "tone": tone,
                "source": str(self.semantic_path),
            }
        response_by_mode = best_intent.get("response_by_mode", {})
        response = response_by_mode.get(
            mode, best_intent.get("response", self.fallback)
        )
        return {
            "intent_id": best_intent.get("id", "fallback"),
            "response": response,
            "mode": mode,
            "tone": tone,
            "source": str(self.semantic_path),
        }


class MoStarUnifiedRuntime:
    LANGUAGE_ALIASES = {
        "en": "english",
        "english": "english",
        "ib": "ibibio",
        "ibb": "ibibio",
        "ibibio": "ibibio",
        "yo": "yoruba",
        "yoruba": "yoruba",
        "sw": "swahili",
        "swahili": "swahili",
        "ki": "swahili",
    }
    VALID_MODES = {"tactical", "strategic", "covenant"}
    DEFAULT_TONE_BY_MODE = {"tactical": 2, "strategic": 3, "covenant": 5}

    def __init__(
        self,
        semantic_path: Path,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
    ):
        self.semantic = GridSemantic(semantic_path)
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.audio_dirs = [
            PROJECT_ROOT
            / "backend"
            / "neo4j-mostar-industries"
            / "import"
            / "Ibibio_audio",
            PROJECT_ROOT
            / "backend"
            / "neo4j-mostar-industries"
            / "import"
            / "data"
            / "Ibibio_codex"
            / "Ibibio_audio",
            PROJECT_ROOT
            / "backend"
            / "neo4j-mostar-industries"
            / "data"
            / "data"
            / "Ibibio_codex"
            / "Ibibio_audio",
            PROJECT_ROOT
            / "backend"
            / "neo4j-mostar-industries"
            / "data_wired_default"
            / "data"
            / "Ibibio_codex"
            / "Ibibio_audio",
        ]
        self._ensure_schema()

    def close(self) -> None:
        self.driver.close()

    def _ensure_schema(self) -> None:
        with self.driver.session() as session:
            session.run(
                "CREATE CONSTRAINT grid_user_preference_unique IF NOT EXISTS FOR (u:GridUserPreference) REQUIRE u.user_id IS UNIQUE"
            )

    def _normalize_language(self, language: str) -> str:
        return self.LANGUAGE_ALIASES.get(
            (language or "english").strip().lower(), "english"
        )

    def _normalize_mode(self, mode: str) -> str:
        candidate = (mode or "strategic").strip().lower()
        return candidate if candidate in self.VALID_MODES else "strategic"

    def _normalize_tone(self, tone: Any, mode: str) -> int:
        try:
            value = int(tone)
        except (TypeError, ValueError):
            value = self.DEFAULT_TONE_BY_MODE[self._normalize_mode(mode)]
        return min(5, max(1, value))

    def get_user_state(self, user_id: str) -> dict[str, Any]:
        with self.driver.session() as session:
            record = session.run(
                "MATCH (u:GridUserPreference {user_id: $user_id}) RETURN properties(u) AS props",
                {"user_id": user_id},
            ).single()
        props = record["props"] if record and record["props"] else {}
        language = self._normalize_language(props.get("language", "english"))
        mode = self._normalize_mode(props.get("mode", "strategic"))
        tone = self._normalize_tone(props.get("tone"), mode)
        return {"user_id": user_id, "language": language, "mode": mode, "tone": tone}

    def update_user_state(
        self,
        user_id: str,
        *,
        language: Optional[str] = None,
        mode: Optional[str] = None,
        tone: Optional[int] = None,
    ) -> dict[str, Any]:
        current = self.get_user_state(user_id)
        resolved_language = self._normalize_language(language or current["language"])
        resolved_mode = self._normalize_mode(mode or current["mode"])
        resolved_tone = self._normalize_tone(
            tone if tone is not None else current["tone"], resolved_mode
        )
        with self.driver.session() as session:
            session.run(
                """
                MERGE (u:GridUserPreference {user_id: $user_id})
                SET u.language = $language,
                    u.mode = $mode,
                    u.tone = $tone,
                    u.updated_at = datetime()
                """,
                {
                    "user_id": user_id,
                    "language": resolved_language,
                    "mode": resolved_mode,
                    "tone": resolved_tone,
                },
            )
        return {
            "user_id": user_id,
            "language": resolved_language,
            "mode": resolved_mode,
            "tone": resolved_tone,
        }

    def _audio_path_for(self, audio_file: Optional[str]) -> Optional[str]:
        if not audio_file:
            return None
        candidate = Path(audio_file)
        if candidate.exists():
            return str(candidate.resolve())
        for audio_dir in self.audio_dirs:
            audio_path = audio_dir / candidate.name
            if audio_path.exists():
                return str(audio_path.resolve())
        return None

    def lookup_ibibio_word(self, word: str) -> Optional[dict[str, Any]]:
        with self.driver.session() as session:
            record = session.run(
                """
                MATCH (w:IbibioWord)
                WHERE toLower(w.orthography) = toLower($word)
                OPTIONAL MATCH (w)-[:HAS_AUDIO_ASSET]->(asset:AudioAsset)
                RETURN w.orthography AS orthography,
                       w.english AS english,
                       w.tone_pattern AS tone_pattern,
                       w.pos AS pos,
                       w.speaker AS speaker,
                       w.audio_file AS audio_file,
                       asset.grid_path AS grid_path,
                       asset.filename AS asset_filename
                LIMIT 1
                """,
                {"word": word},
            ).single()
        if not record:
            return None
        payload = dict(record)
        payload["native_audio_path"] = self._audio_path_for(
            payload.get("audio_file") or payload.get("asset_filename")
        )
        return payload

    def lookup_english_phrase(
        self, phrase: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        with self.driver.session() as session:
            records = session.run(
                """
                MATCH (w:IbibioWord)
                WHERE toLower(w.english) CONTAINS toLower($phrase)
                RETURN w.orthography AS orthography,
                       w.english AS english,
                       w.tone_pattern AS tone_pattern,
                       w.pos AS pos,
                       w.speaker AS speaker,
                       w.audio_file AS audio_file
                ORDER BY CASE WHEN toLower(w.english) = toLower($phrase) THEN 0 ELSE 1 END,
                         CASE WHEN w.audio_file IS NULL THEN 1 ELSE 0 END,
                         w.orthography ASC
                LIMIT $limit
                """,
                {"phrase": phrase, "limit": limit},
            ).data()
        results: list[dict[str, Any]] = []
        for row in records:
            payload = dict(row)
            payload["native_audio_path"] = self._audio_path_for(
                payload.get("audio_file")
            )
            results.append(payload)
        return results

    def covenant_audit(self) -> dict[str, Any]:
        with self.driver.session() as session:
            stats = session.run(
                """
                MATCH (w:IbibioWord)
                WITH count(w) AS total_words,
                     count(CASE WHEN w.audio_file IS NOT NULL THEN 1 END) AS words_with_audio
                OPTIONAL MATCH (m:MoStarMoment)
                RETURN total_words, words_with_audio, count(m) AS total_moments
                """
            ).single()
        total_words = int(stats["total_words"] or 0) if stats else 0
        words_with_audio = int(stats["words_with_audio"] or 0) if stats else 0
        coverage = (
            round((words_with_audio / total_words) * 100, 2) if total_words else 0.0
        )
        return {
            "truth": "online",
            "ethics": "bound",
            "culture": "active",
            "bias": "monitored",
            "ibibio_audio_coverage": coverage,
            "total_words": total_words,
            "words_with_audio": words_with_audio,
            "total_moments": int(stats["total_moments"] or 0) if stats else 0,
        }

    def _command_response(
        self, user_id: str, utterance: str
    ) -> Optional[dict[str, Any]]:
        stripped = utterance.strip()
        lowered = stripped.lower()
        if lowered.startswith("/mode "):
            state = self.update_user_state(user_id, mode=stripped.split(None, 1)[1])
            return {
                "kind": "mode_update",
                "text": f"Mode set to {state['mode']}.",
                "state": state,
            }
        if lowered.startswith("/tone "):
            try:
                tone = int(stripped.split(None, 1)[1])
            except ValueError:
                tone = None
            state = self.update_user_state(user_id, tone=tone)
            return {
                "kind": "tone_update",
                "text": f"Tone set to {state['tone']}",
                "state": state,
            }
        if lowered.startswith("/language "):
            state = self.update_user_state(user_id, language=stripped.split(None, 1)[1])
            return {
                "kind": "language_update",
                "text": f"Language set to {state['language']}.",
                "state": state,
            }
        if lowered.startswith("switch to "):
            state = self.update_user_state(
                user_id, language=stripped.split("switch to ", 1)[1]
            )
            return {
                "kind": "language_update",
                "text": f"Language set to {state['language']}.",
                "state": state,
            }
        if lowered == "/covenant audit":
            return {
                "kind": "covenant_audit",
                "text": "Covenant audit ready.",
                "audit": self.covenant_audit(),
                "state": self.get_user_state(user_id),
            }
        if lowered == "/covenant check":
            return {
                "kind": "covenant_check",
                "text": "Covenant checks passed.",
                "audit": self.covenant_audit(),
                "state": self.get_user_state(user_id),
            }
        if lowered == "/covenant seal":
            return {
                "kind": "covenant_seal",
                "text": "qseal:mo_soulprint_v2",
                "audit": self.covenant_audit(),
                "state": self.get_user_state(user_id),
            }
        return None

    def respond(self, user_id: str, utterance: str) -> dict[str, Any]:
        command = self._command_response(user_id, utterance)
        if command:
            return command
        state = self.get_user_state(user_id)
        language = state["language"]
        mode = state["mode"]
        tone = state["tone"]
        if language == "english":
            semantic = self.semantic.respond(utterance, mode=mode, tone=tone)
            return {
                "kind": "semantic_response",
                "language": language,
                "text": semantic["response"],
                "intent_id": semantic["intent_id"],
                "state": state,
            }
        if language == "ibibio":
            word_match = self.lookup_ibibio_word(utterance)
            if word_match:
                return {
                    "kind": "ibibio_word",
                    "language": language,
                    "text": word_match["orthography"],
                    "translation": word_match.get("english"),
                    "entry": word_match,
                    "state": state,
                }
            english_matches = self.lookup_english_phrase(utterance, limit=3)
            if english_matches:
                top = english_matches[0]
                return {
                    "kind": "ibibio_english_match",
                    "language": language,
                    "text": top["orthography"],
                    "translation": top.get("english"),
                    "matches": english_matches,
                    "entry": top,
                    "state": state,
                }
            return {
                "kind": "ibibio_not_found",
                "language": language,
                "text": "Amedi. Word not found in the Ibibio Grid yet.",
                "state": state,
            }
        semantic = self.semantic.respond(utterance, mode=mode, tone=tone)
        return {
            "kind": "multilingual_semantic_response",
            "language": language,
            "text": semantic["response"],
            "intent_id": semantic["intent_id"],
            "state": state,
        }
