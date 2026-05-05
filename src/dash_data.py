import json
from pathlib import Path

import pandas as pd


def list_sessions(sessions_dir: str) -> list[str]:
    return sorted(
        [p.name for p in Path(sessions_dir).iterdir() if p.is_dir()],
        reverse=True,
    )


def load_session(sessions_dir: str, name: str) -> tuple[pd.DataFrame, dict]:
    base = Path(sessions_dir) / name
    df = pd.read_parquet(base / "telemetry.parquet")
    df["t"] = df["timestamp"] - df["timestamp"].iloc[0]
    info = json.loads((base / "session_info.json").read_text())
    return df, info
