from __future__ import annotations
import json, os, threading
from typing import Any, Dict, Optional, List, Tuple
from .settings import settings

pool = None
_use_file = False
_data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(_data_dir, exist_ok=True)
_actors_file = os.path.join(_data_dir, "actors.json")
_trust_file  = os.path.join(_data_dir, "trust_marks.json")
_lock = threading.Lock()

try:
    import psycopg
    if settings.DATABASE_URL:
        pool = psycopg.Connection.connect(settings.DATABASE_URL)
    else:
        _use_file = True
except Exception:
    _use_file = True
    pool = None

def ensure_schema() -> None:
    if _use_file or pool is None:
        for path in (_actors_file, _trust_file):
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f: json.dump([], f)
        return
    with pool.cursor() as cur:
        cur.execute("""
        create table if not exists actors (
          id bigserial primary key,
          name text unique not null,
          public_key text not null,
          capabilities jsonb not null,
          commitments jsonb not null,
          policy_hash text not null,
          model_fingerprint text not null,
          created_at timestamptz default now()
        );
        create table if not exists trust_marks (
          id bigserial primary key,
          actor_name text not null,
          tier text not null,
          resonance numeric not null,
          oath_ok boolean not null,
          created_at timestamptz default now()
        );
        """)
        pool.commit()

def upsert_actor(a: Dict[str, Any]) -> Tuple[int, str]:
    if _use_file or pool is None:
        with _lock:
            data = []
            if os.path.exists(_actors_file):
                data = json.load(open(_actors_file, "r", encoding="utf-8"))
            # replace or append
            data = [x for x in data if x.get("name") != a["name"]]
            data.append(a)
            json.dump(data, open(_actors_file, "w", encoding="utf-8"), indent=2)
        return (len(data), "file")
    with pool.cursor() as cur:
        cur.execute("""
        insert into actors(name, public_key, capabilities, commitments, policy_hash, model_fingerprint)
        values (%s,%s,%s::jsonb,%s::jsonb,%s,%s)
        on conflict (name) do update set
          public_key=excluded.public_key,
          capabilities=excluded.capabilities,
          commitments=excluded.commitments,
          policy_hash=excluded.policy_hash,
          model_fingerprint=excluded.model_fingerprint
        returning id, now()::text
        """, (a["name"], a["public_key"], json.dumps(a["capabilities"]), json.dumps(a["commitments"]), a["policy_hash"], a["model_fingerprint"]))
        row = cur.fetchone()
        pool.commit()
        return (row[0], row[1])

def get_actor(name: str) -> Optional[Dict[str, Any]]:
    if _use_file or pool is None:
        if not os.path.exists(_actors_file): return None
        for x in json.load(open(_actors_file, "r", encoding="utf-8")):
            if x.get("name") == name: return x
        return None
    with pool.cursor() as cur:
        cur.execute("select name, public_key, capabilities, commitments, policy_hash, model_fingerprint from actors where name=%s", (name,))
        r = cur.fetchone()
        if not r: return None
        return {"name": r[0], "public_key": r[1], "capabilities": r[2], "commitments": r[3], "policy_hash": r[4], "model_fingerprint": r[5]}

def add_trust_mark(actor: str, tier: str, resonance: float, oath_ok: bool) -> None:
    if _use_file or pool is None:
        with _lock:
            data = []
            if os.path.exists(_trust_file):
                data = json.load(open(_trust_file, "r", encoding="utf-8"))
            data.append({"actor_name": actor, "tier": tier, "resonance": resonance, "oath_ok": oath_ok})
            json.dump(data, open(_trust_file, "w", encoding="utf-8"), indent=2)
        return
    with pool.cursor() as cur:
        cur.execute("insert into trust_marks(actor_name, tier, resonance, oath_ok) values (%s,%s,%s,%s)", (actor, tier, resonance, oath_ok))
        pool.commit()

def last_trust(actor: str) -> Optional[Tuple[str, float]]:
    if _use_file or pool is None:
        if not os.path.exists(_trust_file): return None
        data = [x for x in json.load(open(_trust_file, "r", encoding="utf-8")) if x.get("actor_name")==actor]
        if not data: return None
        t = data[-1]
        return (t["tier"], float(t["resonance"]))
    with pool.cursor() as cur:
        cur.execute("select tier, resonance from trust_marks where actor_name=%s order by created_at desc limit 1", (actor,))
        r = cur.fetchone()
        return (r[0], float(r[1])) if r else None

def trust_counts() -> Dict[str,int]:
    if _use_file or pool is None:
        if not os.path.exists(_trust_file): return {"allied":0,"vassal":0,"subjugated":0,"exiled":0}
        data = json.load(open(_trust_file, "r", encoding="utf-8"))
        from collections import Counter
        c = Counter([x.get("tier","exiled") for x in data])
        return {"allied": c.get("allied",0), "vassal": c.get("vassal",0), "subjugated": c.get("subjugated",0), "exiled": c.get("exiled",0)}
    with pool.cursor() as cur:
        res = {}
        for t in ("allied","vassal","subjugated","exiled"):
            cur.execute("select count(*) from trust_marks where tier=%s", (t,))
            res[t] = int(cur.fetchone()[0])
        return res
