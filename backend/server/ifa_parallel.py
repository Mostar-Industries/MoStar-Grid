from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import time, random

def _normalize(vec: List[float]) -> List[float]:
    s = sum(x for x in vec if x > 0.0)
    if s <= 0.0:
        n = len(vec)
        return [1.0/n]*n
    return [max(0.0,x)/s for x in vec]

@dataclass
class IfaResult:
    pattern: int
    confidence: float
    posterior: List[float]
    alternates: List[int]
    elapsed_ms: float
    meta: Dict[str,Any]

class IfaParallel:
    def __init__(self, patterns: int=8, contexts: int=8, seed: int=108):
        assert patterns>1 and contexts>1
        self.P, self.C = patterns, contexts
        self.rng = random.Random(seed)
        raw = [[self.rng.random()+1e-6 for _ in range(self.P)] for __ in range(self.C)]
        for i in range(self.P):
            col_sum = sum(raw[j][i] for j in range(self.C))
            for j in range(self.C):
                raw[j][i] = raw[j][i]/col_sum
        self.likelihood = raw  # C x P
        self.prior = [1.0/self.P]*self.P

    def resolve(self, evidence: List[float], prior: Optional[List[float]]=None, top_k: int=5) -> IfaResult:
        if len(evidence)!=self.C: raise ValueError("evidence length mismatch")
        ev = _normalize(evidence)
        pr = _normalize(prior) if prior is not None else self.prior
        t0 = time.perf_counter()
        score = [0.0]*self.P
        for i in range(self.P):
            s = 0.0
            for j in range(self.C):
                s += self.likelihood[j][i]*ev[j]
            score[i] = pr[i]*s
        s = sum(score) or 1.0
        post = [x/s for x in score]
        best = max(range(self.P), key=lambda i: post[i])
        order = sorted(range(self.P), key=lambda i: post[i], reverse=True)
        alts = [i for i in order if i!=best][:max(0, top_k)]
        return IfaResult(pattern=best, confidence=post[best], posterior=post, alternates=alts, elapsed_ms=(time.perf_counter()-t0)*1000.0, meta={"P":self.P,"C":self.C})
