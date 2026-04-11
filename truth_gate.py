# ═══════════════════════════════════════════════════════════════════
# TRUTH GATE — THE FOUR-ELEMENT VERIFICATION ENGINE
# moscript://codex/v1
# ═══════════════════════════════════════════════════════════════════
#
# Nothing enters the Grid unverified.
# Nothing leaves the Grid unjudged.
#
# The Truth Gate maps signal verification to the four Ibibio elements.
# Each element governs a signal domain. Each has a floor.
# If a signal cannot meet its element's floor, it does not pass.
# If no Fire signal passes, the engine does not activate — period.
#
# Element  │ Ibibio  │ Domain              │ Floor
# ─────────┼─────────┼─────────────────────┼───────
# 🜂 Fire   │ Ikang   │ Disease signals      │ 0.75
# 🜄 Water  │ Mmọng   │ Displacement flows   │ 0.70
# 🜁 Air    │ Afim    │ Conflict events      │ 0.65
# 🜃 Earth  │ Isong   │ Terrain / linguistic │ 0.80
#
# Why these floors?
# Fire is high (0.75) because disease claims kill people if wrong.
# Water is moderate (0.70) because displacement is observable but noisy.
# Air is lowest (0.65) because conflict data is inherently contested.
# Earth is highest (0.80) because terrain and language don't lie —
#   if they score low, the data source is corrupt, not the ground.
#
# ═══════════════════════════════════════════════════════════════════

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
import hashlib
import json


# ── Elements ──────────────────────────────────────────────────────

class Element(Enum):
    """The four Ibibio elements that govern signal truth."""
    FIRE  = ("ikang",  "🜂", 0.75, "disease")
    WATER = ("mmoong", "🜄", 0.70, "displacement")
    AIR   = ("afim",   "🜁", 0.65, "conflict")
    EARTH = ("isong",  "🜃", 0.80, "terrain")

    def __init__(self, ibibio: str, sigil: str, floor: float, domain: str):
        self.ibibio = ibibio
        self.sigil = sigil
        self.floor = floor
        self.domain = domain


# ── Signal ────────────────────────────────────────────────────────

@dataclass
class Signal:
    """A single intelligence signal entering the Gate."""
    id: str
    source: str                    # e.g. "acled", "afro_sentinel", "iom_dtm"
    element: Element
    raw_confidence: float          # source-reported confidence [0, 1]
    timestamp: datetime
    payload: dict                  # the actual data
    provenance: str = ""           # URL, API endpoint, or file path
    corroborating_sources: int = 0 # how many independent sources confirm

    @property
    def fingerprint(self) -> str:
        """Deterministic identity — same signal always same hash."""
        content = f"{self.source}:{self.element.name}:{json.dumps(self.payload, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


# ── Trust Computation ─────────────────────────────────────────────

@dataclass
class TrustScore:
    """The computed trust of a signal after Gate evaluation."""
    signal_id: str
    element: Element
    raw: float
    adjusted: float
    passed: bool
    penalties: List[str] = field(default_factory=list)
    bonuses: List[str] = field(default_factory=list)

    @property
    def margin(self) -> float:
        """How far above or below the floor."""
        return self.adjusted - self.element.floor


def compute_trust(signal: Signal) -> TrustScore:
    """
    Adjust raw confidence through penalties and bonuses.

    Penalties (applied first, multiplicative):
      - Stale signal (>24h old):     ×0.85
      - No provenance URL:           ×0.90
      - Single source, no corroboration: ×0.90

    Bonuses (applied second, additive, capped at +0.15):
      - 2+ corroborating sources:    +0.05 per source (max +0.10)
      - Provenance is .gov / .int:   +0.05
    """
    score = signal.raw_confidence
    penalties = []
    bonuses = []

    # ── Penalties (multiplicative) ────────────────────────────────
    age_hours = (datetime.now(timezone.utc) - signal.timestamp).total_seconds() / 3600

    if age_hours > 24:
        score *= 0.85
        penalties.append(f"stale ({age_hours:.0f}h old)")

    if not signal.provenance:
        score *= 0.90
        penalties.append("no provenance")

    if signal.corroborating_sources == 0:
        score *= 0.90
        penalties.append("uncorroborated")

    # ── Bonuses (additive, capped) ────────────────────────────────
    bonus_total = 0.0

    if signal.corroborating_sources >= 2:
        b = min(signal.corroborating_sources * 0.05, 0.10)
        bonus_total += b
        bonuses.append(f"+{b:.2f} corroboration ({signal.corroborating_sources} sources)")

    if any(d in signal.provenance for d in [".gov", ".int", ".who.", "reliefweb"]):
        bonus_total += 0.05
        bonuses.append("+0.05 institutional provenance")

    score += min(bonus_total, 0.15)
    score = round(min(max(score, 0.0), 1.0), 4)

    return TrustScore(
        signal_id=signal.id,
        element=signal.element,
        raw=signal.raw_confidence,
        adjusted=score,
        passed=score >= signal.element.floor,
        penalties=penalties,
        bonuses=bonuses,
    )


# ── The Gate ──────────────────────────────────────────────────────

@dataclass
class GateVerdict:
    """The Truth Gate's final judgment on a batch of signals."""
    timestamp: datetime
    total_signals: int
    passed_signals: int
    rejected_signals: int
    fire_active: bool              # at least one Fire signal passed
    gate_open: bool                # Fire active = gate open
    element_summary: Dict[str, dict]
    scores: List[TrustScore]
    verdict: str                   # human-readable summary

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "total": self.total_signals,
            "passed": self.passed_signals,
            "rejected": self.rejected_signals,
            "fire_active": self.fire_active,
            "gate_open": self.gate_open,
            "elements": self.element_summary,
            "scores": [
                {
                    "id": s.signal_id,
                    "element": s.element.sigil,
                    "raw": s.raw,
                    "adjusted": s.adjusted,
                    "floor": s.element.floor,
                    "margin": s.margin,
                    "passed": s.passed,
                    "penalties": s.penalties,
                    "bonuses": s.bonuses,
                }
                for s in self.scores
            ],
            "verdict": self.verdict,
        }


class TruthGate:
    """
    The sovereign verification engine.

    Receives signals. Classifies by element. Computes trust.
    Opens only if Fire flows.

    Usage:
        gate = TruthGate()
        verdict = gate.evaluate(signals)
        if verdict.gate_open:
            # proceed to corridor synthesis
        else:
            # hold — not enough verified disease intelligence
    """

    def evaluate(self, signals: List[Signal]) -> GateVerdict:
        """Run all signals through the four elemental floors."""
        scores = [compute_trust(s) for s in signals]

        passed = [s for s in scores if s.passed]
        rejected = [s for s in scores if not s.passed]

        # Fire check — the master gate
        fire_passed = [s for s in passed if s.element == Element.FIRE]
        fire_active = len(fire_passed) > 0

        # Element summary
        summary = {}
        for elem in Element:
            elem_scores = [s for s in scores if s.element == elem]
            elem_passed = [s for s in elem_scores if s.passed]
            summary[elem.sigil] = {
                "name": elem.ibibio,
                "domain": elem.domain,
                "floor": elem.floor,
                "total": len(elem_scores),
                "passed": len(elem_passed),
                "rejected": len(elem_scores) - len(elem_passed),
            }

        # Verdict
        if not fire_active:
            verdict = (
                "GATE CLOSED — 🜂 Ikang (Fire) has no verified signals above floor. "
                "The engine does not activate without disease intelligence. Hold."
            )
        elif len(passed) == len(scores):
            verdict = (
                f"GATE OPEN — All {len(scores)} signals verified. "
                f"🜂 Ikang flows. Proceed to corridor synthesis."
            )
        else:
            verdict = (
                f"GATE OPEN (partial) — {len(passed)}/{len(scores)} signals verified. "
                f"🜂 Ikang flows ({len(fire_passed)} disease signals). "
                f"{len(rejected)} signals below floor — check penalties."
            )

        return GateVerdict(
            timestamp=datetime.now(timezone.utc),
            total_signals=len(scores),
            passed_signals=len(passed),
            rejected_signals=len(rejected),
            fire_active=fire_active,
            gate_open=fire_active,
            element_summary=summary,
            scores=scores,
            verdict=verdict,
        )


# ── MoScript Registration ────────────────────────────────────────

TRUTH_GATE_MOSCRIPT = {
    "id": "mo-gate-truth-001",
    "name": "Truth Gate",
    "trigger": "signal_batch_received",
    "inputs": ["signals: List[Signal]"],
    "logic": "TruthGate().evaluate(signals)",
    "voiceLine": "Nothing enters unverified. Nothing leaves unjudged.",
    "sass": "You thought you could sneak past the elements? Ikang sees you. Isong remembers you.",
}


# ── CLI test ──────────────────────────────────────────────────────

if __name__ == "__main__":
    # Quick smoke test
    test_signals = [
        Signal(
            id="sig-001",
            source="afro_sentinel",
            element=Element.FIRE,
            raw_confidence=0.82,
            timestamp=datetime.now(timezone.utc),
            payload={"disease": "cholera", "location": "Busia border"},
            provenance="https://sentinel.who.int/api/signals/12345",
            corroborating_sources=2,
        ),
        Signal(
            id="sig-002",
            source="iom_dtm",
            element=Element.WATER,
            raw_confidence=0.68,
            timestamp=datetime.now(timezone.utc),
            payload={"flow": "southbound", "count": 340},
            provenance="https://dtm.iom.int/reports/ea-2026-q1",
            corroborating_sources=1,
        ),
        Signal(
            id="sig-003",
            source="acled",
            element=Element.AIR,
            raw_confidence=0.71,
            timestamp=datetime.now(timezone.utc),
            payload={"event_type": "armed_clash", "fatalities": 3},
            provenance="",
            corroborating_sources=0,
        ),
        Signal(
            id="sig-004",
            source="terrain_analysis",
            element=Element.EARTH,
            raw_confidence=0.88,
            timestamp=datetime.now(timezone.utc),
            payload={"crossing_feasibility": 0.91, "language_shift": 0.34},
            provenance="https://reliefweb.int/report/kenya-uganda-corridor",
            corroborating_sources=3,
        ),
    ]

    gate = TruthGate()
    verdict = gate.evaluate(test_signals)

    print(json.dumps(verdict.to_dict(), indent=2))
    print(f"\n{verdict.verdict}")
