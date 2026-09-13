import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AuditLog:
    """Journal append-only lisible par un humain et exploitable par un outil."""

    def __init__(self, path: str | Path = "aibi-audit.jsonl") -> None:
        self.path = Path(path)

    def record(self, event: str, **details: Any) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **details,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
