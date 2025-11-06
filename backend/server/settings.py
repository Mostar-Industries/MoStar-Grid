import os

def _to_bool(v: str | None, default: bool=False) -> bool:
    if v is None: return default
    return v.strip().lower() in ("1","true","yes","y","on")

class Settings:
    MOCK_MODE = _to_bool(os.getenv("MOCK_MODE"), False)
    DATABASE_URL = os.getenv("DATABASE_URL")  # optional
    ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS", "http://localhost:5173")

settings = Settings()
