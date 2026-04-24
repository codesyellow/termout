import json
from pathlib import Path


class HistoryManager:
    CONFIG_PATH = Path.home() / ".config" / "termout" / "history.json"

    @classmethod
    def _ensure_path(cls):
        cls.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def load(cls) -> dict:
        if not cls.CONFIG_PATH.exists():
            return {}
        with open(cls.CONFIG_PATH, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    @classmethod
    def save(cls, data: dict) -> None:
        cls._ensure_path()
        with open(cls.CONFIG_PATH, "w") as f:
            json.dump(data, f, indent=4)
